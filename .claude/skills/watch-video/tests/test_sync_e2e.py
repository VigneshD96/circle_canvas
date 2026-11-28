"""End-to-end A/V sync: cut + join the flash/beep clip many times, then measure flash vs beep offsets.

Needs ffmpeg and tests/fixtures/sync.mp4 (python tests/make_fixtures.py tests/fixtures).
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from wv.edit import render, validate_edl

sys.path.insert(0, str(Path(__file__).parent))

FIX = Path(__file__).parent / "fixtures"
FPS = 25


def flash_times(video: Path) -> list[float]:
    raw = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", str(video), "-vf", "scale=32:18,format=gray",
                          "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    lum = np.frombuffer(raw, np.uint8).reshape(-1, 18 * 32).mean(axis=1)
    on = lum > 128
    return [i / FPS for i in range(len(on)) if on[i] and (i == 0 or not on[i - 1])]


def beep_times(video: Path) -> list[float]:
    raw = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000",
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    y = np.abs(np.frombuffer(raw, np.float32))
    hop = 80  # 5 ms
    env = y[: len(y) // hop * hop].reshape(-1, hop).max(axis=1)
    on = env > 0.05
    return [i * hop / 16000 for i in range(len(on)) if on[i] and (i == 0 or not on[i - 1])]


@pytest.mark.skipif(not (FIX / "sync.mp4").exists(), reason="fixtures not generated")
def test_repeated_cuts_keep_av_sync(tmp_path):
    src = FIX / "sync.mp4"
    # 10 segments that each contain one flash+beep (at 1, 3, 5, ... s); cut edges sit on frame boundaries
    segs = [{"start": round(0.6 + 2 * k, 2), "end": round(1.6 + 2 * k, 2), "label": f"s{k}"} for k in range(9)]
    segs, _ = validate_edl(segs, duration=20.0)
    out = render(src, segs, tmp_path, "joined", "join", has_audio=True, a_order=0)[0]
    f, b = flash_times(Path(out)), beep_times(Path(out))
    assert len(f) == len(segs) and len(b) == len(segs), (f, b)
    offsets = [abs(x - y) for x, y in zip(f, b)]
    assert max(offsets) <= 1.0 / FPS + 0.005, offsets  # within one frame, no drift
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out],
                               capture_output=True, text=True).stdout)
    assert abs(dur - sum(s["end"] - s["start"] for s in segs)) <= 1.0 / FPS + 0.06


@pytest.mark.skipif(not (FIX / "delayed_audio.mp4").exists(), reason="fixtures not generated")
def test_delayed_audio_stays_in_place(tmp_path):
    """Audio starts 1.0 s late in the source; a cut from 0.5 s must keep 0.5 s of silence before the voice."""
    src = FIX / "delayed_audio.mp4"
    out = render(src, [{"start": 0.52, "end": 4.0}], tmp_path, "d", "join", has_audio=True, a_order=0)[0]
    raw = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", out, "-vn", "-ac", "1", "-ar", "16000",
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    y = np.abs(np.frombuffer(raw, np.float32))
    first = int(np.argmax(y > 0.02)) / 16000
    assert first >= 0.45, first  # the voice (source 1.0 s + speech onset) must not move earlier


def test_many_segments_batched_path_keeps_sync(tmp_path):
    """> BATCH segments -> near-lossless intermediates + one final encode; sync must still hold."""
    import make_fixtures

    make_fixtures.make_sync(tmp_path, seconds=92)
    src = tmp_path / "sync.mp4"
    segs = [{"start": round(0.6 + 2 * k, 2), "end": round(1.6 + 2 * k, 2)} for k in range(45)]
    segs, _ = validate_edl(segs, duration=92.0)
    out = render(src, segs, tmp_path / "o", "many", "join", has_audio=True, a_order=0)[0]
    f, b = flash_times(Path(out)), beep_times(Path(out))
    assert len(f) == 45 and len(b) == 45, (len(f), len(b))
    offsets = [abs(x - y) for x, y in zip(f, b)]
    assert max(offsets) <= 1.0 / FPS + 0.005, max(offsets)


def test_cut_drops_source_chapters_and_data_streams(tmp_path):
    """MKV chapters copied into an MP4 cut make players show the source's length (seen with a 22-min episode)."""
    import json as _json
    import make_fixtures

    make_fixtures.make_sync(tmp_path, seconds=30)
    meta = tmp_path / "chap.txt"
    meta.write_text(";FFMETADATA1\n[CHAPTER]\nTIMEBASE=1/1000\nSTART=0\nEND=15000\ntitle=A\n"
                    "[CHAPTER]\nTIMEBASE=1/1000\nSTART=15000\nEND=30000\ntitle=B\n")
    src = tmp_path / "chap.mkv"
    subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", str(tmp_path / "sync.mp4"), "-i", str(meta),
                    "-map_chapters", "1", "-c", "copy", str(src)], check=True)
    for fast in (False, True):
        out = render(src, [{"start": 10.0, "end": 14.0}], tmp_path / f"o{fast}", "c", "join", has_audio=True, a_order=0,
                     fast_copy=fast)[0]
        info = _json.loads(subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams",
                                           "-show_chapters", out], capture_output=True, text=True).stdout)
        assert info["chapters"] == []
        assert sorted(st["codec_type"] for st in info["streams"]) == ["audio", "video"]
        limit = 8.5 if fast else 4.1  # fast-copy starts at the previous keyframe (GOP = 2 s): approximate by design
        assert all(float(st["duration"]) < limit for st in info["streams"])
