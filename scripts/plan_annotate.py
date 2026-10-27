"""在布局俯视图上标动线、机位和关键点（ImageMagick）。标注图只给人看，不能当生成参考（图上的字会被模型照抄）。
用法: python3 -I plan_annotate.py <项目目录>
读 project.json 的 "plans"：
  "plans": {"参考图/gen_R3P.png": {
     "grid": [900, 1600],                     # 下面坐标所在的预览尺寸，会按原图比例换算
     "routes": [{"label":"女主动线","color":"#ff3b30","points":[[450,1470],[655,705],[450,320]],"dash":false}],
     "markers": [{"at":[655,705],"label":"② 拽门把手（锁着）","color":"#ffd60a","dx":-520,"dy":20}],
     "cameras": [{"at":[560,1180],"dir":"up","label":"机位1a → 朝死胡同","dx":-560,"dy":110}]}}
先用 --grid 出带坐标网格的预览，量好坐标再写进 project.json： python3 -I plan_annotate.py <项目目录> --grid
输出 <原图名>_动线.png（--grid 时输出到 /tmp 风格的 <原图名>_grid.jpg）。
"""
import json, math, os, subprocess, sys

FONT = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
NUMFONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


def size(path):
    out = subprocess.run(["magick", "identify", "-format", "%w %h", path], capture_output=True, text=True).stdout.split()
    return int(out[0]), int(out[1])


def grid(path, gw, gh):
    lines = " ".join(f"line {x},0 {x},{gh}" for x in range(0, gw + 1, 100)) + " " + " ".join(f"line 0,{y} {gw},{y}" for y in range(0, gh + 1, 100))
    labels = " ".join(f"text 5,{y - 5} '{y}'" for y in range(100, gh, 100)) + " " + " ".join(f"text {x + 3},20 '{x}'" for x in range(100, gw, 100))
    out = os.path.splitext(path)[0] + "_grid.jpg"
    subprocess.run(["magick", path, "-resize", f"{gw}x{gh}!", "-fill", "none", "-stroke", "yellow", "-strokewidth", "1", "-draw", lines,
                    "-font", NUMFONT, "-fill", "yellow", "-stroke", "none", "-pointsize", "22", "-draw", labels, out], check=True)
    print("grid preview:", out)


def annotate(path, cfg):
    W, H = size(path); gw, gh = cfg.get("grid", [900, 1600]); sx, sy = W / gw, H / gh
    S = lambda p: (p[0] * sx, p[1] * sy)
    sw = max(6, int(W / 135))
    cmd = ["magick", path, "-font", FONT]
    def arrow(a, b, color, size=W / 31):
        (x1, y1), (x2, y2) = S(a), S(b); ang = math.atan2(y2 - y1, x2 - x1)
        pts = [(x2, y2), (x2 - size * math.cos(ang - .45), y2 - size * math.sin(ang - .45)), (x2 - size * math.cos(ang + .45), y2 - size * math.sin(ang + .45))]
        return ["-fill", color, "-stroke", "none", "-draw", "polygon " + " ".join(f"{x:.0f},{y:.0f}" for x, y in pts)]
    def label(p, text, color, dx=0, dy=0, size=None):
        x, y = S(p); ps = str(size or int(W / 47))
        return ["-fill", "#000000b0", "-stroke", "none", "-pointsize", ps, "-annotate", f"+{x + dx + 3:.0f}+{y + dy + 3:.0f}", text,
                "-fill", color, "-annotate", f"+{x + dx:.0f}+{y + dy:.0f}", text]
    legend = []
    for r in cfg.get("routes", []):
        pts = " ".join(f"{x:.0f},{y:.0f}" for x, y in map(S, r["points"]))
        dash = ["-draw", f"stroke-dasharray {sw * 3} {sw * 2} polyline {pts}"] if r.get("dash") else ["-draw", f"polyline {pts}"]
        cmd += ["-fill", "none", "-stroke", r["color"], "-strokewidth", str(sw)] + dash + arrow(r["points"][-2], r["points"][-1], r["color"])
        legend.append((r["label"], r["color"]))
    for m in cfg.get("markers", []):
        x, y = S(m["at"]); rad = W / 40
        cmd += ["-fill", "none", "-stroke", m.get("color", "#ffd60a"), "-strokewidth", str(sw * .6), "-draw", f"circle {x:.0f},{y:.0f} {x + rad:.0f},{y:.0f}"]
        cmd += label(m["at"], m["label"], m.get("color", "#ffd60a"), m.get("dx", 30), m.get("dy", 20))
    for c in cfg.get("cameras", []):
        x, y = S(c["at"]); s = W / 36; up = c.get("dir", "up") == "up"
        tri = [(x, y - s), (x - s * .75, y + s / 2), (x + s * .75, y + s / 2)] if up else [(x, y + s), (x - s * .75, y - s / 2), (x + s * .75, y - s / 2)]
        cmd += ["-fill", "#32d4ff", "-stroke", "#003040", "-strokewidth", "4", "-draw", "polygon " + " ".join(f"{a:.0f},{b:.0f}" for a, b in tri)]
        cmd += label(c["at"], c["label"], "#32d4ff", c.get("dx", 30), c.get("dy", 60), int(W / 54))
    ly = H - 80 - 80 * (len(legend) + 1)
    cmd += ["-fill", "#000000c0", "-stroke", "none", "-draw", f"roundrectangle 40,{ly - 50} {W * .7:.0f},{H - 40} 24,24", "-pointsize", str(int(W / 51))]
    for i, (t, col) in enumerate(legend + [("机位（尖角 = 镜头朝向）", "#32d4ff")]):
        y = ly + i * 80
        cmd += ["-fill", col, "-draw", f"rectangle 80,{y - 16} 200,{y}", "-fill", "white", "-annotate", f"+230+{y + 6}", t]
    out = os.path.splitext(path)[0] + "_动线.png"
    subprocess.run(cmd + [out], check=True)
    print("saved", out)


def main():
    d = sys.argv[1]
    proj = json.load(open(os.path.join(d, "project.json"), encoding="utf-8"))
    for rel, cfg in proj.get("plans", {}).items():
        path = os.path.join(d, rel)
        if "--grid" in sys.argv:
            grid(path, *cfg.get("grid", [900, 1600]))
        else:
            annotate(path, cfg)


if __name__ == "__main__":
    main()
