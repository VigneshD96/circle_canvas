"""verify-edit: check a rendered output against the EDL record that produced it.

Checks: duration = EDL total (+- 1 frame + AAC padding), video/audio stream durations agree, the words around
each cut are the expected source words (re-transcribed with Parakeet), no word straddles a cut, and
(optional) speaker leakage via diarization of the output.
"""
from __future__ import annotations

import re
import tempfile
from pathlib import Path

from .probe import probe
from .util import fmt_ts, read_json

WIN = 2.0


def _norm(w: str) -> str:
    return re.sub(r"[^a-z0-9']", "", w.lower())


def _near(w: dict, t: float) -> bool:
    """Heard word overlaps the window around a cut. Expected words are chosen by their END inside the window, so a
    long word ("details", 0.9 s) can START outside it."""
    return w["end"] >= t - WIN - 0.3 and w["start"] <= t + WIN + 0.3


def _transcribe_words(media: Path) -> list[dict]:
    from .audio import extract
    from .transcribe import transcribe

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        extract(media, 0, td / "a.wav")
        transcribe(td / "a.wav", 0.0, td / "t.json", td / "w.json")
        return read_json(td / "w.json")["words"]


def _transcribe_window(media: Path, t0: float, dur: float) -> list[dict]:
    """Words of one window, in output time. Used to re-listen at a cut: on music-heavy audio, Parakeet on the
    whole file can drop a full line that it hears fine in a short window (Kivi Short 2026-10-06)."""
    from .audio import SR
    from .transcribe import transcribe
    from .util import run

    t0 = max(0.0, t0)
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-ss", f"{t0:.3f}", "-t", f"{dur:.3f}", "-i", str(media),
             "-map", "0:a:0", "-vn", "-ac", "1", "-ar", str(SR), "-c:a", "pcm_f32le", str(td / "a.wav")])
        transcribe(td / "a.wav", t0, td / "t.json", td / "w.json")
        return read_json(td / "w.json")["words"]


def check_output(out: Path, segs: list[dict], src_words: list[dict], leakage: bool = False) -> dict:
    pr = probe(out)
    fps = (pr["video"] or {}).get("fps") or 25.0
    total = sum(s["end"] - s["start"] for s in segs)
    tol = len(segs) / fps + 0.06  # each segment may round to whole frames
    v_d = (pr["video"] or {}).get("duration")
    a_d = None
    res: dict = {"output": str(out), "expected_s": round(total, 3), "duration_s": round(pr["duration"], 3), "problems": []}
    if abs(pr["duration"] - total) > tol:
        res["problems"].append(f"duration {pr['duration']:.3f}s differs from EDL total {total:.3f}s")
    import json as _json

    from .util import run as _run

    info = _json.loads(_run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_chapters",
                             str(out)]).stdout)
    if info.get("chapters"):
        res["problems"].append(f"output has {len(info['chapters'])} chapters copied from the source (players show a wrong length)")
    for st in info.get("streams", []):
        if st.get("codec_type") not in ("video", "audio"):
            res["problems"].append(f"extra {st.get('codec_type')} stream #{st.get('index')} (players may show a wrong length)")
        d = float(st.get("duration") or 0)
        if d and abs(d - total) > max(1.0, tol):
            res["problems"].append(f"stream #{st.get('index')} ({st.get('codec_type')}) lasts {d:.1f}s, expected {total:.1f}s")
    if pr["audio"]:
        from .util import run

        q = run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=duration", "-of", "csv=p=0", str(out)])
        try:
            a_d = float(q.stdout.strip())
        except ValueError:
            a_d = None
    if v_d and a_d and abs(v_d - a_d) > tol:
        res["problems"].append(f"video {v_d:.3f}s vs audio {a_d:.3f}s streams differ (A/V sync risk)")
    res["video_s"], res["audio_s"] = v_d, a_d
    if not pr["audio"]:
        res["ok"] = not res["problems"]
        return res
    out_words = _transcribe_words(out)
    boundaries = []
    t = 0.0
    for i, s in enumerate(segs[:-1]):
        t += s["end"] - s["start"]
        nxt = segs[i + 1]
        exp = [_norm(w["w"]) for w in src_words if s["end"] - WIN < w["end"] <= s["end"] + 0.05 and w["start"] >= s["start"] - 0.05]
        exp += [_norm(w["w"]) for w in src_words if nxt["start"] - 0.05 <= w["start"] < nxt["start"] + WIN and w["end"] <= nxt["end"] + 0.05]
        got = [_norm(w["w"]) for w in out_words if _near(w, t)]
        exp = [w for w in exp if w]
        hit = sum(1 for w in exp if w in got) / len(exp) if exp else 1.0
        if hit < 0.6:
            again = _transcribe_window(out, t - WIN - 2.0, 2 * WIN + 4.0)
            got2 = [_norm(w["w"]) for w in again if _near(w, t)]
            hit = max(hit, sum(1 for w in exp if w in got2) / len(exp))
        straddle = [w["w"] for w in out_words if w["start"] < t - 0.05 and w["end"] > t + 0.05]
        b = {"out_t": round(t, 3), "src": f"{fmt_ts(s['end'])} | {fmt_ts(nxt['start'])}", "word_match": round(hit, 2)}
        if straddle:
            b["straddling_word"] = straddle[0]
        if hit < 0.6:
            res["problems"].append(f"cut at out {fmt_ts(t)}: only {hit:.0%} of expected boundary words heard")
        boundaries.append(b)
    res["boundaries"] = boundaries
    first, last = (out_words[0]["start"], out_words[-1]["end"]) if out_words else (None, None)
    res["first_word_at"], res["last_word_end"] = first, last
    if leakage:
        from .audio import SR, extract, load
        from .diarize import diarize

        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            extract(out, 0, td / "a.wav")
            info = diarize(load(td / "a.wav"), SR, 0.0, td / "d.json")
            d = read_json(td / "d.json")
        talk: dict[str, float] = {}
        for x in d["exclusive"]:
            talk[x["spk"]] = talk.get(x["spk"], 0.0) + x["end"] - x["start"]
        tot = sum(talk.values()) or 1.0
        share = max(talk.values()) / tot if talk else 1.0
        res["leakage"] = {"voices_found": info["speakers"], "main_voice_share": round(share, 3)}
        if share < 0.9:
            res["problems"].append(f"speaker leakage: main voice is only {share:.0%} of speech in the output "
                                   f"(may also be one person split in two voices; listen to check)")
    res["ok"] = not res["problems"]
    return res
