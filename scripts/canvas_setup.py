"""按 project.json 搭画布：没有画布就新建；上传参考素材成节点；为每个 job 建待生成节点并按 refs 顺序连线。
用法: python3 -I canvas_setup.py <项目目录> [--sync-prompts]
- 只建缺的节点，已存在的不动；--sync-prompts 把 project.json 里改过的提示词同步到画布节点草稿。
- refs 里的「图片 N」= 连线顺序：先连的是图片1。视频节点作参考时算「视频1」。
- 写完读回核对（画布网页开着会覆盖 API 写入）。
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chj import Canvas, edge, media_size, upload  # noqa: E402


def load_project(d):
    p = json.load(open(os.path.join(d, "project.json"), encoding="utf-8"))
    sp = os.path.join(d, "state.json")
    st = json.load(open(sp, encoding="utf-8")) if os.path.exists(sp) else {}
    return p, st


def save_state(d, st):
    json.dump(st, open(os.path.join(d, "state.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)


MUSIC = ("start", "continue", "turn", "none")


def music_problems(proj, names=None):
    """检查视频 job 的配乐判断：continue 必须挂上一段视频，turn 不能挂视频，必须先标 music。返回问题列表。"""
    jobs = proj.get("jobs", {})
    video_nodes = {"gen_" + n for n, j in jobs.items() if j["kind"] == "video"}
    def is_video(ref):
        base = ref.split("_v")[0] if ref.startswith("gen_") else ref
        return ref in video_nodes or base in video_nodes or proj.get("refs", {}).get(ref, {}).get("file", "").endswith(".mp4")
    out = []
    for n, j in jobs.items():
        if j["kind"] != "video" or (names and n not in names):
            continue
        m = j.get("music")
        vids = [r for r in j.get("refs", []) if is_video(r)]
        if m not in MUSIC:
            out.append(f"{n}: 没标 music（start / continue / turn / none），先判断这段和上一段是延续还是转折")
        elif m == "continue" and not vids:
            out.append(f"{n}: 标了 continue，但没挂上一段视频作视频1，音乐接不上")
        elif m == "turn" and vids:
            out.append(f"{n}: 标了 turn，却挂了视频 {vids}，参考视频的音乐会盖过提示词（P04 C 段的错），去掉视频参考、只挂尾帧图片")
        elif m == "turn" and "不要" not in j.get("prompt", ""):
            out.append(f"{n}: 标了 turn，提示词里没列出不要的上一段乐器/音效")
    return out


def draft(job):
    if job["kind"] == "image":
        return {"kind": "image", "model": "gpt_image_2", "imageSize": job.get("size", "4K"), "ratio": job["ratio"], "prompt": job["prompt"]}
    return {"kind": "video", "model": job.get("model", "sd25_official"), "inputMode": "reference", "aspectRatio": job.get("ratio", "9:16"),
            "duration": job["duration"], "resolution": job.get("resolution", "1080p"), "generateAudio": True,
            "language": "en", "candidateCount": 1, "prompt": job["prompt"]}


def main():
    d = sys.argv[1]
    sync = "--sync-prompts" in sys.argv
    proj, st = load_project(d)
    if not proj.get("canvas_id"):
        proj["canvas_id"] = Canvas.create("NRT · " + proj["name"])
        json.dump(proj, open(os.path.join(d, "project.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print("created canvas", proj["canvas_id"])
    cv = Canvas(proj["canvas_id"])
    _, p = cv.load()
    have = {n["id"] for n in p["nodes"]}

    # 1. 参考素材：先上传缺的（上传要在 apply 外做，避免重试时重复上传）
    uploads = {}
    for i, (rid, ref) in enumerate(proj.get("refs", {}).items()):
        if rid not in have:
            path = os.path.join(d, ref["file"])
            b, k, _ = upload(path)
            w, h, dur = media_size(path)
            uploads[rid] = (b, k, w, h, dur, i)

    jobs = proj.get("jobs", {})

    def ops_for(payload):
        ids = {n["id"]: n for n in payload["nodes"]}
        eids = {e["id"] for e in payload["edges"]}
        ops = []
        for rid, (b, k, w, h, dur, i) in uploads.items():
            if rid in ids:
                continue
            mt = "video" if dur else "image"
            data = {"type": mt, "label": proj["refs"][rid]["label"], "width": w, "height": h}
            asset = {"mediaType": mt, "origin": "upload", "width": w, "height": h, "source": {"kind": "oss", "osBucket": b, "osKey": k}}
            if dur:
                data["duration"] = asset["duration"] = round(dur, 2)
            ops += [{"type": "add_node", "node": {"id": rid, "type": mt, "position": {"x": 0, "y": i * 700}, "data": data}},
                    {"type": "attach_asset", "node_id": rid, "asset": asset}]
        for j, (name, job) in enumerate(jobs.items()):
            nid = "gen_" + name
            if nid not in ids:
                ops.append({"type": "add_node", "node": {"id": nid, "type": job["kind"],
                            "position": {"x": 800 + 450 * (j % 8), "y": 900 * (j // 8)},
                            "data": {"type": job["kind"], "label": job["label"], "generationDraft": draft(job)}}})
            elif sync and (ids[nid]["data"].get("generationDraft") or {}).get("prompt") != job["prompt"]:
                ops.append({"type": "update_node", "node_id": nid, "patch": {"data": {"generationDraft": {"prompt": job["prompt"]}}}})
            for k, r in enumerate(job.get("refs", []), 1):
                eid = f"e{k}_{r}_{nid}"
                if eid not in eids and not any(e["source"] == r and e["target"] == nid for e in payload["edges"]):
                    ops.append(edge(r, nid, eid))
        return ops

    def check(payload):
        ids = {n["id"] for n in payload["nodes"]}
        return all(r in ids for r in proj.get("refs", {})) and all("gen_" + j in ids for j in jobs)

    cv.apply(ops_for, check)
    # 核对图片编号
    _, p = cv.load()
    lab = {n["id"]: n["data"].get("label", "") for n in p["nodes"]}
    for name, job in jobs.items():
        nid = "gen_" + name
        srcs = [e["source"] for e in p["edges"] if e["target"] == nid]
        want = job.get("refs", [])
        flag = "" if srcs[:len(want)] == want else "  ⚠️ 连线顺序和 refs 不一致，提示词里的图片编号会错位"
        print(f"{nid}: " + "、".join(f"{i}={lab.get(s, s)[:14]}" for i, s in enumerate(srcs, 1)) + flag)
    for prob in music_problems(proj):
        print("  ⚠️ 配乐", prob)
    print(cv.url())


if __name__ == "__main__":
    main()
