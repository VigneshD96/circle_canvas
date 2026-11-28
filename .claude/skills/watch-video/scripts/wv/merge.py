"""Merge validated chunk scene logs into timeline.md / timeline.json."""
from __future__ import annotations

import json
from pathlib import Path

from .util import fmt_ts, write_json
from .validate import validate


def merge(run_dir: Path, run_id: str, chunks: list[dict]) -> dict:
    logs, failed = [], []
    for ch in chunks:
        p = run_dir / "scene_logs" / f"chunk_{ch['id']:02d}.json"
        errs = validate(p, ch, run_id)
        if errs:
            failed.append({"chunk": ch["id"], "path": str(p), "errors": errs[:8]})
        else:
            logs.append(json.loads(p.read_text(encoding="utf-8")))
    logs.sort(key=lambda d: d["chunk_id"])
    md = ["# Timeline (merged scene logs)", ""]
    if failed:
        md += ["**Missing or invalid chunks** (re-run them): " +
               ", ".join(f"{f['chunk']:02d}" for f in failed), ""]
    highlights, quotes, notes, unsure = [], [], [], []
    for d in logs:
        md.append(f"## Chunk {d['chunk_id']:02d} · {fmt_ts(d['start'])}–{fmt_ts(d['end'])}")
        md.append(d["summary"])
        md.append("")
        for sc in d["scenes"]:
            cont = " (continues from previous chunk)" if sc.get("continues_from_prev") else ""
            md.append(f"- **{fmt_ts(sc['start'])}–{fmt_ts(sc['end'])}** · {sc['setting']}{cont} · "
                      f"on screen: {', '.join(sc['on_screen']) or '-'}")
            md.append(f"  {sc['what_happens']}")
            if sc.get("visual_details"):
                md.append(f"  Visual: {sc['visual_details']}")
            if sc.get("on_screen_text"):
                md.append(f"  Text on screen: {sc['on_screen_text']}")
        key = [e for e in d["events"] if e["importance"] >= 3]
        if key:
            md.append("")
            md.append("Key events: " + "; ".join(f"{fmt_ts(e['t'])} {e['type']}: {e['description']}" for e in key))
        if d.get("changes_over_time"):
            md.append(f"\nChanges over time: {d['changes_over_time']}")
        if d.get("goal_notes"):
            md.append(f"\nFor the user's goal: {d['goal_notes']}")
        md.append("")
        highlights += d["highlight_candidates"]
        quotes += d["quotes"]
        notes += [dict(n, chunk=d["chunk_id"]) for n in d["speaker_notes"]]
        unsure += [f"chunk {d['chunk_id']:02d}: {u}" for u in d["uncertain"]]
    if highlights:
        md += ["## Highlight candidates (agent rank, 5 = strongest)"]
        for h in sorted(highlights, key=lambda h: (-h["rank"], h["start"])):
            md.append(f"- [{h['rank']}] {fmt_ts(h['start'])}–{fmt_ts(h['end'])} **{h['title']}**"
                      f"{'' if h['standalone'] else ' (needs context)'} — {h['why']}")
        md.append("")
    if notes:
        md += ["## Speaker notes from watchers"] + [
            f"- {n['id']}{' = ' + n['name'] if n.get('name') else ''}: {n['evidence']}"
            f"{' — POSSIBLE ERROR: ' + n['possible_error'] if n.get('possible_error') else ''}" for n in notes] + [""]
    if unsure:
        md += ["## Open questions"] + [f"- {u}" for u in unsure] + [""]
    (run_dir / "timeline.md").write_text("\n".join(md), encoding="utf-8")
    fixes = [dict(n["fix"], why=n.get("evidence", ""), chunk=n["chunk"]) for n in notes if n.get("fix")]
    write_json(run_dir / "timeline.json", {"chunks": logs, "highlights": highlights, "quotes": quotes,
                                           "speaker_notes": notes, "speaker_fixes": fixes, "uncertain": unsure,
                                           "failed": failed})
    return {"ok": not failed, "merged": len(logs), "failed": failed, "timeline": str(run_dir / "timeline.md"),
            "speaker_fixes": len(fixes)}
