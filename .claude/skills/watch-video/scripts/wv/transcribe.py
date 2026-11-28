"""Parakeet-TDT 0.6B v3 via parakeet-mlx. Uses the library's own chunk stitching (no second merge), then a repair
pass: on long files with music or noise, the full pass can drop whole sentences ("My colleague Lokesh ... got a
27.9 km per kg figure", Tata Aeris review 2026-10-06) or glue words into one token ("economy.9km") that a short
window hears fine. Gaps between words and glued tokens get a second listen; the window's words replace the
original ones only when they add at least REPAIR_MIN_GAIN words."""
from __future__ import annotations

import re
import tempfile
from pathlib import Path

from .util import local_model, write_json

MODEL = "mlx-community/parakeet-tdt-0.6b-v3"
MODEL_REV = "ed2b7e8c15f9aaa0b5772e2efb986255eaef7e15"
CHUNK_S, OVERLAP_S = 120.0, 15.0
REPAIR_V = 1
REPAIR_GAP_S = 1.2       # silence between two words worth a second listen
REPAIR_PAD_S = 1.5       # context on each side of a gap
REPAIR_MAX_S = 40.0      # longest window (a longer gap gets one window at each end)
REPAIR_EDGE_S = 0.5      # words this close to a window edge are not trusted
REPAIR_MIN_GAIN = 2
_GLUED = re.compile(r"[A-Za-z][.,!?][0-9]|[0-9][A-Za-z]{3,}")  # "economy.9km": several words in one token

_PUNCT_ONLY = set(".,!?;:%)]}…\"'”’")


def tokens_to_words(tokens: list[dict]) -> list[dict]:
    """Merge SentencePiece tokens into words.

    A token whose text starts with a space starts a new word. Pure punctuation tokens attach to the
    previous word (their timing is not used for word end, so a trailing '.' does not stretch the word).
    """
    words: list[dict] = []
    pending_space = False  # Parakeet can emit a bare " " token before digits: ' about', ' ', '5'
    for t in tokens:
        txt = t["text"]
        if not txt:
            continue
        core = txt.strip()
        if not core:
            pending_space = True
            continue
        starts_word = txt[0] == " " or pending_space or not words
        pending_space = False
        if not starts_word or (all(c in _PUNCT_ONLY for c in core) and words):
            w = words[-1]
            w["w"] += core
            if not all(c in _PUNCT_ONLY for c in core):
                w["end"] = t["end"]
            w["conf"] = min(w["conf"], t["conf"])
            continue
        words.append({"w": core, "start": t["start"], "end": t["end"], "conf": t["conf"]})
    for w in words:
        w["start"], w["end"], w["conf"] = round(w["start"], 3), round(w["end"], 3), round(w["conf"], 3)
    return words


def transcribe(wav: Path, offset: float, out_tokens: Path, out_words: Path) -> dict:
    from parakeet_mlx import from_pretrained

    model = from_pretrained(local_model(MODEL, MODEL_REV))
    res = model.transcribe(str(wav), chunk_duration=CHUNK_S, overlap_duration=OVERLAP_S)
    tokens = [
        {"text": t.text, "start": round(t.start + offset, 3), "end": round(t.end + offset, 3), "conf": round(t.confidence, 3)}
        for t in res.tokens
    ]
    words, repaired = repair(model, wav, offset, tokens_to_words(tokens))
    write_json(out_tokens, {"model": MODEL, "rev": MODEL_REV, "offset": offset, "tokens": tokens})
    write_json(out_words, {"model": MODEL, "words": words, "repaired": repaired})
    return {"n_words": len(words), "text_chars": len(res.text), "repaired_windows": len(repaired)}


def repair_windows(words: list[dict], duration: float) -> list[list[float]]:
    """Time windows that deserve a second listen: gaps between words, the lead-in and tail, glued tokens."""
    wins: list[list[float]] = []
    edges = [(0.0, 0.0)] + [(w["start"], w["end"]) for w in words] + [(duration, duration)]
    for (_, a_end), (b_start, _) in zip(edges, edges[1:]):
        if b_start - a_end < REPAIR_GAP_S:
            continue
        lo, hi = a_end - REPAIR_PAD_S, b_start + REPAIR_PAD_S
        if hi - lo <= REPAIR_MAX_S:
            wins.append([lo, hi])
        else:
            wins += [[lo, lo + REPAIR_MAX_S], [hi - REPAIR_MAX_S, hi]]
    wins += [[w["start"] - 4.0, w["end"] + 4.0] for w in words if _GLUED.search(w["w"])]
    out: list[list[float]] = []
    for lo, hi in sorted([max(0.0, a), min(duration, b)] for a, b in wins):
        if hi - lo < 0.5:
            continue
        if out and lo <= out[-1][1] and hi - out[-1][0] <= REPAIR_MAX_S:
            out[-1][1] = max(out[-1][1], hi)
        else:
            out.append([lo, hi])
    return out


def splice(words: list[dict], win: list[float], new: list[dict], duration: float) -> tuple[list[dict], dict | None]:
    """Replace the words inside the window's trusted middle by the window's words when that recovers speech."""
    lo = win[0] + (REPAIR_EDGE_S if win[0] > 0 else 0.0)
    hi = win[1] - (REPAIR_EDGE_S if win[1] < duration else 0.0)
    old_in = [w for w in words if lo <= w["start"] < hi]
    new_in = [w for w in new if lo <= w["start"] < hi]
    if len(new_in) < len(old_in) + REPAIR_MIN_GAIN:
        return words, None
    before = [w for w in words if w["start"] < lo]
    after = [w for w in words if w["start"] >= hi]
    floor = before[-1]["end"] - 0.05 if before else -1.0
    ceil = after[0]["start"] + 0.05 if after else duration + 1.0
    new_in = [dict(w, repaired=True) for w in new_in if w["start"] >= floor and w["end"] <= ceil]
    if len(new_in) < len(old_in) + REPAIR_MIN_GAIN:
        return words, None
    note = {"start": round(lo, 3), "end": round(hi, 3), "old": " ".join(w["w"] for w in old_in),
            "new": " ".join(w["w"] for w in new_in)}
    return before + new_in + after, note


def repair(model, wav: Path, offset: float, words: list[dict]) -> tuple[list[dict], list[dict]]:
    import soundfile as sf

    info = sf.info(str(wav))
    duration = offset + info.frames / info.samplerate
    notes = []
    with tempfile.TemporaryDirectory() as td:
        for k, win in enumerate(repair_windows(words, duration)):
            a, b = int((win[0] - offset) * info.samplerate), int((win[1] - offset) * info.samplerate)
            y, sr = sf.read(str(wav), start=max(0, a), stop=b, dtype="float32")
            part = Path(td) / f"w{k}.wav"
            sf.write(str(part), y, sr)
            t0 = max(0, a) / sr + offset
            toks = [{"text": t.text, "start": t.start + t0, "end": t.end + t0, "conf": t.confidence}
                    for t in model.transcribe(str(part)).tokens]
            words, note = splice(words, win, tokens_to_words(toks), duration)
            if note:
                notes.append(note)
    return words, notes
