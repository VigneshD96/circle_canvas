from wv.align import UNKNOWN, align, assign_words, build_lines, nonword_turns, overlap_regions, relabel


def W(w, s, e):
    return {"w": w, "start": s, "end": e, "conf": 1.0}


def T(spk, s, e):
    return {"spk": spk, "start": s, "end": e}


def test_clear_assignment():
    out = assign_words([W("hi", 1.0, 1.4)], [T("A", 0.5, 2.0), T("B", 2.0, 3.0)])
    assert out[0]["spk"] == "A" and out[0]["flags"] == [] and out[0]["alt"] is None


def test_ambiguous_when_word_straddles_boundary():
    out = assign_words([W("well", 1.9, 2.1)], [T("A", 0.5, 2.0), T("B", 2.0, 3.0)])
    assert out[0]["spk"] in ("A", "B")
    assert "ambiguous" in out[0]["flags"] or "weak" in out[0]["flags"]
    assert out[0]["alt"] in ("A", "B") and out[0]["alt"] != out[0]["spk"]


def test_weak_when_less_than_half_covered():
    out = assign_words([W("so", 1.0, 2.0)], [T("A", 1.7, 3.0)])
    assert out[0]["spk"] == "A" and out[0]["flags"] == ["weak"]


def test_near_within_limit_and_unknown_beyond():
    turns = [T("A", 0.0, 1.0)]
    near = assign_words([W("x", 1.2, 1.4)], turns)[0]
    far = assign_words([W("y", 2.0, 2.3)], turns)[0]
    assert near["spk"] == "A" and near["flags"] == ["near"]
    assert far["spk"] == UNKNOWN and far["flags"] == []


def test_long_turn_still_found():
    out = assign_words([W("deep", 150.0, 150.4)], [T("A", 0.0, 200.0)])
    assert out[0]["spk"] == "A"


def test_overlap_flag_from_regular_diarization():
    regular = [T("A", 0.0, 3.0), T("B", 1.0, 2.0)]
    assert overlap_regions(regular) == [(1.0, 2.0)]
    out = assign_words([W("a", 1.2, 1.5), W("b", 2.5, 2.8)], [T("A", 0.0, 3.0)], regular)
    assert "overlap" in out[0]["flags"] and "overlap" not in out[1]["flags"]


def test_relabel_by_talk_time():
    m = relabel([T("SPEAKER_00", 0, 1), T("SPEAKER_01", 1, 5), T("SPEAKER_00", 5, 6)])
    assert m == {"SPEAKER_01": "S1", "SPEAKER_00": "S2"}


def test_lines_split_on_speaker_and_gap():
    ws = [dict(W("a", 0, 0.5), spk="S1", flags=[]), dict(W("b", 0.6, 1.0), spk="S1", flags=[]),
          dict(W("c", 1.1, 1.5), spk="S2", flags=[]), dict(W("d", 5.0, 5.3), spk="S2", flags=["weak"])]
    lines = build_lines(ws)
    assert [ln["text"] for ln in lines] == ["a b", "c", "d"]
    assert lines[2]["uncertain"]


def test_events_never_delete_words_and_nonword_turns_flagged():
    words = [W("hello", 0.1, 0.5)]
    diar = {"exclusive": [T("A", 0.0, 1.0), T("B", 2.0, 4.0)], "regular": [T("A", 0.0, 1.0), T("B", 2.0, 4.0)]}
    events = [{"type": "LAUGHTER", "start": 1.9, "end": 4.1}]
    res = align(words, diar, events)
    assert len(res["words"]) == 1
    nw = res["nonword_turns"]
    assert len(nw) == 1 and nw[0]["likely_non_speech"] is True


def test_nonword_turn_not_flagged_without_events():
    nw = nonword_turns([T("A", 0, 1)], [], [])
    assert nw and nw[0]["likely_non_speech"] is False


def test_sentence_first_word_goes_to_turn_that_starts_inside_it():
    words = [W("done.", 1.0, 1.5), W("Well", 1.9, 2.3)]
    turns = [T("A", 0.0, 2.15), T("B", 2.15, 4.0)]  # 'Well' is 62% inside A, but B's turn starts inside it
    out = assign_words(words, turns)
    assert out[1]["spk"] == "B" and out[1]["alt"] == "A" and "ambiguous" in out[1]["flags"]


def test_mid_sentence_word_keeps_majority_speaker():
    words = [W("and", 1.0, 1.5), W("then", 1.9, 2.3)]
    turns = [T("A", 0.0, 2.15), T("B", 2.15, 4.0)]
    assert assign_words(words, turns)[1]["spk"] == "A"


def test_phrase_override_resolves_to_word_span():
    from wv.transcript import Namer, resolve_overrides
    words = [dict(W("to", 429.0, 429.3), spk="S3"), dict(W("friends", 429.4, 430.9), spk="S3"),
             dict(W("as", 431.0, 431.2), spk="S5"), dict(W("a", 431.2, 431.3), spk="S5"),
             dict(W("healthy", 431.3, 431.9), spk="S5"), dict(W("snack.", 431.9, 432.5), spk="S3")]
    ov, problems = resolve_overrides(words, [{"text": "as a healthy", "t": 431, "name": "Chandler"},
                                             {"text": "not here", "t": 431, "name": "X"}])
    assert len(ov) == 1 and ov[0]["id"] == "S5" and ov[0]["start"] < 431.0 < 431.9 < ov[0]["end"] < 431.95
    assert problems and "not found" in problems[0]
    n = Namer({"speakers": {"S3": {"name": "Chandler", "confidence": "high"}, "S5": {"name": "Monica", "confidence": "high"}},
               "overrides": ov})
    assert {n.label(w["spk"], (w["start"] + w["end"]) / 2) for w in words} == {"Chandler"}
