"""出海匠开放平台 + 画布的共用客户端（餐馆剧情 skill 的所有脚本都用它）。

- 凭据：~/.config/chj-short-drama-video/chj.env 里的 CHJ_OPENAPI_KEY，不打印。
- 网关：https://openapi.gateway.chuhaijiang.com，请求头 X-API-Key；限流 10 次/分钟，连续调用间隔 ≥7 秒。
- 画布坑（2026-10-22 实测）：网页端开着会覆盖 API 写入 → apply 后等 15 秒读回核对；409 = 版本冲突 → 重读再写；
  网络偶发 SSL EOF → 重试。
"""
import json, os, subprocess, time, urllib.error, urllib.request

ENV = os.path.expanduser("~/.config/chj-short-drama-video/chj.env")
BASE = "https://openapi.gateway.chuhaijiang.com"


def _key():
    for line in open(ENV, encoding="utf-8"):
        if line.startswith("CHJ_OPENAPI_KEY="):
            return line.split("=", 1)[1].strip().strip("'\"")
    raise SystemExit("CHJ_OPENAPI_KEY missing in " + ENV)


KEY = _key()


def call(method, path, body=None, tries=4):
    """调用开放平台；网络错误自动重试，HTTP 错误（含 409）原样抛出给调用方处理。"""
    for i in range(tries):
        req = urllib.request.Request(BASE + path, method=method,
            data=json.dumps(body).encode() if body is not None else None,
            headers={"X-API-Key": KEY, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError:
            raise
        except Exception as e:  # SSL EOF、超时等
            if i == tries - 1:
                raise
            print("  network retry:", e)
            time.sleep(5)


def upload(path):
    """上传本地文件，返回 (os_bucket, os_key, signed_url)。PUT 要打到返回的 url，不是 signed_url。"""
    d = call("POST", "/open/v1/upload/presigned-url", {"file_name": ascii_name(path)})["data"]
    ext = os.path.splitext(path)[1].lower()
    ctype = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".mp4": "video/mp4"}.get(ext, "application/octet-stream")
    urllib.request.urlopen(urllib.request.Request(d["url"], method="PUT", data=open(path, "rb").read(),
                                                  headers={"Content-Type": ctype}), timeout=300).read()
    time.sleep(7)
    return d["os_bucket"], d["os_key"], d["signed_url"]


def ascii_name(path):
    base, ext = os.path.splitext(os.path.basename(path))
    safe = "".join(c if c.isascii() and (c.isalnum() or c in "-_") else "_" for c in base).strip("_") or "file"
    return safe + ext


def media_size(path):
    """图片用 sips、视频用 ffprobe 取宽高（和时长）。"""
    if path.lower().endswith(".mp4"):
        out = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
            "stream=width,height:format=duration", "-of", "json", path], capture_output=True, text=True).stdout)
        s = out["streams"][0]
        return s["width"], s["height"], float(out["format"]["duration"])
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", path], capture_output=True, text=True).stdout
    return int(out.split("pixelWidth:")[1].split()[0]), int(out.split("pixelHeight:")[1].split()[0]), None


class Canvas:
    def __init__(self, canvas_id):
        self.id = canvas_id

    @staticmethod
    def create(name):
        r = call("POST", "/open/v1/canvas/create", {"name": name})["data"]
        return r.get("canvas_id") or r["document"]["canvas_id"]

    def url(self):
        return "https://www.chuhaijiang.com/app/create/canvas/" + self.id

    def load(self):
        doc = call("POST", "/open/v1/canvas/load", {"canvas_id": self.id})["data"]["document"]
        p = doc["payload"] if isinstance(doc["payload"], dict) else json.loads(doc["payload"])
        return doc["revision"], p

    def apply(self, build_ops, check=None, tries=4, settle=15):
        """build_ops(payload) -> ops 列表（基于最新画布现算，可返回空）；check(payload) -> bool 读回核对。
        409 时重读重算；写入后等 settle 秒读回，check 不过（被网页覆盖）就重做。"""
        for i in range(tries):
            rev, p = self.load()
            ops = build_ops(p)
            if ops:
                try:
                    r = call("POST", "/open/v1/canvas/apply", {"canvas_id": self.id, "expected_revision": rev, "operations": ops})
                    if r["data"]["base_resp"]["code"] != 0:
                        raise SystemExit(f"apply failed: {r['data']['base_resp']}")
                except urllib.error.HTTPError as e:
                    if e.code == 409:
                        print("  409 conflict, reload"); time.sleep(8); continue
                    raise SystemExit(f"apply HTTP {e.code}: {e.read()[:300]}")
            if check is None:
                return True
            time.sleep(settle if ops else 0)
            _, p = self.load()
            if check(p):
                return True
            print("  readback mismatch (canvas page may have overwritten), retry")
        raise SystemExit("canvas write did not stick after retries")

    def share_snapshot(self):
        """删除前做快照：分享快照可用「克隆画布分享」恢复。"""
        return call("POST", "/open/v1/canvas/share/create", {"canvas_id": self.id})["data"].get("share")

    def task_details(self, task_ids):
        if not task_ids:
            return {}
        r = call("POST", "/open/v1/canvas/tasks/batch-detail", {"task_ids": list(task_ids)})["data"]
        items = r.get("tasks") or r.get("items") or r.get("list") or []
        return {(it.get("task_id") or it.get("id")): it for it in items}


def edge(src, dst, eid=None):
    return {"type": "add_edge", "edge": {"id": eid or f"e_{src}_{dst}", "source": src, "target": dst, "type": "dashed",
            "sourceHandle": "context-source-anchor-right", "targetHandle": "context-target-anchor-left"}}


def result_media(task):
    """batch-detail 的结果：result.data[0] 里有 url / os_bucket / os_key。"""
    res = task.get("result") or {}
    d = res.get("data")
    return d[0] if isinstance(d, list) and d else res
