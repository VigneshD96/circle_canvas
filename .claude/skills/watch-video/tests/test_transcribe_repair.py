from wv.transcribe import repair_windows, splice


def W(w, s, e):
    return {"w": w, "start": s, "end": e, "conf": 0.9}


def test_windows_cover_gaps_lead_in_and_glued_tokens():
    words = [W("On", 3.0, 3.2), W("economy.9km", 3.3, 4.0), W("per", 4.1, 4.3), W("kg", 9.0, 9.3)]
    wins = repair_windows(words, 12.0)
    assert wins[0][0] == 0.0                        # lead-in 0-3 s gets a listen
    assert any(lo <= 4.3 and hi >= 9.0 for lo, hi in wins)  # the 4.7 s gap
    assert any(lo <= 3.3 and hi >= 4.0 for lo, hi in wins)  # glued token


def test_long_gap_gets_a_window_at_each_end():
    wins = repair_windows([W("a", 0.0, 0.5), W("b", 100.0, 100.4)], 100.4)
    assert len(wins) == 2 and all(hi - lo <= 40.0 for lo, hi in wins)


def test_splice_replaces_only_when_speech_is_recovered():
    words = [W("of", 1.0, 1.2), W("economy.9km", 1.3, 2.0), W("figure,", 6.0, 6.4)]
    new = [W("of", 1.0, 1.2), W("economy.", 1.3, 1.7), W("My", 2.0, 2.2), W("colleague", 2.2, 2.6),
           W("got", 3.0, 3.2), W("27.9", 3.3, 3.8), W("km", 3.9, 4.1), W("figure,", 6.0, 6.4)]
    out, note = splice(words, [0.5, 7.0], new, 10.0)
    assert [w["w"] for w in out] == ["of", "economy.", "My", "colleague", "got", "27.9", "km", "figure,"]
    assert note and "27.9" in note["new"] and all(w.get("repaired") for w in out)
    same, none = splice(words, [0.5, 7.0], words, 10.0)
    assert same == words and none is None


def test_splice_never_overlaps_kept_words_at_the_seams():
    words = [W("keep", 0.0, 1.2), W("tail", 9.0, 9.5)]
    new = [W("junk", 1.0, 1.4), W("one", 2.0, 2.3), W("two", 2.4, 2.7), W("three", 3.0, 3.3)]
    out, note = splice(words, [0.5, 8.0], new, 10.0)
    assert [w["w"] for w in out] == ["keep", "one", "two", "three", "tail"]
