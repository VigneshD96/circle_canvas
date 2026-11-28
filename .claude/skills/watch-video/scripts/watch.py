#!/usr/bin/env python3
"""watch-video CLI. Every command prints JSON on stdout; progress goes to stderr.

Run through the skill's own environment:
  uv run --project <skill_dir> python <skill_dir>/scripts/watch.py <command> ...
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from wv.cache import CACHE_ROOT, Run, is_locked, set_active  # noqa: E402
from wv.util import fmt_ts, log, parse_ts, read_json, write_json  # noqa: E402

KINDS = ["sitcom", "tv", "movie", "podcast", "interview", "tutorial", "clip", "meeting", "lecture", "other"]


def out(obj) -> None:
    print(json.dumps(obj, indent=1, ensure_ascii=False, default=str))


def _run(target: str) -> Run:
    return Run.resolve(target)


def _need(run: Run, rel: str, what: str):
    if not run.p(rel).exists():
        raise SystemExit(f"{what} is missing ({rel}); run `watch.py prepare` first")
    return read_json(run.p(rel))


def _edits_dir(run: Run, given: str | None) -> Path:
    if given:
        return Path(given).expanduser()
    d = run.video.parent / f"{run.video.stem}_edits"
    try:
        d.mkdir(parents=True, exist_ok=True)
        probe_file = d / ".write_test"
        probe_file.write_text("x")
        probe_file.unlink()
        return d
    except OSError:
        return run.p("edits")


# ------------------------------------------------------------------ commands
def cmd_hints(a):
    from wv.identify import hints
    from wv.probe import default_audio_order, probe

    run = _run(a.video)
    if not run.p("probe.json").exists():
        write_json(run.p("probe.json"), probe(run.video))
    pr = read_json(run.p("probe.json"))
    v = pr["video"] or {}
    out({
        "run_dir": str(run.dir),
        "file": pr["path"],
        "duration_s": round(pr["duration"], 2),
        "video": {k: v.get(k) for k in ("width", "height", "fps", "vfr", "rotation")} if v else None,
        "audio_streams": [{k: x[k] for k in ("order", "codec", "channels", "language", "title", "default")} for x in pr["audio"]],
        "default_audio_stream": default_audio_order(pr),
        "identity_hints": hints(pr["path"], pr.get("tags")),
        "intake": run.intake() or None,
        "prepared_stages": sorted(run.meta.get("stages", {})),
        "prepare_running": is_locked(run.p(".prepare.lock")),
    })


def cmd_intake(a):
    run = _run(a.video)
    it = run.intake()
    for k in ("visibility", "identity", "kind", "goal", "speakers", "min_speakers", "max_speakers", "audio_stream"):
        v = getattr(a, k)
        if v is not None:
            it[k] = v
    it["updated"] = time.time()
    write_json(run.p("intake.json"), it)
    set_active(run, it.get("visibility", "unsure"), a.session)
    out({"run_dir": str(run.dir), "intake": it, "web_context_allowed": it.get("visibility") == "public"})


def cmd_prepare(a):
    from wv.pipeline import prepare

    run = _run(a.video)
    if is_locked(run.p(".prepare.lock")):
        out({"run_dir": str(run.dir), "status": "already running", "hint": "wait for the running prepare to finish"})
        sys.exit(3)
    force = set(x.strip() for x in (a.force or "").split(",") if x.strip())
    res = prepare(run, phase=a.phase, wait_intake=a.wait_intake, force=force, fps=a.fps)
    out(res)


def cmd_status(a):
    run = _run(a.video)
    chunks = read_json(run.p("chunks", "chunks.json"), {}).get("chunks", [])
    logs = sorted(p.name for p in run.p("scene_logs").glob("chunk_*.json")) if run.p("scene_logs").exists() else []
    out({"run_dir": str(run.dir), "intake": run.intake(), "prepare_running": is_locked(run.p(".prepare.lock")),
         "stages": {k: {"secs": v.get("secs"), "at": v.get("at")} for k, v in run.meta.get("stages", {}).items()},
         "chunks": len(chunks), "scene_logs": logs,
         "files": {n: run.p(n).exists() for n in ("overview.md", "transcript.md", "speakers/evidence.md", "speakers.json",
                                                    "brief.md", "context/web_context.md", "timeline.md", "video_understanding.md")}})


def _apply_map(run: Run, data: dict) -> dict:
    """Validate a speaker map, keep its source form in <run_dir>/speakers.map.json, resolve phrase overrides
    into speakers.json, and rebuild everything that depends on names."""
    from wv.pipeline import rebuild_named
    from wv.transcript import resolve_overrides

    if is_locked(run.p(".prepare.lock")):
        raise SystemExit("prepare is still running; name speakers after it finishes")
    al = _need(run, "align/align.json", "speaker alignment")
    if "speakers" not in data:
        data = {"speakers": data}
    sp = {}
    for k, v in data["speakers"].items():
        sp[k] = {"name": v, "confidence": "medium", "evidence": ""} if isinstance(v, str) else v
        if sp[k].get("confidence") not in ("high", "medium", "low"):
            raise SystemExit(f"{k}: confidence must be high | medium | low")
    src = {"speakers": sp, "overrides": data.get("overrides", [])}
    write_json(run.p("speakers.map.json"), src)
    resolved, problems = resolve_overrides(al["words"], src["overrides"])
    write_json(run.p("speakers.json"), {"speakers": sp, "overrides": resolved})
    rebuild_named(run)
    return {"speakers": sp, "overrides": len(resolved), "override_problems": problems,
            "map_file": str(run.p("speakers.map.json")), "transcript": str(run.p("transcript.md")),
            "packets": str(run.p("chunks", "chunks.json"))}


def _json_arg(value: str):
    """Inline JSON or a JSON file path. Inline is checked first: Path(...).exists() on a long inline string
    raises OSError (File name too long) for anything over 255 bytes (seen 2026-10-03 with a 2-speaker map)."""
    if value.lstrip().startswith(("{", "[")):
        return json.loads(value)
    return json.loads(Path(value).expanduser().read_text())


def cmd_name_speakers(a):
    run = _run(a.video)
    out(_apply_map(run, _json_arg(a.map)))


def cmd_speaker_fixes(a):
    from wv.transcript import resolve_overrides

    run = _run(a.video)
    tl = _need(run, "timeline.json", "merged scene logs")
    al = _need(run, "align/align.json", "speaker alignment")
    fixes = tl.get("speaker_fixes", [])
    mp = read_json(run.p("speakers.map.json")) or {"speakers": (read_json(run.p("speakers.json"), {}) or {}).get("speakers", {}),
                                                   "overrides": []}
    have = {((o.get("text") or "").lower(), o.get("name"), round(float(o.get("t", -9)))) for o in mp.get("overrides", [])}
    skip = {int(x) for x in (a.skip or "").split(",") if x.strip()}
    rows, new = [], []
    for k, f in enumerate(fixes):
        res, prob = resolve_overrides(al["words"], [f])
        dup = ((f["text"].lower(), f["name"], round(float(f["t"]))) in have)
        rows.append({"i": k, "t": f["t"], "text": f["text"], "name": f["name"], "found": not prob, "duplicate": dup,
                     "skipped": k in skip, "why": f.get("why", "")[:160]})
        if not prob and not dup and k not in skip:
            new.append({"text": f["text"], "t": f["t"], "name": f["name"], "why": f.get("why", "")[:200]})
    res = {"fixes": rows, "to_add": len(new)}
    if a.apply and new:
        mp["overrides"] = mp.get("overrides", []) + new
        res["applied"] = _apply_map(run, mp)
    out(res)


def cmd_zoom(a):
    from wv.zoom import zoom

    run = _run(a.video)
    pr = _need(run, "probe.json", "probe")
    res = zoom(run.video, run.p("zoom"), parse_ts(a.start), parse_ts(a.end), fps=a.fps, width=a.width, crop=a.crop,
               sheet=not a.no_sheet, aspect=(pr["video"] or {}).get("aspect") or 1.78)
    out(res)


def cmd_workflow_args(a):
    run = _run(a.video)
    chunks = _need(run, "chunks/chunks.json", "chunk plan")["chunks"]
    brief = run.p("brief.md")
    out({"run_dir": str(run.dir), "run_id": run.run_id, "skill_dir": str(Path(__file__).resolve().parents[1]),
         "brief_path": str(brief), "brief_exists": brief.exists(),
         "chunks": [{"id": c["id"], "start": c["start"], "end": c["end"], "sheets": [c["sheet_ids"][0], c["sheet_ids"][-1]],
                     "tokens": c["tokens"]} for c in chunks]})


def cmd_validate_log(a):
    from wv.validate import validate

    run = _run(a.video)
    chunks = {c["id"]: c for c in _need(run, "chunks/chunks.json", "chunk plan")["chunks"]}
    if a.chunk not in chunks:
        raise SystemExit(f"no chunk {a.chunk}; chunks are {sorted(chunks)}")
    path = Path(a.file) if a.file else run.p("scene_logs", f"chunk_{a.chunk:02d}.json")
    errs = validate(path, chunks[a.chunk], run.run_id)
    out({"chunk": a.chunk, "file": str(path), "ok": not errs, "errors": errs})
    sys.exit(0 if not errs else 1)


def cmd_merge(a):
    from wv.merge import merge

    run = _run(a.video)
    chunks = _need(run, "chunks/chunks.json", "chunk plan")["chunks"]
    res = merge(run.dir, run.run_id, chunks)
    out(res)
    sys.exit(0 if res["ok"] else 2)


def _frame_pts(run: Run) -> list[float]:
    import numpy as np

    p = run.p("video", "scan.npz")
    return np.load(p)["pts"].tolist() if p.exists() else []


def _shot_cuts(run: Run) -> list[float]:
    sel = read_json(run.p("video", "selection.json"), {}) or {}
    return [x["start"] for x in sel.get("shots", [])[1:]]


def _speech(run: Run) -> list[dict] | None:
    ev = read_json(run.p("audio", "events.json"))
    return ev["speech"] if ev else None


def _words(run: Run) -> list[dict]:
    al = read_json(run.p("align", "align.json"))
    if al:
        return al["words"]
    w = read_json(run.p("asr", "words.json"))
    return w["words"] if w else []


def _render_and_verify(run: Run, segs, notes, mode, name, out_dir, fast_copy, verify, leakage, words):
    from wv import edit as ED
    from wv.probe import default_audio_order
    from wv.verify import check_output

    pr = read_json(run.p("probe.json"))
    order = run.intake().get("audio_stream", default_audio_order(pr))
    outs = ED.render(run.video, segs, out_dir, name, mode, has_audio=order is not None, a_order=order or 0, fast_copy=fast_copy)
    rec = out_dir / f"{name}.edl.json"
    ED.write_edl_record(rec, run.video, segs, mode, outs, notes, fast_copy)
    res = {"outputs": outs, "record": str(rec), "segments": len(segs),
           "total_s": round(sum(s["end"] - s["start"] for s in segs), 2), "notes": notes,
           "approximate_cuts": fast_copy}
    if verify:
        if mode == "separate":
            res["verify"] = [check_output(Path(o), [s], words) for o, s in zip(outs, segs)]
        else:
            res["verify"] = check_output(Path(outs[0]), segs, words, leakage=leakage)
    return res


def cmd_cut(a):
    from wv import edit as ED

    run = _run(a.video)
    pr = _need(run, "probe.json", "probe")
    edl = ED.load_edl(a.edl)
    mode = "separate" if a.separate else edl.get("mode", "join")
    order = a.order or edl.get("order", "time")
    segs, warn = ED.validate_edl(edl["segments"], pr["duration"], order=order, merge=(mode == "join"))
    words = _words(run)
    notes = list(warn)
    if not a.no_snap and not a.fast_copy:
        segs, sn = ED.snap_edges(segs, words, _frame_pts(run), cuts=_shot_cuts(run), speech=_speech(run))
        notes += sn
    elif not a.fast_copy:  # exact edges given: still align to the frame grid so audio and video lengths match
        segs = ED.frame_align(segs, _frame_pts(run))
    name = a.name or f"{run.video.stem}_cut"
    out(_render_and_verify(run, segs, notes, mode, name, _edits_dir(run, a.out_dir), a.fast_copy, not a.no_verify,
                           False, words))


def cmd_speaker_only(a):
    from wv import edit as ED
    from wv.transcript import Namer

    run = _run(a.video)
    al = _need(run, "align/align.json", "speaker alignment")
    namer = Namer(read_json(run.p("speakers.json"), {}))
    rel = namer.relabel(al)
    labels = {w["spk"] for w in rel["words"]}
    targets = set()
    for who in a.speaker:
        w = who.strip()
        targets |= {lab for lab in labels if lab.lower() == w.lower()}
        if w.upper() in al["stats"]:  # an ID was given: use its effective label
            targets.add(namer.label(w.upper()))
    if not targets:
        raise SystemExit(f"no speaker matches {a.speaker}; labels in this video: {sorted(labels)} (name them with name-speakers)")
    ids = {k for k, v in namer.map.items() if (v.get("name") or k) in targets} | {t for t in targets if t in al["stats"]}
    low = sorted(k for k in ids if (namer.map.get(k) or {}).get("confidence") not in (None, "high"))
    segs, rep = ED.speaker_segments(rel, targets, overlap=a.overlap, strict=a.strict)
    rep["overrides_used"] = len(namer.overrides)
    segs, sn = ED.snap_edges(segs, rel["words"], _frame_pts(run), keep_ids=targets, cuts=_shot_cuts(run), speech=_speech(run))
    label = "_".join(sorted(a.speaker)).replace(" ", "")
    name = a.name or f"{run.video.stem}_{label}_only"
    od = _edits_dir(run, a.out_dir)
    od.mkdir(parents=True, exist_ok=True)
    edl_path = od / f"{name}.proposed.edl.json"
    write_json(edl_path, {"mode": "join", "order": "time", "segments": segs, "report": rep})
    res = {"targets": sorted(targets), "speaker_ids": sorted(ids), "names_not_high_confidence": low, "report": rep, "edl": str(edl_path),
           "preview": [f"{fmt_ts(s['start'])}-{fmt_ts(s['end'])}" for s in segs[:12]], "snap_notes": sn}
    if a.render:
        res.update(_render_and_verify(run, segs, sn, "join", name, od, False, not a.no_verify, a.leakage, rel["words"]))
    out(res)


def cmd_scenes(a):
    from wv import scenes as SC
    from wv.transcript import Namer

    run = _run(a.video)
    pr = _need(run, "probe.json", "probe")
    tl = _need(run, "timeline.json", "merged scene logs (watch the video and run merge first)")
    al = _need(run, "align/align.json", "speaker alignment")
    namer = Namer(read_json(run.p("speakers.json"), {}))
    rel = namer.relabel(al)
    known = set()
    for v in list(namer.map.values()) + namer.overrides:
        nm = (v.get("name") or "").strip()
        if nm:
            known |= {nm, nm.split(" (")[0], nm.split()[0]}
    scenes = [sc for d in tl["chunks"] for sc in d["scenes"]]
    res = SC.select(scenes, rel["words"], a.who, sorted(known), _shot_cuts(run), pr["duration"])
    if not res["segments"]:
        raise SystemExit(f"no scene found with {a.who!r} on screen or speaking")
    name = a.name or f"{run.video.stem}_{a.who.replace(' ', '')}_scenes"
    od = _edits_dir(run, a.out_dir)
    od.mkdir(parents=True, exist_ok=True)
    edl_path = od / f"{name}.proposed.edl.json"
    write_json(edl_path, {"mode": "join", "order": "time", "segments": res["segments"]})
    edges = SC.edge_sheets(run.video, res["segments"], run.p("edges", name), (pr["video"] or {}).get("aspect") or 1.78)
    out_res = {"who": a.who, "edge_check_sheets": [e["sheet"] for e in edges], "segments": len(res["segments"]), "seconds": res["seconds"], "edl": str(edl_path),
               "kept": [f"{fmt_ts(x['start'])}-{fmt_ts(x['end'])} {x['label']} [{'; '.join(x['edge_method'])}]"
                        for x in res["segments"]],
               "dropped_scenes": [f"{fmt_ts(x['start'])}-{fmt_ts(x['end'])} {x['setting'][:60]}" for x in res["dropped_scenes"]]}
    if a.render:
        from wv import edit as ED

        segs, warn = ED.validate_edl(res["segments"], pr["duration"])
        out_res.update(_render_and_verify(run, segs, warn, "join", name, od, False, not a.no_verify, False, rel["words"]))
    out(out_res)


def cmd_verify_edit(a):
    from wv.verify import check_output

    run = _run(a.video)
    rec = read_json(Path(a.record).expanduser())
    segs = rec["segments"]
    words = _words(run)
    if rec["mode"] == "separate":
        res = [check_output(Path(o), [s], words) for o, s in zip(rec["outputs"], segs)]
    else:
        res = check_output(Path(rec["outputs"][0]), segs, words, leakage=a.leakage)
    out(res)


def cmd_release(a):
    from wv.cache import ACTIVE_MARKER

    data = read_json(ACTIVE_MARKER, {}) or {}
    sessions = data.get("sessions", {})
    gone = sessions.pop(a.session or "_any", None)
    write_json(ACTIVE_MARKER, {"sessions": sessions})
    out({"released": bool(gone), "session": a.session or "_any"})


def cmd_clean(a):
    removed, kept = [], []
    if a.run:
        targets = [Path(a.run).expanduser()]
    else:
        cutoff = time.time() - a.older_than * 86400
        targets = [d for d in CACHE_ROOT.iterdir() if d.is_dir() and (d / "meta.json").exists()
                   and (d / "meta.json").stat().st_mtime < cutoff] if CACHE_ROOT.exists() else []
    for d in targets:
        if is_locked(d / ".prepare.lock"):
            kept.append(str(d))
            continue
        if not a.dry_run:
            shutil.rmtree(d, ignore_errors=True)
        removed.append(str(d))
    out({"removed" if not a.dry_run else "would_remove": removed, "skipped_running": kept})


def main(argv=None):
    ap = argparse.ArgumentParser(prog="watch.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("hints", help="fast probe + identity guess (<1 s)")
    p.add_argument("video")
    p.set_defaults(fn=cmd_hints)

    p = sub.add_parser("intake", help="record the user's answers (visibility gates web search)")
    p.add_argument("video")
    p.add_argument("--visibility", choices=["public", "private", "unsure"])
    p.add_argument("--identity")
    p.add_argument("--kind", choices=KINDS)
    p.add_argument("--goal")
    p.add_argument("--speakers", type=int)
    p.add_argument("--min-speakers", dest="min_speakers", type=int)
    p.add_argument("--max-speakers", dest="max_speakers", type=int)
    p.add_argument("--audio-stream", dest="audio_stream", type=int)
    p.add_argument("--session", help="Claude session id (${CLAUDE_SESSION_ID}) so the web guard is per-session")
    p.set_defaults(fn=cmd_intake)

    p = sub.add_parser("prepare", help="run all heavy stages (cached)")
    p.add_argument("video")
    p.add_argument("--phase", choices=["media", "all"], default="all")
    p.add_argument("--wait-intake", type=float, default=900, help="seconds to wait for intake before diarization")
    p.add_argument("--force", help="comma list of stages to redo (probe,audio,asr,events,scan,frames,plan,sheets,diar,align)")
    p.add_argument("--fps", type=float, help="override base sampling fps")
    p.set_defaults(fn=cmd_prepare)

    p = sub.add_parser("status")
    p.add_argument("video")
    p.set_defaults(fn=cmd_status)

    p = sub.add_parser("name-speakers", help='map IDs to names: {"S1":{"name":"Ross","confidence":"high","evidence":"..."}}')
    p.add_argument("video")
    p.add_argument("--map", required=True, help="JSON file or inline JSON")
    p.set_defaults(fn=cmd_name_speakers)

    p = sub.add_parser("speaker-fixes", help="list (and --apply) the watchers' machine-readable label fixes")
    p.add_argument("video")
    p.add_argument("--apply", action="store_true")
    p.add_argument("--skip", help="comma list of fix indexes not to apply")
    p.set_defaults(fn=cmd_speaker_fixes)

    p = sub.add_parser("zoom", help="dense full-res frames for a time range")
    p.add_argument("video")
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    p.add_argument("--fps", type=float, default=2.0)
    p.add_argument("--width", type=int, default=1280)
    p.add_argument("--crop", help="x,y,w,h in source pixels")
    p.add_argument("--no-sheet", action="store_true")
    p.set_defaults(fn=cmd_zoom)

    p = sub.add_parser("workflow-args", help="compact args for workflows/watch_chunks.js")
    p.add_argument("video")
    p.set_defaults(fn=cmd_workflow_args)

    p = sub.add_parser("validate-log", help="check one chunk scene log")
    p.add_argument("video")
    p.add_argument("--chunk", type=int, required=True)
    p.add_argument("--file")
    p.set_defaults(fn=cmd_validate_log)

    p = sub.add_parser("merge", help="validate all scene logs and build timeline.md")
    p.add_argument("video")
    p.set_defaults(fn=cmd_merge)

    p = sub.add_parser("cut", help="render an EDL (plain cuts)")
    p.add_argument("video")
    p.add_argument("--edl", required=True, help='JSON file or inline JSON: {"segments":[{"start":..,"end":..,"label":..,"reason":..}]}')
    p.add_argument("--separate", action="store_true", help="one file per segment (default: join)")
    p.add_argument("--order", choices=["time", "given"], help="join in time order (default) or EDL order")
    p.add_argument("--no-snap", action="store_true")
    p.add_argument("--fast-copy", action="store_true", help="keyframe stream copy: fast but APPROXIMATE cut points")
    p.add_argument("--no-verify", action="store_true")
    p.add_argument("--out-dir")
    p.add_argument("--name")
    p.set_defaults(fn=cmd_cut)

    p = sub.add_parser("speaker-only", help="EDL (and optional render) of one or more speakers' lines")
    p.add_argument("video")
    p.add_argument("--speaker", action="append", required=True, help="name or ID; repeat for several")
    p.add_argument("--overlap", choices=["keep", "drop"], default="keep")
    p.add_argument("--strict", action="store_true", help="drop words whose speaker is uncertain")
    p.add_argument("--render", action="store_true")
    p.add_argument("--leakage", action="store_true", help="diarize the output to check for other voices")
    p.add_argument("--no-verify", action="store_true")
    p.add_argument("--out-dir")
    p.add_argument("--name")
    p.set_defaults(fn=cmd_speaker_only)

    p = sub.add_parser("scenes", help="every scene a person takes part in (with everyone they talk to)")
    p.add_argument("video")
    p.add_argument("--who", required=True, help="name as used in speakers.json (e.g. Chandler)")
    p.add_argument("--render", action="store_true")
    p.add_argument("--no-verify", action="store_true")
    p.add_argument("--out-dir")
    p.add_argument("--name")
    p.set_defaults(fn=cmd_scenes)

    p = sub.add_parser("verify-edit")
    p.add_argument("video")
    p.add_argument("--record", required=True, help="the .edl.json written next to the output")
    p.add_argument("--leakage", action="store_true")
    p.set_defaults(fn=cmd_verify_edit)

    p = sub.add_parser("release", help="end the private-video web guard for a session")
    p.add_argument("--session")
    p.set_defaults(fn=cmd_release)

    p = sub.add_parser("clean", help="delete old run caches")
    p.add_argument("--older-than", type=float, default=30, help="days")
    p.add_argument("--run")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(fn=cmd_clean)

    a = ap.parse_args(argv)
    try:
        a.fn(a)
    except (RuntimeError, FileNotFoundError, ValueError) as e:
        out({"error": str(e), "command": a.cmd})
        sys.exit(1)


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    main()
