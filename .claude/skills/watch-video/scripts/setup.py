#!/usr/bin/env python3
"""watch-video setup / preflight. Stdlib only, so it runs with any python3.

  python3 setup.py --check     fast status (no downloads); exit 0 = ready, 1 = something missing
  python3 setup.py             install the env (uv sync), download + warm up the three local models
  python3 setup.py --guard     print the settings.json snippet for the private-video web guard
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
HUB = Path(os.environ.get("HF_HOME", "~/.cache/huggingface")).expanduser() / "hub"
MODELS = {
    "parakeet": "mlx-community/parakeet-tdt-0.6b-v3",
    "ced": "mispeech/ced-tiny",
    "pyannote": "pyannote/speaker-diarization-community-1",
}
PYANNOTE_PAGE = "https://huggingface.co/pyannote/speaker-diarization-community-1"


def cached(repo: str) -> bool:
    snap = HUB / f"models--{repo.replace('/', '--')}" / "snapshots"
    return snap.exists() and any(snap.iterdir())


def hf_token_present() -> bool:
    return bool(os.environ.get("HF_TOKEN")) or (HUB.parent / "token").exists()


def status() -> dict:
    st = {
        "apple_silicon": sys.platform == "darwin" and platform.machine() == "arm64",
        "ffmpeg": shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None,
        "uv": shutil.which("uv") is not None,
        "venv": (SKILL / ".venv" / "bin" / "python").exists(),
        "models": {k: cached(v) for k, v in MODELS.items()},
        "hf_token": hf_token_present(),
        "workflow_linked": (Path("~/.claude/workflows/watch-video-chunks.js").expanduser()).exists(),
    }
    st["ready"] = st["apple_silicon"] and st["ffmpeg"] and st["uv"] and st["venv"] and all(st["models"].values())
    steps = []
    if not st["apple_silicon"]:
        steps.append("This skill needs an Apple Silicon Mac (Parakeet runs on MLX).")
    if not st["ffmpeg"]:
        steps.append("Install ffmpeg: brew install ffmpeg")
    if not st["uv"]:
        steps.append("Install uv: brew install uv")
    if not st["models"]["pyannote"] and not st["hf_token"]:
        steps.append(f"Speaker detection model (one time): open {PYANNOTE_PAGE}, log in, accept the terms; create a "
                     "Read token at https://huggingface.co/settings/tokens; then, in a normal Terminal window (the token prompt is "
                     f"interactive and keeps the token out of the chat), run: {SKILL}/.venv/bin/hf auth login "
                     "(if .venv does not exist yet, run setup.py first; it stops before the speaker model).")
    if not st["venv"] or not all(st["models"].values()):
        steps.append(f"Then run: python3 {SKILL}/scripts/setup.py")
    st["next_steps"] = steps
    return st


WARMUP = r"""
import os, sys, json
sys.path.insert(0, %(scripts)r)
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"; os.environ["PYANNOTE_METRICS_ENABLED"] = "0"
import numpy as np
res = {}
from parakeet_mlx import from_pretrained
from wv.transcribe import MODEL, MODEL_REV
m = from_pretrained(MODEL); res["parakeet"] = "ok"
from transformers import AutoFeatureExtractor, AutoModelForAudioClassification
from wv.audio_events import CED_MODEL, CED_REV
AutoFeatureExtractor.from_pretrained(CED_MODEL, revision=CED_REV, trust_remote_code=True)
AutoModelForAudioClassification.from_pretrained(CED_MODEL, revision=CED_REV, trust_remote_code=True); res["ced"] = "ok"
from silero_vad import load_silero_vad; load_silero_vad(); res["silero"] = "ok"
try:
    from pyannote.audio import Pipeline
    p = Pipeline.from_pretrained("pyannote/speaker-diarization-community-1")
    res["pyannote"] = "ok" if p is not None else "not loaded (accept terms + hf auth login)"
except Exception as e:
    res["pyannote"] = f"failed: {type(e).__name__}: {str(e)[:300]}"
print(json.dumps(res))
"""


WORKFLOWS = Path("~/.claude/workflows").expanduser()


def link_workflow() -> str:
    """Saved workflows live in ~/.claude/workflows/; link ours there so /watch-video can call it by name."""
    WORKFLOWS.mkdir(parents=True, exist_ok=True)
    dst, src = WORKFLOWS / "watch-video-chunks.js", SKILL / "workflows" / "watch_chunks.js"
    if dst.is_symlink() or dst.exists():
        if dst.resolve() == src.resolve():
            return "linked"
        return f"exists (not ours): {dst}"
    dst.symlink_to(src)
    return "linked"


def install() -> int:
    st = status()
    if not (st["apple_silicon"] and st["ffmpeg"] and st["uv"]):
        print(json.dumps(st, indent=1))
        return 1
    print("[setup] uv sync (Python 3.12 env inside the skill folder) ...", file=sys.stderr)
    subprocess.run(["uv", "sync", "--project", str(SKILL)], check=True)
    print("[setup] downloading + warming up models (first time: ~2.5 GB) ...", file=sys.stderr)
    code = WARMUP % {"scripts": str(SKILL / "scripts")}
    r = subprocess.run(["uv", "run", "--project", str(SKILL), "python", "-c", code], capture_output=True, text=True)
    lines = [ln for ln in r.stdout.splitlines() if ln.startswith("{")]
    res = json.loads(lines[-1]) if lines else {"error": r.stderr[-1500:]}
    st = status()
    st["warmup"] = res
    st["workflow"] = link_workflow()
    (SKILL / ".setup_status.json").write_text(json.dumps(st, indent=1))
    print(json.dumps(st, indent=1))
    return 0 if st["ready"] else 1


def guard_snippet() -> dict:
    cmd = f"python3 {SKILL}/hooks/private_guard.py"
    return {"hooks": {"PreToolUse": [{"matcher": "WebSearch|WebFetch|Bash|mcp__.*",
                                      "hooks": [{"type": "command", "command": cmd, "timeout": 5}]}]}}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--guard", action="store_true")
    a = ap.parse_args()
    if a.guard:
        print(json.dumps(guard_snippet(), indent=1))
        sys.exit(0)
    if a.check:
        st = status()
        print(json.dumps(st, indent=1))
        sys.exit(0 if st["ready"] else 1)
    sys.exit(install())
