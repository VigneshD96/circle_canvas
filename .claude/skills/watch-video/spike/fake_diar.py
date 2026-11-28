"""Stand-in diarization from fixture truth, to exercise align -> transcript -> evidence -> packets -> overview."""
import json, sys
sys.path.insert(0, "scripts")
from pathlib import Path
from wv.cache import Run
from wv.util import write_json, read_json
from wv import align as AL
from wv.pipeline import build_named

video = Path(sys.argv[1]); truth = json.loads(Path(sys.argv[2]).read_text())
run = Run.for_video(video)
lab = {v: f"SPEAKER_{i:02d}" for i, v in enumerate(sorted({l["voice"] for l in truth["lines"]}))}
turns = [{"start": l["start"] + 0.05, "end": l["speech_end"] + 0.1, "spk": lab[l["voice"]]} for l in truth["lines"]]
write_json(run.p("intake.json"), {"visibility": "private", "kind": "podcast", "goal": "test"})
run.stage("diar", ["audio"], {"fake": True}, ["diar/diar.json"],
          lambda: write_json(run.p("diar", "diar.json"), {"model": "fake", "regular": turns, "exclusive": turns,
                                                          "labels": sorted(lab.values()), "embeddings": None}), force=True)
ev = read_json(run.p("audio", "events.json"))
run.stage("align", ["asr", "diar", "events"], {"fake": True}, ["align/align.json"],
          lambda: write_json(run.p("align", "align.json"),
                             AL.align(read_json(run.p("asr", "words.json"))["words"], read_json(run.p("diar", "diar.json")), ev["events"])),
          force=True)
pr = read_json(run.p("probe.json")); sel = read_json(run.p("video", "selection.json")); plan = read_json(run.p("chunks", "plan.json"))
build_named(run, pr, sel, plan, ev, True)
print(run.dir)
print("mapping", read_json(run.p("align", "align.json"))["mapping"], "truth labels", lab)
