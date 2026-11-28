"""Close look: full-resolution frames (or a crop) for a short time range, optionally packed in a sheet."""
from __future__ import annotations

import subprocess
from pathlib import Path

from .sheets import layout, render
from .util import fmt_ts


def zoom(video: Path, out_dir: Path, start: float, end: float, fps: float = 2.0, width: int = 1280,
         crop: str | None = None, sheet: bool = True, aspect: float = 1.78) -> dict:
    end = max(end, start + 0.05)
    tag = f"{int(start * 1000):09d}-{int(end * 1000):09d}-{fps:g}" + (f"-c{crop.replace(',', '_')}" if crop else "")
    d = out_dir / tag
    d.mkdir(parents=True, exist_ok=True)
    vf = []
    if crop:
        x, y, w, h = crop.split(",")
        vf.append(f"crop={w}:{h}:{x}:{y}")
    vf += [f"fps={fps}", f"scale={width}:-2"]
    # Output frame k of the fps filter is at start + k/fps (+-half a source frame).
    subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-ss", f"{start:.3f}", "-i", str(video),
                    "-t", f"{end - start:.3f}", "-map", "0:v:0", "-vf", ",".join(vf), "-q:v", "2",
                    str(d / "z_%04d.jpg")], check=True, capture_output=True)
    files = sorted(d.glob("z_*.jpg"))
    frames = [{"t": round(start + k / fps, 3), "path": str(p)} for k, p in enumerate(files)]
    out = {"dir": str(d), "frames": frames}
    if sheet and frames:
        lay = layout(aspect if not crop else int(crop.split(",")[2]) / max(1, int(crop.split(",")[3])), None)
        cols = min(3, len(frames))
        lay = dict(lay, cols=cols, tile_w=min(1560 // cols, lay["tile_w"] * 3 // 2))
        lay["tile_h"] = int(lay["tile_w"] / (aspect if not crop else int(crop.split(",")[2]) / max(1, int(crop.split(",")[3]))))
        sheets = []
        for i in range(0, len(frames), 6):
            p = d / f"zoom_sheet_{i // 6 + 1:02d}.jpg"
            render(frames[i:i + 6], f"zoom {fmt_ts(start)}-{fmt_ts(end)} @ {fps:g} fps", lay, p, tag_fn=lambda t: None)
            sheets.append(str(p))
        out["sheets"] = sheets
    return out
