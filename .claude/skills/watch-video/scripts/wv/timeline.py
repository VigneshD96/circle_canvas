"""The one time contract.

Master timeline = seconds since the container start (ffprobe format.start_time). This is the timeline that
ffmpeg uses for input `-ss` seeking and for `trim`/`atrim` filters (without -copyts), so every stage
can pass these seconds straight to ffmpeg.

- Video frames: we keep the real PTS reported by ffmpeg `showinfo` (already relative to container start).
- Audio: the extracted wav has no timestamps; sample 0 sits at `audio_offset` on the master timeline.
  Every audio-derived time (words, turns, events) is shifted by that offset exactly once, in audio.py.
"""
from __future__ import annotations


def audio_offset(probe: dict, order: int | None) -> float:
    if order is None:
        return 0.0
    for a in probe["audio"]:
        if a["order"] == order:
            return max(0.0, float(a.get("start_offset") or 0.0))
    raise ValueError(f"audio stream {order} not found")


def shift(items: list[dict], offset: float, keys=("start", "end")) -> list[dict]:
    if not offset:
        return items
    for it in items:
        for k in keys:
            if it.get(k) is not None:
                it[k] = round(it[k] + offset, 4)
    return items
