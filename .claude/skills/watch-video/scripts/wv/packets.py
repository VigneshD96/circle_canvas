"""Per-chunk packet.md: the exact inputs a chunk watcher reads (its sheets + transcript slice + context)."""
from __future__ import annotations

from pathlib import Path

from .transcript import LEGEND, Namer, entries
from .util import fmt_ts, write_json

CTX_BEFORE_S, CTX_AFTER_S = 30.0, 10.0


def build(run_id: str, title: str, plan: dict, sheet_index: list[dict], al: dict | None, events: list[dict],
          namer: Namer, loud: list[dict], shots: list[dict], gaps: list[dict], out_root: Path,
          context_imgs: dict[int, dict]) -> list[dict]:
    chunks = plan["chunks"]
    out = []
    for ch in chunks:
        cid, s, e = ch["id"], ch["start"], ch["end"]
        my_sheets = [sh for sh in sheet_index if sh["chunk"] == cid]
        d = out_root / f"{cid:02d}"
        md = [f"# Chunk {cid:02d} of {len(chunks):02d} — {fmt_ts(s)} to {fmt_ts(e)}",
              f"Run `{run_id}` · {title}", "",
              "You own ONLY this time range. Anything marked context is read-only: use it to understand, "
              "do not log scenes for it.", "", "## Sheets (read every one, in order)"]
        for sh in my_sheets:
            md.append(f"- sheet {sh['id']:03d}: `{sh['path']}` ({fmt_ts(sh['start'])}–{fmt_ts(sh['end'])}, "
                      f"{len(sh['tiles'])} frames)")
        ctx = context_imgs.get(cid)
        if ctx:
            md += ["", f"Boundary context image (neighbour chunks): `{ctx['path']}`"]
        cuts = [x["start"] for x in shots if s <= x["start"] < e]
        md += ["", f"Shot cuts in range: {len(cuts)}"]
        g = [x for x in gaps if s <= x["start"] < e]
        if g:
            md.append("Fast-motion spans with few frames (zoom if they matter): " +
                      ", ".join(f"{fmt_ts(x['start'])}–{fmt_ts(x['end'])}" for x in g[:10]))
        if al is not None:
            md += ["", LEGEND, ""]
            prev = entries(al, events, namer, loud, max(0.0, s - CTX_BEFORE_S), s)
            if prev:
                md += ["## Transcript — before your range (context only)"] + [t for _, t in prev] + [""]
            mine = entries(al, events, namer, loud, s, e)
            md += ["## Transcript — YOUR RANGE"] + ([t for _, t in mine] or ["(no speech or events)"]) + [""]
            nxt = entries(al, events, namer, loud, e, e + CTX_AFTER_S)
            if nxt:
                md += ["## Transcript — after your range (context only)"] + [t for _, t in nxt]
        else:
            md += ["", "(transcript not ready yet)"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "packet.md").write_text("\n".join(md) + "\n", encoding="utf-8")
        out.append({"id": cid, "start": s, "end": e, "packet": str(d / "packet.md"),
                    "sheets": [sh["path"] for sh in my_sheets], "sheet_ids": [sh["id"] for sh in my_sheets],
                    "context": ctx["path"] if ctx else None,
                    "tokens": sum(sh["tokens"] for sh in my_sheets) + (ctx["tokens"] if ctx else 0)})
    write_json(out_root / "chunks.json", {"mode": plan["mode"], "chunks": out})
    return out
