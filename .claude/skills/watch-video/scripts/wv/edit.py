"""Plain-cut editing from an EDL. The agent picks segments; this module validates, snaps and renders.

Render (default): one ffmpeg call, per segment an accurately seeked input (`-ss S -t D -i src`), audio
re-timed with `aresample=async=1:first_pts=0` (keeps a delayed audio start in sync), then the `concat`
filter, encoded once (libx264 crf 18 + AAC). More than BATCH segments: near-lossless intermediates
(x264 crf 12 + PCM) per batch, then one final encode. `--fast-copy` = stream copy at keyframes (APPROXIMATE).
"""
from __future__ import annotations

import bisect
import json
import math
import re
import subprocess
from pathlib import Path

from .align import UNKNOWN
from .util import fmt_ts, log, write_json

SNAP_LIMIT = 0.25
PAD = 0.15
MIN_SEG = 0.04
BATCH = 32
FADE = 0.01
CUT_TOL = 0.12


# ---------------------------------------------------------------- EDL
def load_edl(src: str) -> dict:
    p = Path(src).expanduser()
    data = json.loads(p.read_text(encoding="utf-8")) if p.exists() else json.loads(src)
    if isinstance(data, list):
        data = {"segments": data}
    data.setdefault("mode", "join")
    data.setdefault("order", "time")
    return data


def validate_edl(segs: list[dict], duration: float, order: str = "time", merge: bool = True) -> tuple[list[dict], list[str]]:
    out, warn = [], []
    for i, s in enumerate(segs):
        try:
            a, b = float(s["start"]), float(s["end"])
        except (KeyError, TypeError, ValueError):
            raise ValueError(f"segment {i}: start/end must be numbers (seconds): {s}")
        if not (math.isfinite(a) and math.isfinite(b)):
            raise ValueError(f"segment {i}: start/end must be finite")
        if a < 0:
            warn.append(f"segment {i}: start {a} < 0, clamped to 0")
            a = 0.0
        if b > duration:
            if b - duration > 0.5:
                warn.append(f"segment {i}: end {b} > duration {duration:.2f}, clamped")
            b = duration
        if b - a < MIN_SEG:
            raise ValueError(f"segment {i}: end must be > start (got {a}-{b})")
        out.append({**s, "start": a, "end": b})
    if order == "time":
        out.sort(key=lambda s: s["start"])
        if merge:
            merged: list[dict] = []
            for s in out:
                if merged and s["start"] <= merged[-1]["end"] + 0.05:
                    m = merged[-1]
                    m["end"] = max(m["end"], s["end"])
                    m["label"] = " + ".join(x for x in (m.get("label"), s.get("label")) if x)
                    warn.append(f"merged overlapping segments at {fmt_ts(s['start'])}")
                else:
                    merged.append(dict(s))
            out = merged
    return out, warn


# ---------------------------------------------------------------- snapping
def _word_at(words: list[dict], starts: list[float], t: float) -> int | None:
    i = bisect.bisect_right(starts, t) - 1
    if i >= 0 and words[i]["start"] < t < words[i]["end"]:
        return i
    return None


def snap_edges(segs: list[dict], words: list[dict], frame_pts: list[float] | None, limit: float = SNAP_LIMIT,
               pad: float = PAD, keep_ids: set[str] | None = None,
               cuts: list[float] | None = None, speech: list[dict] | None = None) -> tuple[list[dict], list[str]]:
    """Move edges so no word is cut in half; pad into silence but never into someone else's word.
    If a shot cut falls inside the padding, the edge moves to the cut (no one-frame flash of the other shot)."""
    cuts = sorted(cuts or [])
    starts = [w["start"] for w in words]
    notes = []
    out = []
    for s in segs:
        a, b = s["start"], s["end"]
        i = _word_at(words, starts, a)
        if i is not None:
            w = words[i]
            if a - w["start"] <= limit:
                a = w["start"]
            elif w["end"] - a <= limit:
                a = w["end"]
            else:
                notes.append(f"start {fmt_ts(a)} cuts the word '{w['w']}' (too far to snap)")
        j = _word_at(words, starts, b)
        if j is not None:
            w = words[j]
            if w["end"] - b <= limit:
                b = w["end"]
            elif b - w["start"] <= limit:
                b = w["start"]
            else:
                notes.append(f"end {fmt_ts(b)} cuts the word '{w['w']}' (too far to snap)")
        # padding: into silence only, never into a word of another speaker (or any word if keep_ids is None)
        k = bisect.bisect_left(starts, a) - 1  # last word starting before a
        lo = a - pad
        if k >= 0 and words[k]["end"] > lo and words[k]["end"] <= a + 1e-6:
            if keep_ids is None or words[k].get("spk") not in keep_ids:
                lo = max(lo, words[k]["end"] + 0.02)
        a2 = min(a, max(0.0, lo))
        m = bisect.bisect_left(starts, b)  # first word starting at/after b
        hi = b + pad
        if m < len(words) and words[m]["start"] < hi:
            if keep_ids is None or words[m].get("spk") not in keep_ids:
                hi = min(hi, words[m]["start"] - 0.02)
        b2 = max(b, hi)
        if cuts:
            # Move an edge to a nearby shot cut when that only drops silence (no one-frame flash of the other
            # shot). ASR word edges move in 80 ms steps and often run early, so ask VAD first; without VAD,
            # allow a cut up to CUT_TOL inside the first/last word.
            for c in cuts[max(0, bisect.bisect_left(cuts, a2) - 1):bisect.bisect_right(cuts, a + SNAP_LIMIT)]:
                if a2 < c <= a + SNAP_LIMIT and (c <= a + CUT_TOL if speech is None else not _speech_in(speech, a2, c - 0.05)):
                    a2 = c
            for c in reversed(cuts[bisect.bisect_left(cuts, b - SNAP_LIMIT):bisect.bisect_right(cuts, b2)]):
                if b - SNAP_LIMIT <= c < b2 and (c >= b - CUT_TOL if speech is None else not _speech_in(speech, c + 0.05, b2)):
                    b2 = c
        if frame_pts:
            a2 = _frame_floor(frame_pts, a2)
            b2 = _frame_ceil(frame_pts, b2)
        if b2 - a2 >= MIN_SEG:
            out.append({**s, "start": round(a2, 4), "end": round(b2, 4), "requested": [s["start"], s["end"]]})
    # Padding must not make two segments overlap that did not overlap as requested: a "given"-order join would
    # show those frames twice (Kivi Short 2026-10-06: segments 0.2 s apart repeated 0.14 s). The overlap is
    # padding, so silence: both edges meet in its middle.
    order = sorted(range(len(out)), key=lambda i: out[i]["start"])
    for p, q in zip(order, order[1:]):
        A, B = out[p], out[q]
        if A["end"] > B["start"] and A["requested"][1] <= B["requested"][0]:
            m = (A["end"] + B["start"]) / 2
            if frame_pts:
                m = _frame_floor(frame_pts, m)
            A["end"] = B["start"] = round(m, 4)
            notes.append(f"padding overlap at {fmt_ts(m)}: edges meet there")
    return out, notes


def frame_align(segs: list[dict], frame_pts: list[float]) -> list[dict]:
    """Start on the frame at/after start, end on the frame at/after end (keeps the chosen edges, frame-exact)."""
    if not frame_pts:
        return segs
    out = []
    for s in segs:
        a, b = _frame_ceil(frame_pts, s["start"]), _frame_ceil(frame_pts, s["end"])
        if b - a >= MIN_SEG:
            out.append({**s, "start": round(a, 4), "end": round(b, 4)})
    return out


def _speech_in(speech: list[dict], x0: float, x1: float) -> bool:
    return x1 > x0 and any(min(x1, sp["end"]) - max(x0, sp["start"]) > 0.02 for sp in speech)


def _frame_floor(pts: list[float], t: float) -> float:
    i = bisect.bisect_right(pts, t + 1e-6) - 1
    return pts[i] if i >= 0 else t


def _frame_ceil(pts: list[float], t: float) -> float:
    i = bisect.bisect_left(pts, t - 1e-6)
    return pts[i] if i < len(pts) else t


# ---------------------------------------------------------------- speaker-only
def speaker_segments(al: dict, ids: set[str], overlap: str = "keep", strict: bool = False,
                     max_join_gap: float = 2.0) -> tuple[list[dict], dict]:
    """Segments where only the target speaker talks. Short lines are kept (no minimum length).

    Two target runs are joined only if the gap between them has no word from anyone else, no UNKNOWN word,
    and no exclusive diarization turn of another speaker longer than 0.2 s.
    """
    words = al["words"]
    other_turns = [t for t in al["exclusive"] if t["spk"] not in ids]
    ot_starts = [t["start"] for t in other_turns]

    def is_target(w):
        if w["spk"] not in ids:
            return False
        fl = set(w.get("flags") or [])
        if overlap == "drop" and "overlap" in fl:
            return False
        if strict and fl & {"weak", "near", "ambiguous"}:
            return False
        return True

    def other_speech_between(a, b) -> bool:
        i = max(0, bisect.bisect_left(ot_starts, a) - 1)
        for t in other_turns[i:]:
            if t["start"] >= b:
                break
            if min(b, t["end"]) - max(a, t["start"]) > 0.2:
                return True
        return False

    runs: list[dict] = []
    cur = None
    for w in words:
        if is_target(w):
            if cur and w["start"] - cur["end"] <= max_join_gap and not other_speech_between(cur["end"], w["start"]):
                cur["end"] = w["end"]
                cur["n"] += 1
                cur["flagged"] += bool(set(w.get("flags") or []) & {"weak", "near", "ambiguous"})
                cur["overlap"] += "overlap" in (w.get("flags") or [])
            else:
                cur = {"start": w["start"], "end": w["end"], "n": 1, "spk": w["spk"],
                       "flagged": int(bool(set(w.get("flags") or []) & {"weak", "near", "ambiguous"})),
                       "overlap": int("overlap" in (w.get("flags") or []))}
                runs.append(cur)
        elif cur is not None:
            # any other word (other speaker, UNKNOWN, or excluded target word) closes the run
            cur = None
    segs = [{"start": r["start"], "end": r["end"], "label": f"{r['spk']} {fmt_ts(r['start'])}",
             "reason": "speaker-only", "words": r["n"], "flagged_words": r["flagged"], "overlap_words": r["overlap"]}
            for r in runs]
    report = {"segments": len(segs), "seconds": round(sum(s["end"] - s["start"] for s in segs), 2),
              "words": sum(s["words"] for s in segs), "flagged_words": sum(s["flagged_words"] for s in segs),
              "overlap_words": sum(s["overlap_words"] for s in segs), "overlap_mode": overlap, "strict": strict}
    return segs, report


# ---------------------------------------------------------------- render
def _run(cmd: list[str]) -> None:
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("ffmpeg failed:\n" + p.stderr[-3000:])


def _safe(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "_", s)[:40].strip("_") or "clip"


def _graph(n: int, durs: list[float], has_audio: bool, a_order: int) -> tuple[str, list[str]]:
    parts, pads = [], []
    for i in range(n):
        parts.append(f"[{i}:v:0]setpts=PTS,format=yuv420p[v{i}]")
        pads.append(f"[v{i}]")
        if has_audio:
            d = durs[i]
            fo = max(0.0, d - FADE)
            parts.append(f"[{i}:a:{a_order}]aresample=async=1:first_pts=0,"
                         f"afade=t=in:st=0:d={FADE},afade=t=out:st={fo:.4f}:d={FADE}[a{i}]")
            pads.append(f"[a{i}]")
    parts.append("".join(pads) + f"concat=n={n}:v=1:a={1 if has_audio else 0}" + ("[v][a]" if has_audio else "[v]"))
    return ";".join(parts), (["-map", "[v]", "-map", "[a]"] if has_audio else ["-map", "[v]"])


def _inputs(src: Path, segs: list[dict]) -> list[str]:
    args = []
    for s in segs:
        # 0.5 ms early so float rounding never drops the frame that sits exactly on `start`
        args += ["-ss", f"{max(0.0, s['start'] - 0.0005):.4f}", "-t", f"{s['end'] - s['start']:.4f}", "-i", str(src)]
    return args


# Never carry source chapters / data / subtitle streams / global tags into a cut: an MKV's chapter track keeps
# the source's full duration and makes players show the wrong length and break seeking.
CLEAN = ["-map_chapters", "-1", "-map_metadata", "-1", "-dn", "-sn"]
FINAL_ENC = CLEAN + ["-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                     "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart"]
MID_ENC = CLEAN + ["-c:v", "libx264", "-crf", "12", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le"]


def render_join(src: Path, segs: list[dict], out: Path, has_audio: bool, a_order: int, work: Path) -> None:
    durs = [s["end"] - s["start"] for s in segs]
    if len(segs) <= BATCH:
        g, maps = _graph(len(segs), durs, has_audio, a_order)
        _run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", *_inputs(src, segs), "-filter_complex", g, *maps,
              *FINAL_ENC, str(out)])
        return
    work.mkdir(parents=True, exist_ok=True)
    mids = []
    for b in range(0, len(segs), BATCH):
        part = segs[b:b + BATCH]
        g, maps = _graph(len(part), [s["end"] - s["start"] for s in part], has_audio, a_order)
        mid = work / f"mid_{b // BATCH:03d}.mkv"
        _run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", *_inputs(src, part), "-filter_complex", g, *maps,
              *MID_ENC, str(mid)])
        mids.append(mid)
    ins, pads = [], []
    for i, m in enumerate(mids):
        ins += ["-i", str(m)]
        pads.append(f"[{i}:v:0]" + (f"[{i}:a:0]" if has_audio else ""))
    g = "".join(pads) + f"concat=n={len(mids)}:v=1:a={1 if has_audio else 0}" + ("[v][a]" if has_audio else "[v]")
    maps = ["-map", "[v]", "-map", "[a]"] if has_audio else ["-map", "[v]"]
    _run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", *ins, "-filter_complex", g, *maps, *FINAL_ENC, str(out)])
    for m in mids:
        m.unlink(missing_ok=True)


def render_fast_copy(src: Path, segs: list[dict], out: Path, work: Path) -> None:
    work.mkdir(parents=True, exist_ok=True)
    parts = []
    for i, s in enumerate(segs):
        p = work / f"fc_{i:04d}{out.suffix}"
        _run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-ss", f"{s['start']:.4f}", "-i", str(src),
              "-t", f"{s['end'] - s['start']:.4f}", "-map", "0:v:0", "-map", "0:a?", *CLEAN, "-c", "copy",
              "-avoid_negative_ts", "make_zero", str(p)])
        parts.append(p)
    lst = work / "list.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    _run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), *CLEAN,
          "-c", "copy", str(out)])
    for p in parts:
        p.unlink(missing_ok=True)


def render(src: Path, segs: list[dict], out_dir: Path, name: str, mode: str, has_audio: bool, a_order: int,
           fast_copy: bool = False) -> list[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    work = out_dir / ".work"
    outs = []
    if mode == "separate":
        for i, s in enumerate(segs):
            o = out_dir / f"{name}_{i + 1:02d}_{_safe(s.get('label') or fmt_ts(s['start']))}.mp4"
            if fast_copy:
                render_fast_copy(src, [s], o, work)
            else:
                render_join(src, [s], o, has_audio, a_order, work)
            outs.append(str(o))
    else:
        o = out_dir / f"{name}.mp4"
        if fast_copy:
            render_fast_copy(src, segs, o, work)
        else:
            render_join(src, segs, o, has_audio, a_order, work)
        outs.append(str(o))
    log(f"rendered {len(outs)} file(s) into {out_dir}")
    return outs


def write_edl_record(path: Path, src: Path, segs: list[dict], mode: str, outputs: list[str], notes: list[str],
                     fast_copy: bool) -> None:
    t = 0.0
    table = []
    for s in segs:
        d = s["end"] - s["start"]
        table.append({**s, "out_start": round(t, 4), "out_end": round(t + d, 4)})
        t += d if mode != "separate" else 0
    write_json(path, {"source": str(src), "mode": mode, "approximate": fast_copy, "segments": table,
                      "outputs": outputs, "notes": notes, "total": round(sum(s["end"] - s["start"] for s in segs), 4)})


def other_ids(al: dict, ids: set[str]) -> set[str]:
    return {w["spk"] for w in al["words"] if w["spk"] not in ids and w["spk"] != UNKNOWN}
