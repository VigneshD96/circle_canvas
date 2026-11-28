from wv.identify import hints
from wv.transcribe import tokens_to_words


def tok(text, s, e, c=1.0):
    return {"text": text, "start": s, "end": e, "conf": c}


def test_tokens_merge_subwords_and_punctuation():
    toks = [tok(" Go", 0.0, 0.16), tok("od", 0.16, 0.32), tok(" mor", 0.32, 0.48), tok("ning", 0.48, 0.64),
            tok(",", 0.64, 0.72), tok(" it", 0.8, 0.9), tok("'s", 0.9, 1.0, 0.8), tok(" 5", 1.0, 1.2),
            tok(" cups", 1.2, 1.5), tok("?", 1.5, 1.9)]
    w = tokens_to_words(toks)
    assert [x["w"] for x in w] == ["Good", "morning,", "it's", "5", "cups?"]
    assert w[1]["end"] == 0.64  # comma does not stretch the word
    assert w[4]["end"] == 1.5  # '?' does not stretch the word
    assert w[2]["conf"] == 0.8


def test_bare_space_token_before_digit_starts_new_word():
    toks = [tok(" about", 0.0, 0.3), tok(" ", 0.3, 0.35), tok("5", 0.35, 0.5), tok(" cu", 0.5, 0.6), tok("ps", 0.6, 0.7),
            tok(".", 0.7, 0.8), tok(" ", 0.8, 0.85), tok("5", 0.85, 1.0)]
    assert [x["w"] for x in tokens_to_words(toks)] == ["about", "5", "cups.", "5"]


def test_first_token_without_space_starts_word():
    assert [x["w"] for x in tokens_to_words([tok("Hi", 0, 0.2), tok(" there", 0.2, 0.5)])] == ["Hi", "there"]


def test_hints_tv_episode():
    h = hints("Friends.S04E03.The.One.With.The.Jam.1080p.WEB-DL.x264.mkv")
    assert h["series"] == "Friends" and h["season"] == 4 and h["episode"] == 3
    assert h["episode_title"] == "The One With The Jam"
    assert h["guess"].startswith("Friends S04E03")


def test_hints_nxn_and_youtube_and_plain():
    assert hints("The Big Bang Theory 2x05 - The Euclid Alternative.mp4")["season"] == 2
    y = hints("Lex Fridman Podcast #400 - Guest Name [dQw4w9WgXcQ].mp4")
    assert y["youtube_id"] == "dQw4w9WgXcQ"
    p = hints("team sync recording.mov")
    assert p["guess"] == "team sync recording" and "season" not in p


def test_hints_uses_container_tags():
    h = hints("video.mp4", {"title": "My Talk", "artist": "Jane"})
    assert h["tag_title"] == "My Talk" and h["tag_artist"] == "Jane"
