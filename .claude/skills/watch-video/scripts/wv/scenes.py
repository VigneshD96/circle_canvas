"""Character scenes: every scene a person takes part in (with everyone they talk to), nothing else.

Source of scenes: the merged watcher scene logs (timeline.json), which say who is on screen per scene.
A scene is kept if the person is on screen in it or speaks in it (effective speaker labels, overrides
included). Short people-free scenes that lead into a kept scene (establishing shots) are kept as bridges.
Adjacent kept scenes merge into one segment.

Edges: the watchers' scene times come from sparse sheets and are about +-1.5 s off, and sitcoms often change
scene with a dissolve, not a hard cut. Tried and rejected (2026-10, Friends S07E22): colour-histogram edge
refinement and a linear-blend dissolve fit on the scan thumbnails. Both were right on some edges and wrong
by 1-3 s on others (motion during dissolves, slow camera moves inside a scene). So the code only proposes
(one-sided hard-cut snap, else the logged time) and draws an edge-check strip per edge; the agent decides
the exact edge by eye. That check fixed 6 of 10 edges in the test episode.
"""
from __future__ import annotations

import bisect
import re
import subprocess

import numpy as np

SNAP_S = 2.0
BRIDGE_MAX_S = 20.0
MERGE_GAP_S = 1.5


def name_pattern(who: str) -> re.Pattern:
    # "Chandler" must not match "Helena (Chandler's dad)" or "Chandler's apartment"
    return re.compile(rf"\b{re.escape(who)}\b(?!['’]s)", re.IGNORECASE)


def mentions(texts: list[str], pat: re.Pattern) -> bool:
    return any(pat.search(t or "") for t in texts)


def _nearest(cuts: list[float], t: float, max_d: float) -> float | None:
    i = bisect.bisect_left(cuts, t)
    best = None
    for j in (i - 1, i):
        if 0 <= j < len(cuts) and abs(cuts[j] - t) <= max_d and (best is None or abs(cuts[j] - t) < abs(best - t)):
            best = cuts[j]
    return best


def select(scenes: list[dict], words: list[dict], who: str, known_names: list[str], cuts: list[float],
           duration: float, min_words: int = 2) -> dict:
    pat = name_pattern(who)
    people = [name_pattern(n) for n in known_names if n]
    scenes = sorted(scenes, key=lambda s: s["start"])
    picked = []
    for sc in scenes:
        spoken = [w for w in words if sc["start"] <= w["start"] < sc["end"] and w["spk"].lower() == who.lower()]
        on = mentions(sc.get("on_screen", []), pat)
        why = []
        if on:
            why.append("on screen")
        if len(spoken) >= min_words:
            why.append(f"speaks {len(spoken)} words")
        picked.append({**sc, "keep": bool(why), "why": ", ".join(why),
                       "people_free": not any(mentions(sc.get("on_screen", []), p) for p in people)})
    for i, sc in enumerate(picked):  # establishing shots that lead into a kept scene
        if (not sc["keep"] and sc["people_free"] and sc["end"] - sc["start"] <= BRIDGE_MAX_S
                and i + 1 < len(picked) and picked[i + 1]["keep"]):
            sc["keep"], sc["why"] = True, "bridge (no people) into the next kept scene"
    segs: list[dict] = []
    for sc in picked:
        if not sc["keep"]:
            continue
        if segs and sc["start"] - segs[-1]["end"] <= MERGE_GAP_S:
            segs[-1]["end"] = max(segs[-1]["end"], sc["end"])
            segs[-1]["scenes"].append(sc)
        else:
            segs.append({"start": sc["start"], "end": sc["end"], "scenes": [sc]})
    for s in segs:
        s["edge_method"] = []
        for side in ("start", "end"):
            t = s[side]
            if (side == "start" and t <= SNAP_S) or (side == "end" and t >= duration - SNAP_S):
                s[side] = 0.0 if side == "start" else duration
                s["edge_method"].append(f"{side}: file edge")
                continue
            # one-sided: never start before or end after the logged scene edge by more than 0.5 s
            lo, hi = (t - 0.5, t + SNAP_S) if side == "start" else (t - SNAP_S, t + 0.5)
            cand = [c for c in cuts if lo <= c <= hi]
            if cand:
                s[side] = min(cand, key=lambda c: abs(c - t))
            s["edge_method"].append(f"{side}: {'cut' if cand else 'logged'} {s[side]:.2f}")
        s["start"], s["end"] = round(s["start"], 3), round(s["end"], 3)
        s["label"] = f"{who}: " + " / ".join(dict.fromkeys(sc["setting"].split(",")[0][:40] for sc in s["scenes"]))
        s["reason"] = "; ".join(f"{sc['start']:.0f}-{sc['end']:.0f} {sc['why']}" for sc in s["scenes"])
    dropped = [{"start": sc["start"], "end": sc["end"], "setting": sc["setting"]} for sc in picked if not sc["keep"]]
    return {"segments": [{k: s[k] for k in ("start", "end", "label", "reason", "edge_method")} for s in segs
                         if s["end"] > s["start"]],
            "dropped_scenes": dropped,
            "seconds": round(sum(s["end"] - s["start"] for s in segs), 1)}


def edge_sheets(video, segments: list[dict], out_dir, aspect: float) -> list[dict]:
    """One 4 fps strip (+-2 s) per segment edge, the proposed edge tile marked, so the agent can confirm by eye."""
    from pathlib import Path

    from .sheets import layout, render
    from .util import fmt_ts

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    lay = layout(aspect, None)
    lay = dict(lay, cols=5, tile_w=300, tile_h=int(300 / aspect), font_px=16)
    res = []
    for k, seg in enumerate(segments, 1):
        for side in ("start", "end"):
            t = seg[side]
            t0 = max(0.0, t - 2.5)
            d = out_dir / f"seg{k:02d}_{side}"
            d.mkdir(exist_ok=True)
            subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-ss", f"{t0:.3f}", "-i", str(video),
                            "-t", "5", "-map", "0:v:0", "-vf", "fps=5,scale=300:-2", "-q:v", "4", str(d / "f_%03d.jpg")],
                           capture_output=True)
            files = sorted(d.glob("f_*.jpg"))
            tiles = [{"t": t0 + i / 5, "path": str(f)} for i, f in enumerate(files)]
            if not tiles:
                continue
            mark = min(range(len(tiles)), key=lambda i: abs(tiles[i]["t"] - t))
            tag = "START here" if side == "start" else "END here"
            path = out_dir / f"seg{k:02d}_{side}.jpg"
            render(tiles, f"segment {k} {side} {fmt_ts(t)}: kept part is {'right of' if side == 'start' else 'left of'} the mark",
                   lay, path, tag_fn=lambda tl, m=tiles[mark]: tag if tl is m else None)
            res.append({"segment": k, "side": side, "t": t, "sheet": str(path)})
    return res
