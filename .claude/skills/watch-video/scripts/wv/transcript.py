"""Render the speaker-tagged transcript (with audio events) as markdown. Names come from speakers.json."""
from __future__ import annotations

import re

from .align import UNKNOWN, build_lines
from .util import fmt_dur, fmt_ts


def _norm(w: str) -> str:
    return re.sub(r"[^a-z0-9']", "", w.lower())


def resolve_overrides(words: list[dict], overrides: list[dict], window: float = 6.0) -> tuple[list[dict], list[str]]:
    """Turn phrase overrides {"text","t","name"[,"id"]} into exact {"id","start","end","name"} entries.

    The phrase is matched word by word (case/punctuation-insensitive) near time t; one entry is produced per
    speaker ID found among the matched words (or only for "id" if given). Entries with start/end pass through.
    """
    out, problems = [], []
    norm = [_norm(w["w"]) for w in words]
    for o in overrides:
        if "start" in o and "end" in o:
            out.append(o)
            continue
        toks = [_norm(x) for x in str(o.get("text", "")).split() if _norm(x)]
        if not toks or "t" not in o:
            problems.append(f"override needs start/end or text+t: {o}")
            continue
        best = None
        for i in range(len(words) - len(toks) + 1):
            if abs(words[i]["start"] - o["t"]) > window or norm[i:i + len(toks)] != toks:
                continue
            d = abs(words[i]["start"] - o["t"])
            if best is None or d < best[0]:
                best = (d, i)
        if best is None:
            problems.append(f"phrase not found near {o['t']}: {o.get('text')!r}")
            continue
        span = words[best[1]:best[1] + len(toks)]
        ids = [o["id"]] if o.get("id") else sorted({w["spk"] for w in span})
        for sid in ids:
            mine = [w for w in span if w["spk"] == sid] or span
            out.append({"id": sid, "start": round(mine[0]["start"] - 0.01, 3), "end": round(mine[-1]["end"] + 0.01, 3),
                        "name": o["name"], "why": o.get("why", ""), "text": o.get("text")})
    return out, problems

FAST_WPS = 3.8


class Namer:
    """speakers.json -> display labels. High confidence: 'Ross'. Lower: 'Ross? [S3]'. None: 'S3'."""

    def __init__(self, speakers: dict | None):
        speakers = speakers or {}
        self.map = speakers.get("speakers", {})
        self.overrides = speakers.get("overrides", [])

    def override(self, spk: str, t: float | None) -> str | None:
        if t is not None:
            for o in self.overrides:
                if o.get("id") == spk and o["start"] <= t <= o["end"]:
                    return o["name"]
        return None

    def name(self, spk: str, t: float | None = None) -> str:
        ov = self.override(spk, t)
        if ov:
            return ov
        if spk == UNKNOWN:
            return "??"
        e = self.map.get(spk)
        if not e or not e.get("name"):
            return spk
        return e["name"] if e.get("confidence") == "high" else f"{e['name']}? [{spk}]"

    def label(self, spk: str, t: float | None = None) -> str:
        """Who this is for edits: override name, else mapped name (any confidence), else the ID."""
        return self.override(spk, t) or (self.map.get(spk) or {}).get("name") or spk

    def relabel(self, al: dict) -> dict:
        """Copy of an alignment whose words/turns carry effective labels (names + time-range overrides)."""
        words = [dict(w, spk=self.label(w["spk"], (w["start"] + w["end"]) / 2)) for w in al["words"]]
        excl = [dict(x, spk=self.label(x["spk"], (x["start"] + x["end"]) / 2)) for x in al["exclusive"]]
        return dict(al, words=words, exclusive=excl)

    def with_overrides(self, al: dict) -> dict:
        """Alignment for display: words inside an override carry the override name; lines are rebuilt so a
        corrected phrase becomes its own line."""
        if not self.overrides:
            return al

        def lab(spk):  # same label for the same person, so corrected words join that person's line
            e = self.map.get(spk) or {}
            return e["name"] if e.get("name") and e.get("confidence") == "high" else spk

        words = []
        for w in al["words"]:
            ov = self.override(w["spk"], (w["start"] + w["end"]) / 2)
            if ov:  # hand-verified: no residual uncertainty
                words.append(dict(w, spk=ov, alt=None, flags=[f for f in w.get("flags", []) if f == "overlap"]))
            else:
                words.append(dict(w, spk=lab(w["spk"]), alt=lab(w["alt"]) if w.get("alt") else None))
        return dict(al, words=words, lines=build_lines(words))

    def ids_for(self, who: str) -> list[str]:
        """Speaker IDs that map to a name (case-insensitive) or the ID itself."""
        w = who.strip().lower()
        ids = [k for k, v in self.map.items() if (v.get("name") or "").lower() == w]
        return ids or ([who.strip().upper()] if who.strip().upper().startswith("S") else [])


def _overlap_frac(a0: float, a1: float, spans: list[dict]) -> float:
    d = max(a1 - a0, 1e-3)
    return sum(max(0.0, min(a1, s["end"]) - max(a0, s["start"])) for s in spans) / d


def line_text(ln: dict, namer: Namer, loud: list[dict]) -> str:
    tags = []
    if ln.get("uncertain"):
        tags.append("(?" + (f" maybe {'/'.join(namer.name(a) for a in ln['alts'])}" if ln.get("alts") else "") + ")")
    if ln.get("overlap", 0) and ln["overlap"] / max(ln["n"], 1) >= 0.3:
        tags.append("(overlap)")
    if loud and _overlap_frac(ln["start"], ln["end"], loud) >= 0.5:
        tags.append("«loud»")
    if ln.get("rate", 0) > FAST_WPS and ln["end"] - ln["start"] >= 2:
        tags.append("(fast)")
    suffix = (" " + " ".join(tags)) if tags else ""
    return f"[{fmt_ts(ln['start'])}–{fmt_ts(ln['end'])}] {namer.name(ln['spk'], ln['start'])}: {ln['text']}{suffix}"


def entries(al: dict, events: list[dict], namer: Namer, loud: list[dict], start: float = 0.0,
            end: float = float("inf")) -> list[tuple[float, str]]:
    out = []
    for ln in al["lines"]:
        if start <= ln["start"] < end:
            out.append((ln["start"], line_text(ln, namer, loud)))
    hide = {k for k, s in al["stats"].items() if s.get("likely_not_a_person")}
    for t in al["nonword_turns"]:
        if start <= t["start"] < end and not t["likely_non_speech"] and t["spk"] not in hide and t["end"] - t["start"] >= 0.6:
            out.append((t["start"], f"[{fmt_ts(t['start'])}–{fmt_ts(t['end'])}] {namer.name(t['spk'], t['start'])}: "
                                    f"[voice, no words recognized]"))
    for e in events:
        if start <= e["start"] < end:
            out.append((e["start"], f"[{fmt_ts(e['start'])}–{fmt_ts(e['end'])}] [{e['type']}]"))
    out.sort(key=lambda x: x[0])
    return out


def speakers_table(al: dict, namer: Namer) -> str:
    rows = ["| ID | Name | Talk time | Words | Unsure words | First heard | Note |", "|---|---|---|---|---|---|---|"]
    for spk, s in sorted(al["stats"].items(), key=lambda kv: -kv[1]["talk_s"]):
        if spk == UNKNOWN:
            continue
        nm = namer.name(spk)
        note = "likely NOT a person (laughter/music)" if s.get("likely_not_a_person") else ""
        pct = f"{100 * s['flagged_words'] / s['words']:.0f}%" if s["words"] else "-"
        rows.append(f"| {spk} | {nm if nm != spk else ''} | {fmt_dur(s['talk_s'])} | {s['words']} | {pct} | "
                    f"{fmt_ts(s['first']) if s['first'] is not None else '-'} | {note} |")
    unk = al["stats"].get(UNKNOWN)
    if unk:
        rows.append(f"\nWords with no speaker (UNKNOWN, shown as ??): {unk['words']}")
    return "\n".join(rows)


LEGEND = ("Legend: `(?)` speaker unsure (maybe = other candidate) | `(overlap)` people talk over each other, "
          "the words are mostly the loudest voice | `«loud»` loud passage | `(fast)` fast speech | "
          "`[LAUGHTER]` etc. = sound events, boundaries ±0.5 s | `??` = speaker unknown.")


def render(al: dict, events: list[dict], namer: Namer, loud: list[dict], title: str) -> str:
    body = "\n".join(txt for _, txt in entries(al, events, namer, loud))
    return f"# Transcript — {title}\n\n{speakers_table(al, namer)}\n\n{LEGEND}\n\n{body}\n"
