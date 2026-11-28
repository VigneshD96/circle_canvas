"""Audio extraction + loudness. The wav's sample 0 sits at `offset` seconds on the master timeline."""
from __future__ import annotations

from pathlib import Path

import numpy as np

from .util import run, write_json

SR = 16000


def extract(video: Path, order: int, out_wav: Path) -> None:
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_wav.with_suffix(".tmp.wav")
    run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", str(video), "-map", f"0:a:{order}",
         "-vn", "-ac", "1", "-ar", str(SR), "-c:a", "pcm_f32le", str(tmp)])
    tmp.replace(out_wav)


def load(wav: Path) -> np.ndarray:
    import soundfile as sf

    y, sr = sf.read(str(wav), dtype="float32")
    assert sr == SR, sr
    return y


def loudness(y: np.ndarray, offset: float, out: Path, step: float = 0.5) -> dict:
    """RMS dBFS per `step` seconds + a loud threshold (85th percentile of speech-level frames)."""
    n = int(SR * step)
    frames = len(y) // n
    if frames == 0:
        write_json(out, {"step": step, "offset": offset, "db": [], "loud_db": None, "silence_db": -50.0})
        return {}
    rms = np.sqrt(np.mean(y[: frames * n].reshape(frames, n) ** 2, axis=1) + 1e-12)
    db = np.round(20 * np.log10(rms), 1)
    active = db[db > -45]
    loud = float(np.percentile(active, 90)) if len(active) > 10 else None
    data = {"step": step, "offset": offset, "db": db.tolist(), "loud_db": loud, "silence_db": -50.0}
    write_json(out, data)
    return data


def loud_spans(ld: dict, min_len: float = 1.0) -> list[dict]:
    """Spans where loudness stays at/above the 90th percentile for >= min_len seconds."""
    if not ld.get("db") or ld.get("loud_db") is None:
        return []
    step, off, thr = ld["step"], ld["offset"], ld["loud_db"]
    spans, start = [], None
    for i, v in enumerate(ld["db"] + [-120.0]):
        if v >= thr and start is None:
            start = i
        elif v < thr and start is not None:
            if (i - start) * step >= min_len:
                spans.append({"start": round(off + start * step, 2), "end": round(off + i * step, 2)})
            start = None
    return spans
