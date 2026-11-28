"""Independent checks for a chunk scene log. Never trusts the worker's own 'ok'."""
from __future__ import annotations

import json
from pathlib import Path

SCHEMA = Path(__file__).resolve().parents[2] / "references" / "scene_log.schema.json"
TOL = 2.0  # seconds of slack at chunk edges
MIN_SCENE_COVERAGE = 0.8


def validate(log_path: Path, chunk: dict, run_id: str) -> list[str]:
    import jsonschema

    errs: list[str] = []
    if not log_path.exists():
        return [f"missing file {log_path}"]
    try:
        data = json.loads(log_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"not valid JSON: {e}"]
    v = jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text()))
    for e in sorted(v.iter_errors(data), key=lambda e: list(e.path)):
        errs.append(f"schema: {'/'.join(str(p) for p in e.path) or '<root>'}: {e.message}")
    if errs:
        return errs
    s, e = chunk["start"], chunk["end"]
    if data["run_id"] != run_id:
        errs.append(f"run_id {data['run_id']!r} != {run_id!r}")
    if data["chunk_id"] != chunk["id"]:
        errs.append(f"chunk_id {data['chunk_id']} != {chunk['id']}")
    if abs(data["start"] - s) > TOL or abs(data["end"] - e) > TOL:
        errs.append(f"start/end {data['start']}-{data['end']} must be the chunk range {s}-{e}")

    def inside(t, what):
        if not (s - TOL <= t <= e + TOL):
            errs.append(f"{what} time {t} is outside the chunk range {s}-{e}")

    prev_end = None
    covered = 0.0
    for i, sc in enumerate(data["scenes"]):
        inside(sc["start"], f"scenes[{i}].start")
        inside(sc["end"], f"scenes[{i}].end")
        if sc["end"] <= sc["start"]:
            errs.append(f"scenes[{i}] end <= start")
        if prev_end is not None and sc["start"] < prev_end - TOL:
            errs.append(f"scenes[{i}] starts before the previous scene ends (not in time order)")
        prev_end = sc["end"]
        covered += max(0.0, min(e, sc["end"]) - max(s, sc["start"]))
        bad = [r for r in sc["sheet_refs"] if r not in chunk["sheet_ids"]]
        if bad:
            errs.append(f"scenes[{i}].sheet_refs {bad} are not this chunk's sheets {chunk['sheet_ids']}")
    if e - s > 0 and covered / (e - s) < MIN_SCENE_COVERAGE:
        errs.append(f"scenes cover {covered / (e - s):.0%} of the range; need >= {MIN_SCENE_COVERAGE:.0%} (no gaps)")
    seen = {r for sc in data["scenes"] for r in sc["sheet_refs"]}
    unseen = [i for i in chunk["sheet_ids"] if i not in seen]
    if unseen:
        errs.append(f"sheets never referenced by any scene: {unseen} (read every sheet)")
    for k, ev in enumerate(data["events"]):
        inside(ev["t"], f"events[{k}].t")
    for k, q in enumerate(data["quotes"]):
        inside(q["start"], f"quotes[{k}].start")
    for k, h in enumerate(data["highlight_candidates"]):
        inside(h["start"], f"highlight_candidates[{k}].start")
        if h["end"] <= h["start"]:
            errs.append(f"highlight_candidates[{k}] end <= start")
    return errs
