"""Generate synthetic test videos with known ground truth (macOS `say` + ffmpeg).

  dialog.mp4         3 voices, one coloured scene per line (scene cut at each line start), 0.6 s gaps,
                     a 3 s applause-like noise burst at the end. truth.json lists every line.
  vfr.mkv            same picture at variable frame rate
  delayed_audio.mp4  audio stream starts 1.0 s after the video
  sync.mp4           white flash + 1 kHz beep every 2.0 s (for A/V sync checks after edits)

Usage: python tests/make_fixtures.py OUT_DIR
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
LINES = [
    ("Samantha", "Good morning everyone, and welcome back to the show. Today we are talking about coffee."),
    ("Daniel", "Thanks for having me. I have to admit, I drink about five cups a day."),
    ("Karen", "Five cups? That is honestly a lot. I stopped at two after my doctor gave me a warning."),
    ("Samantha", "So Daniel, what got you into coffee in the first place?"),
    ("Daniel", "My grandfather owned a small roastery in Bristol. I grew up smelling fresh beans every morning."),
    ("Karen", "That sounds wonderful. I grew up with instant coffee and nothing else."),
    ("Samantha", "Let's talk about the science. Does caffeine really improve focus?"),
    ("Daniel", "Yes, in moderate amounts. But the effect fades if you drink it all day."),
    ("Karen", "Exactly. And sleep matters more than any cup of coffee."),
    ("Samantha", "Great point. Thank you both for joining us today."),
]
COLORS = {"Samantha": "0x1f4e9e", "Daniel": "0x2e7d32", "Karen": "0xb23a48"}
GAP = 0.6


def sh(*cmd):
    subprocess.run(cmd, check=True, capture_output=True)


def dur(p: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def make_dialog(out: Path) -> dict:
    tmp = out / "_parts"
    tmp.mkdir(parents=True, exist_ok=True)
    truth, segs, t = [], [], 0.0
    for i, (voice, text) in enumerate(LINES):
        aiff, wav = tmp / f"l{i:02d}.aiff", tmp / f"l{i:02d}.wav"
        sh("say", "-v", voice, "-o", str(aiff), text)
        sh("ffmpeg", "-y", "-loglevel", "error", "-i", str(aiff), "-ar", "48000", "-ac", "2", "-af", f"apad=pad_dur={GAP}", str(wav))
        d = dur(wav)
        seg = tmp / f"s{i:02d}.mp4"
        label = f"{voice} - line {i + 1}"
        fc = (f"[0:v][2:v]overlay=x='mod(t*120,1180)':y=500[b];"
              f"[b]drawtext=fontfile={FONT}:text='{label}':fontcolor=white:fontsize=56:x=60:y=80[v]")
        sh("ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"color=c={COLORS[voice]}:s=1280x720:r=25:d={d}",
           "-i", str(wav), "-f", "lavfi", "-i", "color=c=white:s=100x100:r=25", "-filter_complex", fc,
           "-map", "[v]", "-map", "1:a", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(seg))
        segs.append(seg)
        truth.append({"i": i, "voice": voice, "text": text, "start": round(t, 3), "speech_end": round(t + d - GAP, 3),
                      "end": round(t + d, 3)})
        t += d
    # applause-like ending: pink noise bursts over a grey card
    tail = tmp / "tail.mp4"
    sh("ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=gray:s=1280x720:r=25:d=3",
       "-f", "lavfi", "-i", "anoisesrc=color=pink:amplitude=0.4:d=3,tremolo=f=9:d=0.9,aformat=sample_rates=48000:channel_layouts=stereo",
       "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(tail))
    segs.append(tail)
    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{s}'\n" for s in segs))
    dst = out / "dialog.mp4"
    sh("ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
       "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", str(dst))
    info = {"file": str(dst), "lines": truth, "tail": {"start": round(t, 3), "end": round(t + 3, 3)},
            "speakers": sorted(COLORS), "cuts": [ln["start"] for ln in truth[1:]] + [round(t, 3)]}
    (out / "dialog.truth.json").write_text(json.dumps(info, indent=1))
    return info


def make_vfr(out: Path, src: Path) -> None:
    # Drop every 3rd frame in the first half -> genuinely variable frame timing
    sh("ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-vf", "select='if(lt(t,20),not(eq(mod(n,3),0)),1)'",
       "-fps_mode", "vfr", "-c:v", "libx264", "-c:a", "copy", str(out / "vfr.mkv"))


def make_delayed(out: Path, src: Path) -> None:
    sh("ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-itsoffset", "1.0", "-i", str(src),
       "-map", "0:v", "-map", "1:a", "-c", "copy", str(out / "delayed_audio.mp4"))


def make_sync(out: Path, seconds: int = 20) -> None:
    # 1 frame (40 ms) white flash and a 40 ms beep at t = 1, 3, 5, ... (every 2 s, offset 1 s)
    vf = "drawbox=x=0:y=0:w=iw:h=ih:color=white:t=fill:enable='lt(mod(t-1,2),0.04)*gte(t,1)'"
    af = "volume=enable='lt(mod(t-1,2),0.04)*gte(t,1)':volume=1,volume=enable='not(lt(mod(t-1,2),0.04)*gte(t,1))':volume=0"
    sh("ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"color=c=black:s=640x360:r=25:d={seconds}",
       "-f", "lavfi", "-i", f"sine=f=1000:sample_rate=48000:d={seconds}", "-vf", vf, "-af", af,
       "-c:v", "libx264", "-pix_fmt", "yuv420p", "-g", "50", "-c:a", "aac", "-shortest", str(out / "sync.mp4"))


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "fixtures").resolve()
    out.mkdir(parents=True, exist_ok=True)
    info = make_dialog(out)
    make_vfr(out, Path(info["file"]))
    make_delayed(out, Path(info["file"]))
    make_sync(out)
    print(json.dumps({"out": str(out), "dialog_duration": dur(Path(info["file"]))}))
