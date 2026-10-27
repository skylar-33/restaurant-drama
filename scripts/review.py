"""审片：时长/音轨、2fps 联系表、逐词转写；--brand 时把品牌词那一小段音频单独切出来再转写（排除上下文影响）。
用法: python3 review.py [--brand 品牌词片段] 视频1.mp4 [视频2.mp4 ...]
输出到 视频所在目录/审片/<名>_sheet.jpg、<名>_asr.txt，并打印摘要。
转写用 faster-whisper（small.en）。首次运行会在 ~/.cache/restaurant-drama/asr 建虚拟环境并安装。
注意：转写模型不认识品牌词，带上下文时会往常见词上猜（如 ".com" 前面会猜成 restaurant），
所以判断念法以「单独切出来」的结果为准；最终仍要人耳确认。
"""
import json, os, subprocess, sys

VENV = os.path.expanduser("~/.cache/restaurant-drama/asr")
FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

try:
    from faster_whisper import WhisperModel
except ImportError:
    py = os.path.join(VENV, "bin", "python")
    if not os.path.exists(py):
        subprocess.run(["python3.11" if subprocess.run(["which", "python3.11"], capture_output=True).returncode == 0 else "python3",
                        "-m", "venv", VENV], check=True)
        subprocess.run([py, "-m", "pip", "install", "-q", "faster-whisper"], check=True)
    os.execv(py, [py] + sys.argv)


def main():
    args = sys.argv[1:]
    brand = None
    if "--brand" in args:
        i = args.index("--brand"); brand = args[i + 1].lower(); del args[i:i + 2]
    model = WhisperModel("small.en", device="cpu", compute_type="int8")
    for path in args:
        name = os.path.splitext(os.path.basename(path))[0]
        out = os.path.join(os.path.dirname(os.path.abspath(path)), "审片")
        os.makedirs(out, exist_ok=True)
        info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height",
                                          "-of", "json", path], capture_output=True, text=True).stdout)
        dur = float(info["format"]["duration"])
        v = next(s for s in info["streams"] if s["codec_type"] == "video")
        rows = (int(dur * 2) + 1 + 5) // 6
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", path, "-vf",
            f"fps=2,scale=270:-1,drawtext=fontfile={FONT}:text='%{{pts\\:hms}}':x=6:y=6:fontsize=20:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=6x{rows}",
            "-frames:v", "1", os.path.join(out, name + "_sheet.jpg")], check=True)
        segs, _ = model.transcribe(path, word_timestamps=True, language="en")
        words = [w for s in segs for w in (s.words or [])]
        lines = [f"{name}: {dur:.2f}s {v['width']}x{v['height']} audio={'audio' in [s['codec_type'] for s in info['streams']]}",
                 "  " + " ".join(f"{w.word.strip()}[{w.start:.1f}]" for w in words)]
        if brand:
            hits = [k for k, w in enumerate(words) if brand in w.word.lower().replace(" ", "")]
            for k in hits:
                st = words[k].start
                en = words[k + 1].start if k + 1 < len(words) and words[k + 1].start - st > 0.3 else words[k].end + 0.25
                if words[k + 1:k + 2] and words[k + 1].word.strip().startswith(("-", ".")) and k + 2 < len(words):
                    en = words[k + 2].start  # 品牌词被拆成 nature + -stront 时一起切
                wav = os.path.join(out, f"{name}_brand_{st:.1f}.wav")
                subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{max(0, st - 0.05):.2f}", "-to", f"{en:.2f}",
                                "-i", path, "-vn", "-ac", "1", "-ar", "16000", wav], check=True)
                s2, _ = model.transcribe(wav, language="en", condition_on_previous_text=False)
                lines.append(f"  品牌词 {st:.2f}-{en:.2f}s 单独转写: {' '.join(x.text.strip() for x in s2)}")
            if not hits:
                lines.append(f"  没转写到含 '{brand}' 的词（可能念得很偏，或句子里没有）")
        txt = "\n".join(lines)
        open(os.path.join(out, name + "_asr.txt"), "w", encoding="utf-8").write(txt)
        print(txt, "\n")


if __name__ == "__main__":
    main()
