"""ffprobe wrapper: the facts every other stage needs about the source file."""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from .util import run


def _f(x, default=None):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def _rate(s: str | None) -> float | None:
    if not s or s in ("0/0", "0"):
        return None
    try:
        return float(Fraction(s))
    except (ValueError, ZeroDivisionError):
        return None


def probe(path: str | Path) -> dict:
    p = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)])
    data = json.loads(p.stdout)
    fmt = data.get("format", {})
    fmt_start = _f(fmt.get("start_time"), 0.0) or 0.0
    out = {
        "path": str(Path(path).resolve()),
        "container": fmt.get("format_name"),
        "duration": _f(fmt.get("duration"), 0.0),
        "start_time": fmt_start,
        "size_bytes": int(fmt.get("size", 0) or 0),
        "tags": {k.lower(): v for k, v in (fmt.get("tags") or {}).items()},
        "video": None,
        "audio": [],
    }
    for s in data.get("streams", []):
        st = s.get("codec_type")
        if st == "video" and out["video"] is None and not (s.get("disposition") or {}).get("attached_pic"):
            rot = 0
            for sd in s.get("side_data_list") or []:
                if "rotation" in sd:
                    rot = int(_f(sd["rotation"], 0))
            rot = rot or int(_f((s.get("tags") or {}).get("rotate"), 0))
            w, h = int(s.get("width", 0)), int(s.get("height", 0))
            if abs(rot) % 180 == 90:
                w, h = h, w
            r, avg = _rate(s.get("r_frame_rate")), _rate(s.get("avg_frame_rate"))
            out["video"] = {
                "index": s["index"],
                "codec": s.get("codec_name"),
                "width": w,  # display size (rotation applied)
                "height": h,
                "rotation": rot,
                "fps": avg or r,
                "vfr": bool(r and avg and abs(r - avg) / max(r, avg) > 0.01),
                "start_offset": (_f(s.get("start_time"), fmt_start) or fmt_start) - fmt_start,
                "duration": _f(s.get("duration")),
            }
        elif st == "audio":
            out["audio"].append({
                "index": s["index"],
                "order": len(out["audio"]),  # N in -map 0:a:N
                "codec": s.get("codec_name"),
                "channels": s.get("channels"),
                "sample_rate": int(s.get("sample_rate", 0) or 0),
                "start_offset": (_f(s.get("start_time"), fmt_start) or fmt_start) - fmt_start,
                "language": (s.get("tags") or {}).get("language"),
                "title": (s.get("tags") or {}).get("title"),
                "default": bool((s.get("disposition") or {}).get("default")),
            })
    if out["video"]:
        w, h = out["video"]["width"], out["video"]["height"]
        out["video"]["aspect"] = round(w / h, 3) if h else None
    return out


def default_audio_order(pr: dict) -> int | None:
    """Pick the audio stream: default-flagged first, else the first one."""
    if not pr["audio"]:
        return None
    for a in pr["audio"]:
        if a["default"]:
            return a["order"]
    return 0
