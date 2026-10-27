"""按时间线 JSON 拼粗剪：统一 1080x1920 / 30fps / 48kHz 立体声，concat 后响度标准化。
用法: python3 -I assemble.py <timeline.json>
timeline.json 里路径相对于该文件所在目录。段落类型：
  {"type":"clip","src":"视频/a.mp4","start":0,"end":8.8,"black_head":0.3}   片段（可截取；black_head=开头盖黑但保留声音）
  {"type":"black","dur":1}                                                 纯黑静音
  {"type":"rewind","src":"视频/a.mp4","end":8.6,"dur":0.6}                 倒带：src 的 0–end 倒放压到 dur 秒，加噪点和倒带声
  {"type":"title","text":"Take two.","dur":0.4}                            黑底白字标题卡
  {"type":"endcard","dur":0.5,"bg":"0x00913A","logo":"参考素材/logo_white.png"}
     尾板最好不用；要留只闪一下，不写网址/按钮（见 prompt-rules.md 第四节）。lines、button 字段仍支持
顶层: {"output":"视频/xxx.mp4","loudness":-14,"segments":[...]}
"""
import json, os, subprocess, sys, tempfile

FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
V = "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps=30,format=yuv420p,setsar=1"
A = "aresample=48000,aformat=channel_layouts=stereo"
SILENT = ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
ENC = ["-c:v", "libx264", "-crf", "18", "-c:a", "aac"]


def run(a):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"] + a, check=True)


def esc(t):
    return t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’").replace("%", "\\%")


def render(seg, base, out):
    t = seg["type"]
    if t == "clip":
        cut = (["-ss", str(seg["start"])] if seg.get("start") else []) + (["-to", str(seg["end"])] if seg.get("end") else [])
        vf = V + (f",drawbox=x=0:y=0:w=iw:h=ih:color=black:t=fill:enable='lt(t,{seg['black_head']})'" if seg.get("black_head") else "")
        run(cut + ["-i", os.path.join(base, seg["src"]), "-vf", vf, "-af", A] + ENC + [out])
    elif t == "black":
        run(["-f", "lavfi", "-i", f"color=black:s=1080x1920:r=30:d={seg['dur']}"] + SILENT + ["-t", str(seg["dur"]), "-vf", "format=yuv420p,setsar=1"] + ENC + [out])
    elif t == "title":
        run(["-f", "lavfi", "-i", f"color=black:s=1080x1920:r=30:d={seg['dur']}"] + SILENT + ["-t", str(seg["dur"]), "-vf",
            f"drawtext=fontfile='{FONT}':text='{esc(seg['text'])}':fontsize={seg.get('size', 110)}:fontcolor=white:x=(w-tw)/2:y=(h-th)/2,format=yuv420p,setsar=1"] + ENC + [out])
    elif t == "rewind":
        k = seg["end"] / seg["dur"]
        run(["-t", str(seg["end"]), "-i", os.path.join(base, seg["src"]), "-filter_complex",
             f"[0:v]{V},reverse,setpts=PTS/{k:.3f},noise=alls=45:allf=t,eq=saturation=0.5[v];"
             f"[0:a]{A},areverse,asetrate=48000*{min(k, 12):.2f},aresample=48000,atrim=0:{seg['dur']},volume=0.6[a]",
             "-map", "[v]", "-map", "[a]", "-t", str(seg["dur"])] + ENC + [out])
    elif t == "endcard":
        d = seg["dur"]
        f = f"[1]scale=860:-1[l];[0][l]overlay=(W-w)/2:(H-h)/2-80"
        for ln in seg.get("lines", []):
            f += f",drawtext=fontfile='{FONT}':text='{esc(ln['text'])}':fontsize={ln.get('size', 48)}:fontcolor={ln.get('color', 'white')}:x=(w-tw)/2:y=h/2+({ln.get('y', 90)})"
        if seg.get("button"):
            f += (f",drawbox=x=170:y=ih/2+70:w=740:h=130:color=white:t=fill"
                  f",drawtext=fontfile='{FONT}':text='{esc(seg['button']['text'])}':fontsize=54:fontcolor={seg.get('bg', '0x00913A')}:x=(w-tw)/2:y=h/2+70+(130-th)/2")
        f += ",format=yuv420p,setsar=1[v]"
        run(["-f", "lavfi", "-i", f"color={seg.get('bg', '0x00913A')}:s=1080x1920:r=30:d={d}", "-i", os.path.join(base, seg["logo"])] + SILENT +
            ["-filter_complex", f, "-map", "[v]", "-map", "2:a", "-t", str(d)] + ENC + [out])
    else:
        raise SystemExit("unknown segment type " + t)


def main():
    tl_path = sys.argv[1]
    base = os.path.dirname(os.path.abspath(tl_path))
    tl = json.load(open(tl_path, encoding="utf-8"))
    out = os.path.join(base, tl["output"])
    with tempfile.TemporaryDirectory(prefix="asm_") as tmp:
        parts = []
        for i, seg in enumerate(tl["segments"]):
            p = os.path.join(tmp, f"{i:02d}.mp4"); render(seg, base, p); parts.append(p)
        ins = sum((["-i", x] for x in parts), [])
        fc = "".join(f"[{i}:v][{i}:a]" for i in range(len(parts))) + f"concat=n={len(parts)}:v=1:a=1[v][a0];" \
             f"[a0]loudnorm=I={tl.get('loudness', -14)}:TP=-1.5:LRA=11,aresample=48000[a]"
        run(ins + ["-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "18", "-c:a", "aac", "-b:a", "192k",
                   "-movflags", "+faststart", out])
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out], capture_output=True, text=True).stdout)
    print("saved", out, f"{d:.2f}s")


if __name__ == "__main__":
    main()
