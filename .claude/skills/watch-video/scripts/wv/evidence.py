"""Speaker evidence pack: what the agent needs to map S1..Sn to names.

Per speaker: talk time, longest lines, frames taken while they speak alone, names other people say just
before this speaker talks, self-introductions, and voice-embedding similarity to other IDs (possible
split of one person). All of it is evidence, not proof (a reaction shot can show the listener).
"""
from __future__ import annotations

import re
import subprocess
from collections import Counter
from pathlib import Path

import numpy as np

from .align import UNKNOWN
from .sheets import render as render_sheet
from .util import fmt_dur, fmt_ts

_STOP = set("""I I'm I've I'll I'd The A An And But Or So Yes No Oh Okay OK Well Hey Hi Hello Yeah Right What Why How When
Where Who Which This That These Those It It's He She We They You Your My Our Their His Her Mr Mrs Ms Dr Thank Thanks Please
Sorry Look Listen Wait Come Let Let's Just Now Then There Here God Jesus Christ Monday Tuesday Wednesday Thursday Friday
Saturday Sunday January February March April May June July August September October November December Good Great Sure
Not Do Don't Did Is Are Was Were Be Been Can Could Would Should Will Okay Alright All Hmm Uh Um Huh Wow""".split())
_NAME = re.compile(r"\b([A-Z][a-z]{2,})\b")
_SELF = re.compile(r"\b(?:I'm|I am|my name is|this is|it's)\s+([A-Z][a-z]{2,})")


def _names_in(text: str) -> list[str]:
    out = []
    for m in _NAME.finditer(text):
        w = m.group(1)
        if w in _STOP:
            continue
        # skip sentence-initial words unless followed by a comma (vocative: "Ross, come here")
        before = text[: m.start()].rstrip()
        if (not before or before[-1] in ".?!") and not text[m.end(): m.end() + 1] == ",":
            continue
        out.append(w)
    return out


def _extract(video: Path, t: float, dst: Path) -> bool:
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-ss", f"{t:.3f}", "-i", str(video),
                    "-frames:v", "1", "-vf", "scale=768:-2", "-q:v", "3", str(dst)], capture_output=True)
    return dst.exists()


def build(al: dict, diar: dict, video: Path | None, out_dir: Path, lay: dict) -> str:
    lines = al["lines"]
    stats = al["stats"]
    spks = [s for s in sorted(stats, key=lambda k: -stats[k]["talk_s"]) if s != UNKNOWN]
    addressed: dict[str, Counter] = {s: Counter() for s in spks}
    self_intro: dict[str, Counter] = {s: Counter() for s in spks}
    for i, ln in enumerate(lines):
        if ln["spk"] not in addressed:
            continue
        for m in _SELF.finditer(ln["text"]):
            if m.group(1) not in _STOP:
                self_intro[ln["spk"]][m.group(1)] += 1
        if i > 0 and lines[i - 1]["spk"] != ln["spk"] and ln["start"] - lines[i - 1]["end"] <= 3.0:
            for nm in _names_in(lines[i - 1]["text"]):
                addressed[ln["spk"]][nm] += 1
    # voice similarity between IDs (cosine of pyannote speaker embeddings)
    sims = []
    emb = diar.get("embeddings") or {}
    mapped = {al["mapping"].get(raw, raw): np.asarray(v, dtype=np.float32) for raw, v in emb.items()}
    keys = [k for k in spks if k in mapped]
    for a in range(len(keys)):
        for b in range(a + 1, len(keys)):
            x, y = mapped[keys[a]], mapped[keys[b]]
            c = float(x @ y / (np.linalg.norm(x) * np.linalg.norm(y) + 1e-9))
            if c >= 0.5:
                sims.append((c, keys[a], keys[b]))
    sims.sort(reverse=True)

    md = ["# Speaker evidence", "",
          "Use this to map speaker IDs to names. Evidence is not proof: a frame taken while someone talks can show "
          "the listener (reaction shot); a name said just before a line may be the person being addressed OR someone "
          "else. Trust a name only when several signals agree. Several IDs can be one person. Unsure -> leave unnamed.", ""]
    if sims:
        md.append("**Voices that sound alike (possible same person split in two IDs):** " +
                  ", ".join(f"{a}~{b} ({c:.2f})" for c, a, b in sims[:10]))
        md.append("")
    for s in spks:
        st = stats[s]
        own = [ln for ln in lines if ln["spk"] == s]
        md.append(f"## {s} — talk {fmt_dur(st['talk_s'])}, {st['turns']} turns, {st['words']} words, "
                  f"first heard {fmt_ts(st['first']) if st['first'] is not None else '-'}")
        if st.get("likely_not_a_person"):
            md.append("**Probably not a person**: most of this ID's time is laughter/music with no words.")
        if addressed[s]:
            md.append("- Names said by others right before this ID talks: " +
                      ", ".join(f"{n} ×{c}" for n, c in addressed[s].most_common(6)))
        if self_intro[s]:
            md.append("- Self-introductions: " + ", ".join(f"{n} ×{c}" for n, c in self_intro[s].most_common(3)))
        longest = sorted(own, key=lambda ln: ln["end"] - ln["start"], reverse=True)[:5]
        for ln in sorted(longest, key=lambda ln: ln["start"]):
            md.append(f"- [{fmt_ts(ln['start'])}] “{ln['text'][:220]}”")
        solo = [ln for ln in own if not ln.get("uncertain") and not ln.get("overlap") and ln["end"] - ln["start"] >= 1.5]
        solo = sorted(solo, key=lambda ln: ln["end"] - ln["start"], reverse=True)[:3]
        if video is not None and solo:
            tiles = []
            for k, ln in enumerate(sorted(solo, key=lambda ln: ln["start"])):
                t = (ln["start"] + ln["end"]) / 2
                p = out_dir / "img" / f"{s}_{k + 1}.jpg"
                if p.exists() or _extract(video, t, p):
                    tiles.append({"t": t, "path": str(p), "reason": ""})
            if tiles:
                sheet = out_dir / f"{s}.jpg"
                small = dict(lay, cols=len(tiles))
                render_sheet(tiles, f"{s} is talking (alone) in these frames", small, sheet, tag_fn=lambda t: None)
                md.append(f"- Frames while {s} talks alone: `{sheet}`")
        md.append("")
    return "\n".join(md)
