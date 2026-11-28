import json

import numpy as np
import pytest

from wv import chunks, frames
from wv.edit import snap_edges, speaker_segments, validate_edl
from wv.validate import validate


def W(w, s, e, spk="S1", flags=None):
    return {"w": w, "start": s, "end": e, "spk": spk, "flags": flags or [], "alt": None, "conf": 1.0}


# ---------------- EDL validation
def test_validate_edl_sorts_merges_and_clamps():
    segs, warn = validate_edl([{"start": 5, "end": 8}, {"start": 1, "end": 3}, {"start": 7.5, "end": 9}, {"start": -1, "end": 0.5},
                               {"start": 9.5, "end": 99}], duration=10)
    assert [(s["start"], s["end"]) for s in segs] == [(0.0, 0.5), (1, 3), (5, 9), (9.5, 10)]
    assert any("clamped" in w for w in warn) and any("merged" in w for w in warn)


@pytest.mark.parametrize("bad", [{"start": 3, "end": 3}, {"start": "x", "end": 4}, {"start": float("nan"), "end": 4}, {"end": 4}])
def test_validate_edl_rejects_bad(bad):
    with pytest.raises(ValueError):
        validate_edl([bad], duration=10)


def test_given_order_kept():
    segs, _ = validate_edl([{"start": 5, "end": 6}, {"start": 1, "end": 2}], duration=10, order="given")
    assert [s["start"] for s in segs] == [5, 1]


# ---------------- snapping
WORDS = [W("hello", 1.0, 1.4), W("there", 1.5, 1.9), W("friend", 2.0, 2.6, "S2"), W("yes", 3.5, 3.8, "S2")]


def test_snap_includes_word_when_edge_close_to_start_and_pads_into_silence():
    segs, notes = snap_edges([{"start": 1.1, "end": 1.85}], WORDS, None)
    s = segs[0]
    assert s["start"] < 1.0 and s["start"] >= 1.0 - 0.15 - 1e-9  # snapped to word start then padded
    assert s["end"] >= 1.9 and s["end"] <= 1.98 + 1e-9  # padding stops before S2's "friend" at 2.0
    assert notes == []


def test_snap_excludes_word_when_edge_near_its_end():
    segs, _ = snap_edges([{"start": 1.35, "end": 3.0}], WORDS, None)
    assert segs[0]["start"] >= 1.4  # 'hello' excluded, never half-cut


def test_snap_reports_word_too_long_to_snap():
    long = [W("loooong", 1.0, 2.0)]
    _, notes = snap_edges([{"start": 1.5, "end": 3.0}], long, None)
    assert notes and "cuts the word" in notes[0]


def test_snap_to_frame_grid():
    pts = [i * 0.04 for i in range(200)]
    segs, _ = snap_edges([{"start": 0.53, "end": 0.71}], [], pts)
    assert round(segs[0]["start"] / 0.04, 6).is_integer() and round(segs[0]["end"] / 0.04, 6).is_integer()
    assert segs[0]["start"] <= 0.53 and segs[0]["end"] >= 0.71


def test_padding_never_overlaps_neighbour_segment():
    # Kivi Short (2026-10-06): segments 0.2 s apart in silence were each padded 0.15 s -> 0.1 s shown twice
    pts = [i / 30 for i in range(3000)]
    segs, notes = snap_edges([{"start": 52.3, "end": 62.8}, {"start": 63.0, "end": 69.6}], [], pts)
    assert segs[0]["end"] == segs[1]["start"]
    assert 62.8 <= segs[0]["end"] <= 63.0
    assert any("padding overlap" in n for n in notes)


# ---------------- speaker-only
def _al(words, excl):
    return {"words": words, "exclusive": excl}


def test_speaker_only_keeps_short_lines_and_never_bridges_other_speech():
    words = [W("hi", 0.0, 0.2, "S1"), W("there", 0.3, 0.6, "S1"), W("what", 0.8, 1.0, "S2"),
             W("ok", 1.2, 1.3, "S1"), W("then", 4.0, 4.3, "S1")]
    excl = [{"spk": "S1", "start": 0, "end": 0.7}, {"spk": "S2", "start": 0.75, "end": 1.1},
            {"spk": "S1", "start": 1.15, "end": 1.35}, {"spk": "S2", "start": 2.0, "end": 3.0}, {"spk": "S1", "start": 3.9, "end": 4.4}]
    segs, rep = speaker_segments(_al(words, excl), {"S1"})
    assert [(s["start"], s["end"]) for s in segs] == [(0.0, 0.6), (1.2, 1.3), (4.0, 4.3)]
    assert rep["segments"] == 3


def test_speaker_only_joins_across_silence_and_overlap_drop():
    words = [W("a", 0.0, 0.2), W("b", 0.9, 1.1, flags=["overlap"]), W("c", 1.5, 1.7)]
    excl = [{"spk": "S1", "start": 0, "end": 1.8}]
    keep, _ = speaker_segments(_al(words, excl), {"S1"})
    assert [(s["start"], s["end"]) for s in keep] == [(0.0, 1.7)]
    drop, _ = speaker_segments(_al(words, excl), {"S1"}, overlap="drop")
    assert [(s["start"], s["end"]) for s in drop] == [(0.0, 0.2), (1.5, 1.7)]


# ---------------- frames + chunk planning
def test_frame_budget_relaxes_but_keeps_all_cuts():
    n = 3000
    pts = np.arange(n) * 0.04
    score = np.full(n, 30.0, np.float32)  # constant heavy motion -> every grid frame "changes"
    score[::250] = 200.0  # a cut every 10 s
    rng = np.random.default_rng(0)
    dh = rng.integers(0, 2**63, n, dtype=np.int64).astype(np.uint64)
    th = rng.integers(0, 255, (n, 18, 32), dtype=np.uint8)
    sel = frames.select(pts, score, dh, th, duration=float(pts[-1]), budget=60)
    assert len(sel["kept"]) <= 60 or sel["fps_scale"] == frames.FPS_SCALES[-1]
    cut_frames = {s["first"] for s in sel["shots"]}
    assert cut_frames <= {k["idx"] for k in sel["kept"]}


def test_detect_cuts_min_length():
    pts = np.arange(100) * 0.04
    score = np.zeros(100, np.float32)
    score[[20, 22, 60]] = 100.0  # 20 and 22 are 0.08 s apart -> second suppressed
    assert frames.detect_cuts(pts, score) == [20, 60]


def test_chunk_plan_inline_and_fanout_snaps_to_cut_in_silence():
    kept = [{"t": float(t), "idx": t, "shot": 0, "reason": "grid"} for t in range(0, 900)]
    small = chunks.plan(kept[:100], [{"start": 0}], [], 900, per_sheet=9)
    assert small["mode"] == "inline" and len(small["chunks"]) == 1
    shots = [{"start": 0.0}, {"start": 452.0}]
    speech = [{"start": 0, "end": 451.5}, {"start": 452.8, "end": 900}]
    big = chunks.plan(kept, shots, speech, 900, per_sheet=9, sheets_per_chunk=50)
    assert big["mode"] == "fanout" and len(big["chunks"]) == 2
    assert big["chunks"][1]["start"] == 452.0


# ---------------- scene log validation
def _log(**over):
    d = {"run_id": "r1", "chunk_id": 1, "start": 0, "end": 60, "summary": "Two people talk about coffee in a studio.",
         "scenes": [{"start": 0, "end": 60, "setting": "studio", "on_screen": ["Ann"], "what_happens": "talk",
                     "sheet_refs": [1, 2]}],
         "events": [], "quotes": [], "highlight_candidates": [], "changes_over_time": "", "speaker_notes": [], "uncertain": []}
    d.update(over)
    return d


def test_validate_ok_and_errors(tmp_path):
    ch = {"id": 1, "start": 0, "end": 60, "sheet_ids": [1, 2]}
    p = tmp_path / "c.json"
    p.write_text(json.dumps(_log()))
    assert validate(p, ch, "r1") == []
    p.write_text(json.dumps(_log(run_id="other", scenes=[{"start": 0, "end": 20, "setting": "s", "on_screen": [],
                                                           "what_happens": "x", "sheet_refs": [1, 9]}])))
    errs = " | ".join(validate(p, ch, "r1"))
    assert "run_id" in errs and "cover" in errs and "[9]" in errs and "never referenced" in errs
    p.write_text("{not json")
    assert "not valid JSON" in validate(p, ch, "r1")[0]


def test_padding_stops_at_shot_cut():
    words = [W("hi", 20.5, 20.8), W("there", 20.9, 21.3)]
    segs, _ = snap_edges([{"start": 20.5, "end": 21.3}], words, None, cuts=[20.45, 21.40])
    assert segs[0]["start"] == 20.45  # padding would reach 20.35, i.e. into the previous shot
    assert segs[0]["end"] == 21.40


def test_cut_snap_uses_vad_when_asr_starts_early():
    words = [W("Thanks", 5.44, 5.8)]  # ASR says 5.44 but VAD says speech starts at 5.6 (= the shot cut)
    speech = [{"start": 5.6, "end": 7.0}]
    segs, _ = snap_edges([{"start": 5.44, "end": 5.8}], words, None, cuts=[5.6], speech=speech)
    assert segs[0]["start"] == 5.6
    # but never move past real speech: VAD speech already at 5.45 -> keep the early start
    segs, _ = snap_edges([{"start": 5.44, "end": 5.8}], words, None, cuts=[5.6], speech=[{"start": 5.45, "end": 7.0}])
    assert segs[0]["start"] < 5.44


def test_many_short_shots_keep_grid_before_shot_ends():
    n = 6000  # 240 s at 25 fps, a cut every 2 s (120 shots), mild motion
    pts = np.arange(n) * 0.04
    score = np.full(n, 2.0, np.float32)
    score[::50] = 120.0
    rng = np.random.default_rng(1)
    dh = rng.integers(0, 2**63, n, dtype=np.int64).astype(np.uint64)
    th = rng.integers(0, 255, (n, 18, 32), dtype=np.uint8)
    sel = frames.select(pts, score, dh, th, duration=240.0, budget=300)
    reasons = {k["reason"] for k in sel["kept"]}
    assert len(sel["kept"]) <= 300 and "shot_end" not in reasons  # 2 s shots are shorter than SHOT_END_MIN_S
    assert sel["fps_scale"] >= 0.5  # grid density kept


def test_merge_collects_machine_readable_speaker_fixes(tmp_path):
    from wv.merge import merge
    from wv.transcript import resolve_overrides
    log = _log(speaker_notes=[{"id": "S5", "evidence": "Chandler mid-sentence on screen",
                               "possible_error": "'as a healthy' is Chandler",
                               "fix": {"text": "as a healthy", "t": 31.0, "name": "Chandler"}}])
    (tmp_path / "scene_logs").mkdir()
    (tmp_path / "scene_logs" / "chunk_01.json").write_text(json.dumps(log))
    res = merge(tmp_path, "r1", [{"id": 1, "start": 0, "end": 60, "sheet_ids": [1, 2]}])
    assert res["ok"] and res["speaker_fixes"] == 1
    fixes = json.loads((tmp_path / "timeline.json").read_text())["speaker_fixes"]
    words = [{"w": "as", "start": 31.0, "end": 31.2, "spk": "S5"}, {"w": "a", "start": 31.2, "end": 31.3, "spk": "S5"},
             {"w": "healthy", "start": 31.3, "end": 31.9, "spk": "S5"}]
    ov, problems = resolve_overrides(words, fixes)
    assert not problems and ov[0]["id"] == "S5" and ov[0]["name"] == "Chandler"
