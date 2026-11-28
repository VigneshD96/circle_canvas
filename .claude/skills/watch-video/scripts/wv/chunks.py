"""Chunk planner. Chunk count follows a per-worker sheet budget (not a fixed cap).

Boundaries snap to a nearby shot cut that sits in a silence gap (best), else a silence gap, else a cut.
"""
from __future__ import annotations

import math

INLINE_MAX_SHEETS = 20
SHEETS_PER_CHUNK = 20


def silence_gaps(speech: list[dict], duration: float, min_gap: float = 0.4) -> list[tuple[float, float]]:
    gaps, prev = [], 0.0
    for s in sorted(speech, key=lambda x: x["start"]):
        if s["start"] - prev >= min_gap:
            gaps.append((prev, s["start"]))
        prev = max(prev, s["end"])
    if duration - prev >= min_gap:
        gaps.append((prev, duration))
    return gaps


def _snap(target: float, window: float, cuts: list[float], gaps: list[tuple[float, float]]) -> float:
    best, best_score = target, 1.0  # score 1.0 = "no candidate"; lower is better
    for c in cuts:
        if abs(c - target) > window:
            continue
        in_gap = any(a - 0.2 <= c <= b + 0.2 for a, b in gaps)
        sc = abs(c - target) / window - (0.5 if in_gap else 0.2)
        if sc < best_score:
            best, best_score = c, sc
    for a, b in gaps:
        mid = (a + b) / 2
        if abs(mid - target) > window:
            continue
        sc = abs(mid - target) / window - 0.3
        if sc < best_score:
            best, best_score = mid, sc
    return round(best, 3)


def plan(kept: list[dict], shots: list[dict], speech: list[dict], duration: float, per_sheet: int,
         inline_max: int = INLINE_MAX_SHEETS, sheets_per_chunk: int = SHEETS_PER_CHUNK) -> dict:
    total_sheets = math.ceil(len(kept) / per_sheet) if kept else 0
    if total_sheets <= inline_max:
        return {"mode": "inline", "total_sheets": total_sheets,
                "chunks": [{"id": 1, "start": 0.0, "end": round(duration + 0.001, 3)}]}
    n = math.ceil(total_sheets / sheets_per_chunk)
    cuts = [s["start"] for s in shots[1:]]
    gaps = silence_gaps(speech, duration)
    times = [k["t"] for k in kept]
    bounds = [0.0]
    for j in range(1, n):
        target = times[min(len(times) - 1, round(j * len(times) / n))]
        window = min(60.0, 0.15 * duration / n)
        b = _snap(target, window, cuts, gaps)
        if b <= bounds[-1] + 1.0:
            b = target
        bounds.append(b)
    bounds.append(round(duration + 0.001, 3))
    chunks = [{"id": i + 1, "start": bounds[i], "end": bounds[i + 1]} for i in range(n)]
    return {"mode": "fanout", "total_sheets": total_sheets, "chunks": chunks}
