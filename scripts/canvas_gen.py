"""对 project.json 里的 job 发起画布生成，每个候选一个节点（gen_X、gen_X_v2 …）。
用法: python3 -I canvas_gen.py <项目目录> JOB [JOB ...] [--n N] [--force]
- 视频 job 提交前检查配乐判断（project.json 的 music 字段，见 SKILL.md），不合规拒绝提交；--force 跳过。
- 已提交的任务记在 state.json，重跑只续查，不重复扣费；被拒/中断的请求可能已在服务端执行，先看节点上有没有 taskId。
- 失败（超时等）的候选不在原节点重提（会拿回旧任务号），而是新建下一个编号的候选节点。
- 完成后下载：图片到 参考图/，视频到 视频/；节点卡在 running 不挂素材时，按任务结果 attach_asset 补挂。
- Seedance 2.5 并发上限 4，排队用 ≤3：视频一次最多提交 3 个候选。默认候选数：图片 1 个、视频 2 个（陈尚宇 2026-10-23 定）；首帧要 2 个时加 --n 2，--n 对本次所有 job 生效。
"""
import json, os, sys, time, urllib.error, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chj import Canvas, call, edge, result_media  # noqa: E402
from canvas_setup import load_project, music_problems, save_state  # noqa: E402


def main():
    args = sys.argv[1:]
    d = args.pop(0)
    n_arg = None
    if "--n" in args:
        i = args.index("--n"); n_arg = int(args[i + 1]); del args[i:i + 2]
    force = "--force" in args
    jobs = [a for a in args if a != "--force"]
    proj, st = load_project(d)
    probs = music_problems(proj, jobs)
    if probs and not force:
        print("配乐检查没通过，未提交（确认无误可加 --force）：")
        for p_ in probs:
            print("  -", p_)
        sys.exit(1)
    tasks = st.setdefault("tasks", {}); failed = st.setdefault("failed", {})
    cv = Canvas(proj["canvas_id"])

    def cands(j, payload):
        base = [f"gen_{j}"] + [f"gen_{j}_v{k}" for k in range(2, 30)]
        alive = [c for c in base if c not in failed]
        n = n_arg or (2 if proj["jobs"][j]["kind"] == "video" else 1)
        return alive[:n]

    # 1. 补建候选节点（复制主节点草稿和连线，连线顺序不变）
    def ops_dup(payload):
        ids = {x["id"]: x for x in payload["nodes"]}
        ops = []
        for j in jobs:
            src = ids["gen_" + j]
            for c in cands(j, payload):
                if c in ids:
                    continue
                k = c.rsplit("_v", 1)[1] if "_v" in c else "1"
                dd = json.loads(json.dumps(src["data"]))
                for key in ("generation", "asset"):
                    dd.pop(key, None)
                dd["label"] = proj["jobs"][j]["label"] + f" v{k}"
                ops.append({"type": "add_node", "node": {"id": c, "type": src["type"],
                            "position": {"x": src["position"]["x"] + 450 * (int(k) - 1), "y": src["position"]["y"]}, "data": dd}})
                for e in payload["edges"]:
                    if e["target"] == src["id"]:
                        ops.append(edge(e["source"], c, f"{e['id']}__{c}"))
        return ops

    cv.apply(ops_dup, lambda pl: all(c in {x["id"] for x in pl["nodes"]} for j in jobs for c in cands(j, pl)))

    # 2. 逐个提交
    _, p = cv.load()
    for j in jobs:
        for c in cands(j, p):
            if c in tasks:
                continue
            for attempt in range(4):
                rev, pl = cv.load()
                g = next((x["data"].get("generation") or {} for x in pl["nodes"] if x["id"] == c), {})
                if g.get("taskId") and g.get("status") not in ("failed", "submit_failed"):
                    tasks[c] = g["taskId"]; print(c, "claimed existing task", g["taskId"]); break
                try:
                    r = call("POST", "/open/v1/canvas/generate", {"canvas_id": cv.id, "target_node_id": c, "expected_revision": rev})
                except urllib.error.HTTPError as e:
                    if e.code == 409:
                        time.sleep(8); continue
                    raise
                br = r["data"]["base_resp"]
                if br["code"] != 0:
                    print(c, "submit failed", br); break
                pp = r["data"]["document"]["payload"]
                pp = pp if isinstance(pp, dict) else json.loads(pp)
                tasks[c] = next(x for x in pp["nodes"] if x["id"] == c)["data"]["generation"]["taskId"]
                print(c, "submitted", tasks[c], flush=True)
                break
            save_state(d, st)
            time.sleep(7)

    # 3. 轮询 + 下载
    want = [c for j in jobs for c in cands(j, p) if c in tasks]
    def out_path(c):
        kind = proj["jobs"][c[4:].split("_v")[0]]["kind"]
        sub = "视频" if kind == "video" else "参考图"
        os.makedirs(os.path.join(d, sub), exist_ok=True)
        return os.path.join(d, sub, c + (".mp4" if kind == "video" else ".png"))
    pending = [c for c in want if not os.path.exists(out_path(c))]
    t0 = time.time()
    while pending and time.time() - t0 < 3600:
        det = cv.task_details([tasks[c] for c in pending])
        for c in list(pending):
            it = det.get(tasks[c], {}); s = it.get("status")
            if s in ("completed", "success"):
                urllib.request.urlretrieve(result_media(it)["url"], out_path(c)); print(c, "done", flush=True); pending.remove(c)
            elif s in ("failed", "refunded", "cancelled"):
                print(c, s, (it.get("err_zh") or it.get("error") or "")[:120]); failed[c] = tasks.pop(c); pending.remove(c); save_state(d, st)
        if pending:
            time.sleep(15)
    if pending:
        print("still running:", pending)

    # 4. 补挂卡在 running 的素材，读回核对
    _, pl = cv.load()
    stuck = [x["id"] for x in pl["nodes"] if x["id"] in want and x["id"] in tasks and not x["data"].get("asset")]
    if stuck:
        det = cv.task_details([tasks[c] for c in stuck])
        media = {c: result_media(det[tasks[c]]) for c in stuck if det.get(tasks[c], {}).get("status") in ("completed", "success")}
        def ops_attach(payload):
            ops = []
            for c, m in media.items():
                kind = proj["jobs"][c[4:].split("_v")[0]]["kind"]
                ops.append({"type": "attach_asset", "node_id": c, "asset": {"mediaType": kind, "origin": "generation",
                            "source": {"kind": "task", "sourceTaskId": tasks[c], "osBucket": m["os_bucket"], "osKey": m["os_key"]}}})
            return ops
        cv.apply(ops_attach, lambda pl2: all(x["data"].get("asset") for x in pl2["nodes"] if x["id"] in media))
        print("attached stuck assets:", list(media))
    if failed and any(c[4:].split("_v")[0] in jobs for c in failed):
        print("有失败候选，重跑本命令会自动新建下一个编号补齐", [c for c in failed if c[4:].split("_v")[0] in jobs])


if __name__ == "__main__":
    main()
