"""Word -> speaker alignment and line building.

Rules (see plan):
- frac(spk) = share of the word's duration covered by that speaker's EXCLUSIVE turns.
- best >= 0.5 and best - second >= MARGIN  -> speaker = best.
- best >= 0.5 and margin small             -> speaker = best, alt = second, flag "ambiguous".
- 0 < best < 0.5                            -> speaker = best, flag "weak".
- no overlap, nearest turn edge <= NEAR_S   -> speaker = nearest, flag "near".
- otherwise                                 -> UNKNOWN.
- word midpoint inside a REGULAR-diarization overlap region -> flag "overlap".
Events (laughter, music) are annotations only. They never delete words or turns.
"""
from __future__ import annotations

import bisect
from collections import defaultdict

UNKNOWN = "UNKNOWN"
MARGIN = 0.2
NEAR_S = 0.3
LINE_GAP_S = 1.0
LINE_SOFT_MAX_S = 25.0
LINE_HARD_MAX_S = 40.0
NONSPEECH_TAGS = {"LAUGHTER", "APPLAUSE", "MUSIC", "CHEERING", "CROWD", "SINGING"}


def overlap_regions(regular: list[dict]) -> list[tuple[float, float]]:
    """Intervals where >= 2 speakers are active in the regular diarization."""
    pts = []
    for t in regular:
        pts.append((t["start"], 1))
        pts.append((t["end"], -1))
    pts.sort(key=lambda p: (p[0], p[1]))
    out, active, start = [], 0, None
    for x, d in pts:
        prev = active
        active += d
        if prev < 2 <= active:
            start = x
        elif prev >= 2 > active and start is not None:
            if x - start > 0.05:
                out.append((round(start, 3), round(x, 3)))
            start = None
    return out


def _in_regions(t: float, regions: list[tuple[float, float]], starts: list[float]) -> bool:
    i = bisect.bisect_right(starts, t) - 1
    return i >= 0 and regions[i][0] <= t <= regions[i][1]


def assign_words(words: list[dict], excl: list[dict], regular: list[dict] | None = None) -> list[dict]:
    excl = sorted(excl, key=lambda t: t["start"])
    starts = [t["start"] for t in excl]
    max_len = max((t["end"] - t["start"] for t in excl), default=0.0)
    ov_regions = overlap_regions(regular or [])
    ov_starts = [r[0] for r in ov_regions]
    out = []
    for w in words:
        ws, we = w["start"], w["end"]
        dur = max(we - ws, 0.02)
        lo = max(0, bisect.bisect_left(starts, ws - max_len - NEAR_S))
        hi = bisect.bisect_right(starts, we + NEAR_S)
        cover: dict[str, float] = defaultdict(float)
        nearest, nearest_d = None, 1e9
        for t in excl[lo:hi]:
            ov = min(we, t["end"]) - max(ws, t["start"])
            if ov > 0:
                cover[t["spk"]] += ov
            else:
                d = max(t["start"] - we, ws - t["end"])
                if d < nearest_d:
                    nearest, nearest_d = t["spk"], d
        ranked = sorted(((v / dur, k) for k, v in cover.items()), reverse=True)
        rec = {**w, "spk": UNKNOWN, "alt": None, "flags": []}
        if ranked:
            best, bspk = ranked[0]
            second, sspk = ranked[1] if len(ranked) > 1 else (0.0, None)
            rec["spk"] = bspk
            if best >= 0.5:
                if best - second < MARGIN and sspk:
                    rec["alt"], rec["flags"] = sspk, ["ambiguous"]
            else:
                rec["flags"] = ["weak"]
                rec["alt"] = sspk
        elif nearest is not None and nearest_d <= NEAR_S:
            rec["spk"], rec["flags"] = nearest, ["near"]
        # ASR word times run slightly early, so a sentence-first word that straddles a turn start is usually
        # the new speaker's first word, not the previous speaker's last word.
        if len(ranked) > 1 and out and out[-1]["w"][-1:] in ".?!":
            other = ranked[1][1] if ranked[0][1] == rec["spk"] else ranked[0][1]
            if any(ws < t["start"] < we and t["spk"] == other for t in excl[lo:hi]):
                rec["alt"], rec["spk"] = rec["spk"], other
                rec["flags"] = ["ambiguous"]
        mid = (ws + we) / 2
        if ov_regions and _in_regions(mid, ov_regions, ov_starts):
            rec["flags"] = rec["flags"] + ["overlap"]
        out.append(rec)
    return out


def relabel(excl: list[dict]) -> dict[str, str]:
    """Raw pyannote labels -> S1..Sn by exclusive talk time (desc). Deterministic for one diarization."""
    talk: dict[str, float] = defaultdict(float)
    for t in excl:
        talk[t["spk"]] += t["end"] - t["start"]
    order = sorted(talk, key=lambda k: (-talk[k], k))
    return {raw: f"S{i + 1}" for i, raw in enumerate(order)}


def build_lines(words: list[dict]) -> list[dict]:
    lines: list[dict] = []
    cur = None
    for w in words:
        new = (
            cur is None
            or w["spk"] != cur["spk"]
            or w["start"] - cur["end"] > LINE_GAP_S
            or (w["start"] - cur["start"] > LINE_SOFT_MAX_S and cur["text"][-1:] in ".?!")
            or w["start"] - cur["start"] > LINE_HARD_MAX_S
        )
        if new:
            cur = {"spk": w["spk"], "start": w["start"], "end": w["end"], "text": w["w"], "n": 0, "flagged": 0,
                   "overlap": 0, "alts": set()}
            lines.append(cur)
        else:
            cur["text"] += " " + w["w"]
            cur["end"] = w["end"]
        cur["n"] += 1
        fl = set(w.get("flags") or [])
        if fl & {"weak", "near", "ambiguous"} or w["spk"] == UNKNOWN:
            cur["flagged"] += 1
        if "overlap" in fl:
            cur["overlap"] += 1
        if w.get("alt"):
            cur["alts"].add(w["alt"])
    for ln in lines:
        dur = max(ln["end"] - ln["start"], 0.1)
        ln["rate"] = round(ln["n"] / dur, 2)
        ln["uncertain"] = ln["flagged"] / ln["n"] > 0.3
        ln["alts"] = sorted(ln["alts"])
        ln["start"], ln["end"] = round(ln["start"], 2), round(ln["end"], 2)
    return lines


def _overlap_len(a0, a1, spans) -> float:
    return sum(max(0.0, min(a1, s["end"]) - max(a0, s["start"])) for s in spans)


def nonword_turns(excl: list[dict], words: list[dict], events: list[dict], min_len: float = 0.4) -> list[dict]:
    """Exclusive turns with no recognized words. Kept as evidence, flagged if they sit in laughter/music."""
    wst = [w["start"] for w in words]
    ns_events = [e for e in events if e["type"] in NONSPEECH_TAGS]
    out = []
    for t in excl:
        if t["end"] - t["start"] < min_len:
            continue
        i = bisect.bisect_left(wst, t["start"] - 0.05)
        has_word = i < len(words) and words[i]["start"] < t["end"]
        if has_word:
            continue
        frac = _overlap_len(t["start"], t["end"], ns_events) / (t["end"] - t["start"])
        out.append({**t, "likely_non_speech": frac >= 0.5})
    return out


def speaker_stats(excl: list[dict], words: list[dict], nonword: list[dict]) -> dict[str, dict]:
    st: dict[str, dict] = defaultdict(lambda: {"talk_s": 0.0, "turns": 0, "words": 0, "flagged_words": 0,
                                               "first": None, "nonword_s": 0.0, "nonspeech_s": 0.0})
    for t in excl:
        s = st[t["spk"]]
        s["talk_s"] += t["end"] - t["start"]
        s["turns"] += 1
        s["first"] = t["start"] if s["first"] is None else min(s["first"], t["start"])
    for w in words:
        s = st[w["spk"]]
        s["words"] += 1
        if w["spk"] == UNKNOWN or set(w.get("flags") or []) & {"weak", "near", "ambiguous"}:
            s["flagged_words"] += 1
    for t in nonword:
        st[t["spk"]]["nonword_s"] += t["end"] - t["start"]
        if t["likely_non_speech"]:
            st[t["spk"]]["nonspeech_s"] += t["end"] - t["start"]
    for k, s in st.items():
        s["talk_s"] = round(s["talk_s"], 1)
        s["nonword_s"] = round(s["nonword_s"], 1)
        s["nonspeech_s"] = round(s["nonspeech_s"], 1)
        s["likely_not_a_person"] = bool(s["talk_s"] > 0 and s["nonspeech_s"] / s["talk_s"] >= 0.5 and s["words"] < 20)
    return dict(st)


def align(words: list[dict], diar: dict, events: list[dict]) -> dict:
    mapping = relabel(diar["exclusive"])

    def m(x):
        return mapping.get(x, x)

    excl = [{**t, "spk": m(t["spk"])} for t in diar["exclusive"]]
    regular = [{**t, "spk": m(t["spk"])} for t in diar["regular"]]
    aw = assign_words(words, excl, regular)
    for w in aw:
        if w.get("alt"):
            w["alt"] = m(w["alt"])
    lines = build_lines(aw)
    nonword = nonword_turns(excl, aw, events)
    stats = speaker_stats(excl, aw, nonword)
    return {"mapping": mapping, "words": aw, "lines": lines, "nonword_turns": nonword, "stats": stats,
            "overlaps": overlap_regions(regular), "exclusive": excl}
