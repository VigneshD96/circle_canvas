import sys, json, time
sys.path.insert(0, "scripts")
from pathlib import Path
import numpy as np
from wv.probe import probe
from wv import frames
v = Path(sys.argv[1]); out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
pr = probe(v); print("probe video:", {k: pr["video"][k] for k in ("width","height","fps","vfr","start_offset")}, "audio:", [(a["order"], a["start_offset"]) for a in pr["audio"]])
t=time.time(); info = frames.scan(v, pr["video"]["width"], pr["video"]["height"], out/"scan.npz"); print("scan", info, f"{time.time()-t:.2f}s")
d = np.load(out/"scan.npz")
sel = frames.select(d["pts"], d["score"], d["dhash"], d["thumbs"], pr["duration"])
print("pts first", d["pts"][:3], "n", len(d["pts"]))
print("shots", len(sel["shots"]), [s["start"] for s in sel["shots"]])
print("kept", len(sel["kept"]), "reasons", {r: sum(1 for k in sel["kept"] if k["reason"]==r) for r in set(k["reason"] for k in sel["kept"])})
print("gaps", sel["coverage_gaps"][:5])
t=time.time(); frames.extract(v, sel["kept"], pr["video"]["width"], pr["video"]["height"], out/"frames"); print("extract", f"{time.time()-t:.2f}s", len(list((out/'frames').glob('*.jpg'))))
