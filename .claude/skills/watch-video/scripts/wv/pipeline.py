"""prepare: run every stage (fingerprinted, cached). Media stages need no user answers; diarization waits for intake."""
from __future__ import annotations

import hashlib
import json
import os
import threading
import time
from pathlib import Path

from .cache import FileLock, Run
from .util import log, read_json, write_json

HF_HUB = Path(os.environ.get("HF_HOME", "~/.cache/huggingface")).expanduser() / "hub"
MODELS = ["mlx-community/parakeet-tdt-0.6b-v3", "mispeech/ced-tiny", "pyannote/speaker-diarization-community-1"]


def hf_cached(repo: str) -> bool:
    snap = HF_HUB / f"models--{repo.replace('/', '--')}" / "snapshots"
    return snap.exists() and any(snap.iterdir())


def go_offline_if_cached() -> bool:
    """Privacy + speed: no hub calls once every model is on disk. Must run before huggingface_hub is imported."""
    if all(hf_cached(m) for m in MODELS):
        os.environ["HF_HUB_OFFLINE"] = "1"
        return True
    return False


def names_hash(run: Run) -> str:
    p = run.p("speakers.json")
    return hashlib.sha1(p.read_bytes()).hexdigest()[:12] if p.exists() else ""


def wait_for_intake(run: Run, timeout: float) -> dict:
    t0 = time.time()
    warned = False
    while True:
        it = run.intake()
        if it.get("visibility"):
            return it
        if time.time() - t0 >= timeout:
            log("intake not recorded in time; continuing with automatic speaker count")
            return it
        if not warned:
            log("waiting for intake answers (watch.py intake ...) before speaker detection")
            warned = True
        time.sleep(2)


def prepare(run: Run, phase: str = "all", wait_intake: float = 900, force: set[str] | None = None,
            fps: float | None = None) -> dict:
    force = force or set()
    go_offline_if_cached()
    from . import audio as A
    from . import audio_events as E
    from . import chunks as C
    from . import frames as F
    from . import probe as P
    from . import sheets as S
    from . import transcribe as T

    with FileLock(run.p(".prepare.lock")):
        video = run.video
        run.stage("probe", [], {"src": run.meta["source"]}, ["probe.json"],
                  lambda: write_json(run.p("probe.json"), P.probe(video)), force="probe" in force)
        pr = read_json(run.p("probe.json"))
        intake = run.intake()
        kind = intake.get("kind")
        order = intake.get("audio_stream", P.default_audio_order(pr))
        has_audio, has_video = order is not None, pr["video"] is not None
        if not has_video:
            raise SystemExit("no video stream found; this skill needs a video file")
        errors: list[BaseException] = []

        def audio_track():
            try:
                if not has_audio:
                    return
                from .timeline import audio_offset

                off = audio_offset(pr, order)

                def do_audio():
                    A.extract(video, order, run.p("audio", "audio.wav"))
                    A.loudness(A.load(run.p("audio", "audio.wav")), off, run.p("audio", "loudness.json"))

                run.stage("audio", ["probe"], {"order": order, "offset": off}, ["audio/audio.wav", "audio/loudness.json"],
                          do_audio, force="audio" in force)
                run.stage("asr", ["audio"], {"model": T.MODEL, "rev": T.MODEL_REV, "chunk": T.CHUNK_S, "ov": T.OVERLAP_S, "repair": T.REPAIR_V},
                          ["asr/words.json", "asr/tokens.json"],
                          lambda: T.transcribe(run.p("audio", "audio.wav"), off, run.p("asr", "tokens.json"), run.p("asr", "words.json")),
                          force="asr" in force)
                run.stage("events", ["audio"], {"ced": E.CED_REV, "classes": sorted(E.EVENT_CLASSES), "v": 3}, ["audio/events.json"],
                          lambda: E.run_all(A.load(run.p("audio", "audio.wav")), A.SR, off, run.p("audio", "events.json")),
                          force="events" in force)
            except BaseException as e:  # surfaced after join
                errors.append(e)

        def visual_track():
            try:
                run.stage("scan", ["probe"], {"edge": F.SCAN_LONG_EDGE, "thumb": [F.THUMB_W, F.THUMB_H]}, ["video/scan.npz"],
                          lambda: F.run_scan(video, pr, run.dir), force="scan" in force)
                run.stage("frames", ["scan"], {"fps": fps, "kind": kind, "edge": F.FRAME_LONG_EDGE, "v": 4},
                          ["video/selection.json"], lambda: F.run_select(video, pr, run.dir, fps, kind),
                          force="frames" in force)
            except BaseException as e:
                errors.append(e)

        ta, tv = threading.Thread(target=audio_track), threading.Thread(target=visual_track)
        ta.start(), tv.start()
        ta.join(), tv.join()
        if errors:
            raise errors[0]

        sel = read_json(run.p("video", "selection.json"))
        ev = read_json(run.p("audio", "events.json"), {"speech": [], "events": []}) if has_audio else {"speech": [], "events": []}
        lay = S.layout(pr["video"]["aspect"] or 1.78, kind)
        plan_deps = ["frames"] + (["events"] if has_audio else [])

        run.stage("plan", plan_deps, {"inline": C.INLINE_MAX_SHEETS, "per_chunk": C.SHEETS_PER_CHUNK, "per_sheet": lay["per_sheet"]},
                  ["chunks/plan.json"],
                  lambda: write_json(run.p("chunks", "plan.json"),
                                     C.plan(sel["kept"], sel["shots"], ev["speech"], pr["duration"], lay["per_sheet"])),
                  force="plan" in force)
        plan = read_json(run.p("chunks", "plan.json"))

        def do_sheets():
            index = S.build_sheets(sel["kept"], plan["chunks"], lay, run.p("sheets"))
            sb = S.storyboard(sel["kept"], pr["duration"], lay, run.p("storyboard")) if plan["mode"] == "fanout" else []
            ctx = {}
            chs = plan["chunks"]
            for i, ch in enumerate(chs):
                prev = [k for k in sel["kept"] if chs[i - 1]["start"] <= k["t"] < ch["start"]][-2:] if i > 0 else []
                nxt = [k for k in sel["kept"] if chs[i + 1]["start"] <= k["t"] < chs[i + 1]["end"]][:2] if i + 1 < len(chs) else []
                c = S.context_strip(prev, nxt, lay, run.p("chunks", f"{ch['id']:02d}", "context.jpg"))
                if c:
                    ctx[ch["id"]] = c
            write_json(run.p("sheets", "index.json"), {"layout": lay, "sheets": index, "storyboard": sb, "context": ctx})

        run.stage("sheets", ["plan"], {"layout": lay, "v": 2}, ["sheets/index.json"], do_sheets, force="sheets" in force)

        if phase == "media":
            return summary(run, pr, "media")

        intake = wait_for_intake(run, wait_intake)
        if has_audio:
            from . import align as AL
            from . import diarize as D

            diar_params = {"num": intake.get("speakers"), "min": intake.get("min_speakers"), "max": intake.get("max_speakers"),
                           "model": D.MODEL, "rev": D.MODEL_REV}

            def do_diar():
                D.diarize(A.load(run.p("audio", "audio.wav")), A.SR, read_json(run.p("audio", "loudness.json"))["offset"],
                          run.p("diar", "diar.json"), num_speakers=diar_params["num"], min_speakers=diar_params["min"],
                          max_speakers=diar_params["max"])

            run.stage("diar", ["audio"], diar_params, ["diar/diar.json"], do_diar, force="diar" in force)

            def do_align():
                words = read_json(run.p("asr", "words.json"))["words"]
                diar = read_json(run.p("diar", "diar.json"))
                write_json(run.p("align", "align.json"), AL.align(words, diar, ev["events"]))

            run.stage("align", ["asr", "diar", "events"], {"margin": AL.MARGIN, "near": AL.NEAR_S, "v": 2},
                      ["align/align.json"], do_align, force="align" in force)
        build_named(run, pr, sel, plan, ev, has_audio)
        return summary(run, pr, "all")


def build_named(run: Run, pr: dict, sel: dict, plan: dict, ev: dict, has_audio: bool) -> None:
    """Everything that depends on speaker names: transcript, evidence, packets, overview. Cheap; re-run on naming."""
    from . import evidence as EV
    from . import overview as OV
    from . import packets as PK
    from .audio import loud_spans
    from .identify import hints
    from .transcript import Namer, render

    namer = Namer(read_json(run.p("speakers.json"), {}))
    nh = names_hash(run)
    title = Path(pr["path"]).name
    al_raw = read_json(run.p("align", "align.json")) if has_audio and run.p("align", "align.json").exists() else None
    al = namer.with_overrides(al_raw) if al_raw is not None else None
    loud = loud_spans(read_json(run.p("audio", "loudness.json"), {})) if has_audio else []
    sidx = read_json(run.p("sheets", "index.json"))
    lay = sidx["layout"]
    if al is not None:
        run.stage("transcript", ["align"], {"names": nh, "v": 3}, ["transcript.md"],
                  lambda: run.p("transcript.md").write_text(render(al, ev["events"], namer, loud, title), encoding="utf-8"))
        run.stage("evidence", ["align", "frames"], {"v": 1}, ["speakers/evidence.md"],
                  lambda: run.p("speakers", "evidence.md").write_text(
                      EV.build(al_raw, read_json(run.p("diar", "diar.json")), run.video, run.p("speakers"), lay), encoding="utf-8"))
    pk_deps = ["sheets"] + (["align"] if al is not None else [])
    ctx = {int(k): v for k, v in sidx.get("context", {}).items()}
    run.stage("packets", pk_deps, {"names": nh, "v": 3}, ["chunks/chunks.json"],
              lambda: PK.build(run.run_id, title, plan, sidx["sheets"], al, ev["events"], namer, loud, sel["shots"],
                               sel["coverage_gaps"], run.p("chunks"), ctx))
    chunks = read_json(run.p("chunks", "chunks.json"))["chunks"]
    ov = OV.build(run, pr, run.intake(), hints(pr["path"], pr.get("tags")), sel, plan, chunks, sidx.get("storyboard", []), al_raw,
                  ev["events"], run.p("transcript.md") if al is not None else None,
                  run.p("speakers", "evidence.md") if al is not None else None, namer)
    run.p("overview.md").write_text(ov, encoding="utf-8")


def summary(run: Run, pr: dict, phase: str) -> dict:
    plan = read_json(run.p("chunks", "plan.json"), {})
    sidx = read_json(run.p("sheets", "index.json"), {})
    out = {"run_dir": str(run.dir), "phase_done": phase, "duration": pr["duration"], "mode": plan.get("mode"),
           "sheets": len(sidx.get("sheets", [])), "chunks": len(plan.get("chunks", [])),
           "storyboard": [s["path"] for s in sidx.get("storyboard", [])]}
    if phase == "all":
        out.update({"overview": str(run.p("overview.md")),
                    "transcript": str(run.p("transcript.md")) if run.p("transcript.md").exists() else None,
                    "evidence": str(run.p("speakers", "evidence.md")) if run.p("speakers", "evidence.md").exists() else None,
                    "chunks_json": str(run.p("chunks", "chunks.json"))})
    out["stage_secs"] = {k: v.get("secs") for k, v in run.meta["stages"].items()}
    return out


def dumps(x) -> str:
    return json.dumps(x, indent=1, ensure_ascii=False)


def rebuild_named(run: Run) -> None:
    """Re-render name-dependent files (after name-speakers) without touching media or models."""
    pr = read_json(run.p("probe.json"))
    sel = read_json(run.p("video", "selection.json"))
    plan = read_json(run.p("chunks", "plan.json"))
    has_audio = run.p("audio", "events.json").exists()
    ev = read_json(run.p("audio", "events.json"), {"speech": [], "events": []}) if has_audio else {"speech": [], "events": []}
    build_named(run, pr, sel, plan, ev, has_audio)
