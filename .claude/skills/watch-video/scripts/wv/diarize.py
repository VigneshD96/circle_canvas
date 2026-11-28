"""Speaker diarization with pyannote community-1 (no speaker cap). Audio goes in as an in-memory waveform."""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np

from .util import local_model, log, write_json

MODEL = "pyannote/speaker-diarization-community-1"
MODEL_REV = None  # pinned by setup.py after the first verified download (see references in README)


def _device(prefer: str):
    import torch

    if prefer in ("auto", "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def load_pipeline(device: str = "auto"):
    import torch
    from pyannote.audio import Pipeline

    src = local_model(MODEL, MODEL_REV)
    try:
        pipe = Pipeline.from_pretrained(src) if src != MODEL else Pipeline.from_pretrained(MODEL, revision=MODEL_REV)
    except Exception as e:  # GatedRepoError / 401 when terms not accepted or not logged in
        if "gated" in type(e).__name__.lower() or "401" in str(e) or "restricted" in str(e).lower():
            raise RuntimeError(
                "Speaker detection model is gated. One-time fix for the USER: open "
                "https://huggingface.co/pyannote/speaker-diarization-community-1, log in, accept the terms; create a Read "
                "token at https://huggingface.co/settings/tokens; in a normal Terminal window run "
                "`~/.claude/skills/watch-video/.venv/bin/hf auth login` and paste the token. "
                "Then run prepare again (media stages are cached).") from None
        raise
    if pipe is None:
        raise RuntimeError(
            "Could not load pyannote/speaker-diarization-community-1. Accept the model terms at "
            "https://huggingface.co/pyannote/speaker-diarization-community-1 and run `~/.claude/skills/watch-video/.venv/bin/hf auth login`."
        )
    dev = _device(device)
    pipe.to(dev)
    return pipe, str(dev)


def diarize(y: np.ndarray, sr: int, offset: float, out: Path, num_speakers: int | None = None,
            min_speakers: int | None = None, max_speakers: int | None = None, device: str = "auto") -> dict:
    import torch

    pipe, dev = load_pipeline(device)
    kw = {}
    if num_speakers:
        kw["num_speakers"] = int(num_speakers)
    else:
        if min_speakers:
            kw["min_speakers"] = int(min_speakers)
        if max_speakers:
            kw["max_speakers"] = int(max_speakers)
    wav = {"waveform": torch.from_numpy(np.ascontiguousarray(y, dtype=np.float32))[None, :], "sample_rate": sr}
    try:
        res = pipe(wav, **kw)
    except Exception as e:  # MPS kernels can be missing for some ops; CPU always works
        if dev != "cpu":
            log(f"diarize: {dev} failed ({type(e).__name__}: {e}); retrying on cpu")
            pipe.to(torch.device("cpu"))
            dev = "cpu"
            res = pipe(wav, **kw)
        else:
            raise
    ser = res.serialize()
    labels = list(res.speaker_diarization.labels())

    def conv(items):
        return [{"start": round(t["start"] + offset, 3), "end": round(t["end"] + offset, 3), "spk": t["speaker"]}
                for t in items]

    emb = None
    if getattr(res, "speaker_embeddings", None) is not None:
        emb = {lab: np.asarray(res.speaker_embeddings[i]).round(5).tolist() for i, lab in enumerate(labels)
               if i < len(res.speaker_embeddings)}
    data = {
        "model": MODEL,
        "device": dev,
        "params": kw,
        "regular": conv(ser.get("diarization", [])),
        "exclusive": conv(ser.get("exclusive_diarization", [])),
        "labels": labels,
        "embeddings": emb,
    }
    write_json(out, data)
    return {"speakers": len(labels), "turns": len(data["exclusive"]), "device": dev}


def model_cached() -> bool:
    from huggingface_hub import try_to_load_from_cache

    p = try_to_load_from_cache(MODEL, "config.yaml")
    return isinstance(p, str) and os.path.exists(p)
