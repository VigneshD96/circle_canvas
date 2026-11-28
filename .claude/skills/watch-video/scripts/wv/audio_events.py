"""Speech spans (silero-vad) and sound events (CED-tiny: laughter, applause, music, ...).

CED-tiny outputs per-class probabilities (already sigmoid). We score 1 s windows with a 0.5 s hop,
smooth with a 3-window median, threshold per class, and merge runs into spans. Event boundaries are
approximate (about +-0.5 s) and several labels may overlap.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from .util import local_model, write_json

CED_MODEL = "mispeech/ced-tiny"
CED_REV = "ace276d29dd0bb3f3517b0fa8cf300738c409019"
WIN_S, HOP_S = 1.0, 0.5

# label in AudioSet ontology -> (our tag, threshold, min span seconds)
EVENT_CLASSES = {
    # A sitcom laugh track scores mostly as "Snicker"/"Chuckle", rarely as "Laughter": take the family max.
    "Laughter": ("LAUGHTER", 0.15, 0.5),
    "Giggle": ("LAUGHTER", 0.15, 0.5),
    "Chuckle, chortle": ("LAUGHTER", 0.15, 0.5),
    "Belly laugh": ("LAUGHTER", 0.15, 0.5),
    "Snicker": ("LAUGHTER", 0.15, 0.5),
    "Applause": ("APPLAUSE", 0.25, 0.5),
    "Clapping": ("APPLAUSE", 0.3, 0.5),
    "Cheering": ("CHEERING", 0.25, 0.5),
    "Crowd": ("CROWD", 0.4, 1.0),
    "Music": ("MUSIC", 0.40, 1.5),
    "Singing": ("SINGING", 0.40, 1.0),
    "Screaming": ("SCREAM", 0.30, 0.5),
    "Crying, sobbing": ("CRYING", 0.30, 0.5),
    "Gasp": ("GASP", 0.40, 0.3),
    "Doorbell": ("DOORBELL", 0.40, 0.3),
    "Telephone bell ringing": ("PHONE", 0.40, 0.5),
    "Siren": ("SIREN", 0.40, 0.5),
    "Car": ("CAR", 0.50, 1.0),
    "Explosion": ("EXPLOSION", 0.40, 0.3),
    "Gunshot, gunfire": ("GUNSHOT", 0.40, 0.2),
    "Dog": ("DOG", 0.40, 0.5),
}


def vad(y: np.ndarray, sr: int, offset: float) -> list[dict]:
    import torch
    from silero_vad import get_speech_timestamps, load_silero_vad

    model = load_silero_vad()
    spans = get_speech_timestamps(torch.from_numpy(y), model, sampling_rate=sr, return_seconds=True)
    return [{"start": round(s["start"] + offset, 2), "end": round(s["end"] + offset, 2)} for s in spans]


def _runs_to_spans(mask: np.ndarray, probs: np.ndarray, offset: float, min_len: float) -> list[dict]:
    spans, i, n = [], 0, len(mask)
    while i < n:
        if not mask[i]:
            i += 1
            continue
        j = i
        while j + 1 < n and mask[j + 1]:
            j += 1
        start, end = i * HOP_S, j * HOP_S + WIN_S
        if end - start >= min_len:
            spans.append({"start": round(start + offset, 2), "end": round(end + offset, 2),
                          "peak": round(float(probs[i:j + 1].max()), 2)})
        i = j + 1
    return spans


def ced_events(y: np.ndarray, sr: int, offset: float, batch: int = 64) -> list[dict]:
    import torch
    from transformers import AutoFeatureExtractor, AutoModelForAudioClassification

    src = local_model(CED_MODEL, CED_REV)
    kw = {} if src != CED_MODEL else {"revision": CED_REV}
    fe = AutoFeatureExtractor.from_pretrained(src, trust_remote_code=True, **kw)
    model = AutoModelForAudioClassification.from_pretrained(src, trust_remote_code=True, **kw).eval()
    win, hop = int(WIN_S * sr), int(HOP_S * sr)
    if len(y) < win:
        y = np.pad(y, (0, win - len(y)))
    starts = list(range(0, len(y) - win + 1, hop))
    label2id = {v: int(k) for k, v in model.config.id2label.items()}
    cls_ids = {name: label2id[name] for name in EVENT_CLASSES if name in label2id}
    out = np.zeros((len(starts), len(cls_ids)), dtype=np.float32)
    cols = list(cls_ids.values())
    with torch.inference_mode():
        for b in range(0, len(starts), batch):
            chunk = [y[s:s + win] for s in starts[b:b + batch]]
            x = fe(chunk, sampling_rate=sr, return_tensors="pt")
            probs = model(**x).logits  # CED returns sigmoid probabilities
            out[b:b + len(chunk)] = probs[:, cols].numpy()
    # 3-window median smoothing, only for long events (music, crowd); short bursts such as a laugh-track
    # laugh or a gasp often fill a single 1 s window and would be erased by it
    if len(out) >= 3:
        padded = np.pad(out, ((1, 1), (0, 0)), mode="edge")
        smooth = np.median(np.stack([padded[:-2], padded[1:-1], padded[2:]]), axis=0)
        long_cols = [k for k, name in enumerate(cls_ids) if EVENT_CLASSES[name][2] >= 1.0]
        out[:, long_cols] = smooth[:, long_cols]
    # merge classes that share a tag (max), then threshold
    by_tag: dict[str, tuple[np.ndarray, float, float]] = {}
    for k, name in enumerate(cls_ids):
        tag, thr, min_len = EVENT_CLASSES[name]
        if tag in by_tag:
            prev, pthr, pmin = by_tag[tag]
            by_tag[tag] = (np.maximum(prev, out[:, k]), min(pthr, thr), min(pmin, min_len))
        else:
            by_tag[tag] = (out[:, k].copy(), thr, min_len)
    events = []
    for tag, (p, thr, min_len) in by_tag.items():
        for s in _runs_to_spans(p >= thr, p, offset, min_len):
            events.append({"type": tag, **s})
    events.sort(key=lambda e: e["start"])
    return events


def run_all(y: np.ndarray, sr: int, offset: float, out: Path) -> dict:
    speech = vad(y, sr, offset)
    events = ced_events(y, sr, offset)
    write_json(out, {"speech": speech, "events": events, "ced_model": CED_MODEL, "ced_rev": CED_REV,
                     "note": "event boundaries are approximate (+-0.5 s); labels may overlap", "v": 3})
    return {"speech_spans": len(speech), "events": len(events)}
