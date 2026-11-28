"""overview.md: the first file the agent reads after prepare."""
from __future__ import annotations

from collections import Counter
from pathlib import Path

from .transcript import Namer, speakers_table
from .util import fmt_dur, fmt_ts


def build(run, probe: dict, intake: dict, hints: dict, sel: dict, plan: dict, chunks: list[dict],
          storyboard: list[dict], al: dict | None, events: list[dict], transcript_path: Path | None,
          evidence_path: Path | None, namer: Namer) -> str:
    v = probe.get("video") or {}
    md = [f"# Overview — {Path(probe['path']).name}", ""]
    md.append(f"- Duration **{fmt_dur(probe['duration'])}** · {v.get('width')}x{v.get('height')} "
              f"@ {v.get('fps') and round(v['fps'], 2)} fps{' (VFR)' if v.get('vfr') else ''} · "
              f"audio streams: {len(probe['audio'])} (using #{intake.get('audio_stream', 0)})")
    md.append(f"- Run dir: `{run.dir}`")
    md.append(f"- Identity guess (filename/tags, NOT confirmed): {hints.get('guess') or '-'}")
    if intake:
        md.append(f"- Intake: visibility **{intake.get('visibility', 'not asked')}** · kind {intake.get('kind', '-')} "
                  f"· identity {intake.get('identity') or '-'} · goal: {intake.get('goal') or '-'}")
    else:
        md.append("- Intake: **not recorded** — treat as PRIVATE (no web search) until the user answers.")
    md.append("")
    md.append("## Pictures")
    md.append(f"- {sel['n_frames']} frames decoded · {len(sel['shots'])} shots · **{len(sel['kept'])} frames kept** "
              f"(base {sel['fps']} fps, heartbeat {sel['heartbeat']:.0f} s, budget {sel['budget']}, sampling x{sel['fps_scale']})")
    tok = sum(c["tokens"] for c in chunks)
    md.append(f"- Mode: **{plan['mode']}** · {plan['total_sheets']} sheets in {len(chunks)} chunk(s) · "
              f"≈{tok // 1000}k image tokens for a full watch (plan for ≈{4 * tok // 1000}k total with "
              f"sub-agent overhead)")
    if storyboard:
        md.append("- Storyboard for the global skim: " + ", ".join(f"`{s['path']}`" for s in storyboard))
    if sel["coverage_gaps"]:
        md.append(f"- Fast-motion spans with few frames ({len(sel['coverage_gaps'])}): " +
                  ", ".join(f"{fmt_ts(g['start'])}–{fmt_ts(g['end'])}" for g in sel["coverage_gaps"][:12]) +
                  " — zoom before making precise claims there.")
    md.append("")
    md.append("## Sound")
    if al is not None:
        md.append(f"- Transcript: `{transcript_path}` · speaker evidence: `{evidence_path}`")
        md.append("")
        md.append(speakers_table(al, namer))
        n_ov = sum(1 for w in al["words"] if "overlap" in (w.get("flags") or []))
        md.append(f"\nOverlap words: {n_ov} · overlap regions: {len(al['overlaps'])}")
    else:
        md.append("- Speaker analysis not done yet (waits for intake).")
    cnt = Counter(e["type"] for e in events)
    if cnt:
        md.append("- Sound events: " + ", ".join(f"{k} ×{n}" for k, n in cnt.most_common()))
    md.append("")
    md.append("## Chunks")
    for c in chunks:
        md.append(f"- {c['id']:02d}: {fmt_ts(c['start'])}–{fmt_ts(c['end'])} · {len(c['sheets'])} sheets "
                  f"· ≈{c['tokens'] // 1000}k tokens · `{c['packet']}`")
    return "\n".join(md) + "\n"
