"""Visual track.

Pass 1 (scan): one ffmpeg decode of EVERY frame at a tiny size, with `showinfo` giving each frame's real
PTS. Per frame we keep an HSV change score, a 64-bit dHash and a 32x18 gray thumbnail.
Shot cuts: the PySceneDetect AdaptiveDetector rule (score / mean of 2 neighbours on each side >= 3.0
and score >= 15), minimum shot length 0.25 s.
Selection: sampling grid (base fps by duration) + first frame of every shot + last frame of longer shots,
then dedup inside a shot (dHash distance or any region changed) with a heartbeat.
Pass 2 (extract): accurate `-ss <pts>` seek per kept frame, 768 px long edge JPEG.
"""
from __future__ import annotations

import bisect
import re
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

from .util import log, write_json

SCAN_LONG_EDGE = 128
THUMB_W, THUMB_H = 32, 18
FRAME_LONG_EDGE = 768

ADAPT_THRESHOLD, MIN_CONTENT, WINDOW, MIN_SHOT_S = 3.0, 15.0, 2, 0.25
HASH_DIST = 10
SHOT_END_MIN_S = 4.0
_PTS_RE = re.compile(rb"pts_time:\s*(-?[0-9.]+)")


def base_fps(duration: float) -> float:
    if duration <= 60:
        return 4.0
    if duration <= 600:
        return 2.0
    if duration <= 3600:
        return 1.0
    return 0.5


def heartbeat(duration: float) -> float:
    return float(min(10.0, max(2.0, duration / 600.0)))


def _scan_size(w: int, h: int) -> tuple[int, int]:
    if w >= h:
        sw, sh = SCAN_LONG_EDGE, max(2, int(round(SCAN_LONG_EDGE * h / w / 2)) * 2)
    else:
        sh, sw = SCAN_LONG_EDGE, max(2, int(round(SCAN_LONG_EDGE * w / h / 2)) * 2)
    return sw, sh


def _dhash(gray: np.ndarray) -> int:
    import cv2

    small = cv2.resize(gray, (9, 8), interpolation=cv2.INTER_AREA).astype(np.int16)
    bits = (small[:, 1:] > small[:, :-1]).flatten()
    return int(np.packbits(bits).view(">u8")[0])


def hamming(a: int, b: int) -> int:
    return int(bin(int(a) ^ int(b)).count("1"))


def scan(video: Path, width: int, height: int, out_npz: Path, hwaccel: bool = False) -> dict:
    import cv2

    sw, sh = _scan_size(width, height)
    cmd = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "info"]
    if hwaccel:
        cmd += ["-hwaccel", "videotoolbox"]
    cmd += ["-i", str(video), "-map", "0:v:0", "-an", "-sn", "-dn",
            "-vf", f"scale={sw}:{sh}:flags=area,showinfo", "-fps_mode", "passthrough",
            "-pix_fmt", "bgr24", "-f", "rawvideo", "pipe:1"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    pts: list[float] = []
    err_tail: list[bytes] = []

    def read_err():
        for line in proc.stderr:
            m = _PTS_RE.search(line)
            if m:
                pts.append(float(m.group(1)))
            else:
                err_tail.append(line)
                del err_tail[:-20]

    th = threading.Thread(target=read_err, daemon=True)
    th.start()
    fsize = sw * sh * 3
    scores, hashes, thumbs = [], [], []
    prev_hsv = None
    while True:
        buf = proc.stdout.read(fsize)
        if not buf or len(buf) < fsize:
            break
        img = np.frombuffer(buf, np.uint8).reshape(sh, sw, 3)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.int16)
        scores.append(0.0 if prev_hsv is None else float(np.abs(hsv - prev_hsv).mean()))
        prev_hsv = hsv
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        hashes.append(_dhash(gray))
        tw, th_ = (THUMB_W, THUMB_H) if sw >= sh else (THUMB_H, THUMB_W)
        thumbs.append(cv2.resize(gray, (tw, th_), interpolation=cv2.INTER_AREA))
    proc.wait()
    th.join(timeout=5)
    n = min(len(scores), len(pts))
    if n == 0:
        if hwaccel:
            log("scan: hardware decode gave no frames; retrying in software")
            return scan(video, width, height, out_npz, hwaccel=False)
        raise RuntimeError("video scan produced no frames:\n" + b"".join(err_tail).decode(errors="replace"))
    if len(scores) != len(pts):
        log(f"scan: frame/pts count mismatch {len(scores)} vs {len(pts)}; using {n}")
    out_npz.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out_npz, pts=np.array(pts[:n], np.float64), score=np.array(scores[:n], np.float32),
                        dhash=np.array(hashes[:n], np.uint64), thumbs=np.stack(thumbs[:n]))
    return {"frames": n, "scan_size": [sw, sh], "hwaccel": hwaccel}


def detect_cuts(pts: np.ndarray, score: np.ndarray) -> list[int]:
    """Indices of frames that start a new shot (frame 0 not included)."""
    n = len(score)
    cuts: list[int] = []
    last_cut_t = pts[0] if n else 0.0
    for i in range(WINDOW, n - WINDOW):
        s = score[i]
        if s < MIN_CONTENT:
            continue
        neigh = np.concatenate([score[i - WINDOW:i], score[i + 1:i + 1 + WINDOW]])
        avg = float(neigh.mean())
        ratio = 255.0 if avg < 1e-5 else min(s / avg, 255.0)
        if ratio >= ADAPT_THRESHOLD and pts[i] - last_cut_t >= MIN_SHOT_S:
            cuts.append(i)
            last_cut_t = pts[i]
    return cuts


def region_changed(a: np.ndarray, b: np.ndarray, cell: int = 4, thr: float = 10.0) -> bool:
    """True if any cell x cell block of the gray thumbnails differs by more than thr on average."""
    d = np.abs(a.astype(np.int16) - b.astype(np.int16))
    h, w = d.shape
    hh, ww = h // cell * cell, w // cell * cell
    blocks = d[:hh, :ww].reshape(hh // cell, cell, ww // cell, cell).mean(axis=(1, 3))
    return bool(blocks.max() > thr)


def frame_budget(duration: float) -> int:
    """Upper bound on kept frames. Static videos stay far below it; it only bites on high-motion video."""
    m = duration / 60.0
    if m <= 1:
        return 150
    if m <= 10:
        return int(150 + 40 * (m - 1))
    if m <= 60:
        return int(510 + 15 * (m - 10))
    return int(1260 + 8 * (m - 60))


FPS_SCALES = (1.0, 0.75, 0.5, 0.35, 0.25, 0.15, 0.1, 0.05)


def select(pts: np.ndarray, score: np.ndarray, dhash: np.ndarray, thumbs: np.ndarray, duration: float,
           fps: float | None = None, region_thr: float = 10.0, budget: int | None = None) -> dict:
    """Pick frames; if over budget, lower the sampling rate step by step (change thresholds stay; cuts always kept)."""
    budget = budget or frame_budget(duration)
    base = fps or base_fps(duration)
    res = None
    # keep within-shot sampling density first: drop shot-end frames before going below half the base rate
    attempts = [(k, True) for k in FPS_SCALES if k >= 0.5] + [(k, False) for k in FPS_SCALES]
    for k, ends in attempts:
        res = _select_once(pts, score, dhash, thumbs, duration, base * k, region_thr, 1.0 / k, shot_ends=ends)
        if len(res["kept"]) <= budget:
            break
    res.pop("_factor")
    res["budget"], res["fps_scale"], res["shot_end_frames"] = budget, k, ends
    if len(res["kept"]) > budget:
        log(f"frames: {len(res['kept'])} kept > budget {budget} even at {res['fps']:.2f} fps (mostly shot cuts); keeping all cuts")
    elif k < 1:
        log(f"frames: lowered sampling to {res['fps']:.2f} fps (x{k}) to fit budget {budget}")
    return res


def _select_once(pts, score, dhash, thumbs, duration, fps, region_thr, factor, shot_ends=True) -> dict:
    fps = fps or base_fps(duration)
    hb = heartbeat(duration) * factor
    hash_dist = HASH_DIST
    n = len(pts)
    cuts = detect_cuts(pts, score)
    shot_starts = [0] + cuts
    shot_of = np.zeros(n, np.int32)
    for k, s in enumerate(shot_starts):
        shot_of[s:] = k
    shots = []
    for k, s in enumerate(shot_starts):
        e = (shot_starts[k + 1] - 1) if k + 1 < len(shot_starts) else n - 1
        shots.append({"id": k, "start": round(float(pts[s]), 3), "end": round(float(pts[e]), 3), "first": s, "last": e})
    reasons: dict[int, str] = {}
    pts_list = pts.tolist()
    t, end_t = float(pts[0]), float(pts[-1])
    while t <= end_t + 1e-6:
        i = max(0, bisect.bisect_right(pts_list, t + 1e-6) - 1)
        reasons.setdefault(i, "grid")
        t += 1.0 / fps
    for sh in shots:
        reasons[sh["first"]] = "cut"
        if shot_ends and sh["end"] - sh["start"] >= SHOT_END_MIN_S and reasons.get(sh["last"]) != "cut":
            reasons[sh["last"]] = "shot_end"
    kept: list[dict] = []
    last_idx_in_shot: dict[int, int] = {}
    for i in sorted(reasons):
        why = reasons[i]
        sid = int(shot_of[i])
        li = last_idx_in_shot.get(sid)
        keep = why == "cut" or li is None
        if not keep:
            changed = hamming(dhash[i], dhash[li]) > hash_dist or region_changed(thumbs[i], thumbs[li], thr=region_thr)
            if changed:
                keep, why = True, ("change" if why == "grid" else why)
            elif pts[i] - pts[li] >= hb:
                keep, why = True, "heartbeat"
        if keep:
            kept.append({"idx": int(i), "t": round(float(pts[i]), 3), "shot": sid, "reason": why})
            last_idx_in_shot[sid] = i
    gaps = coverage_gaps(pts, score, [k["t"] for k in kept])
    return {"fps": fps, "heartbeat": hb, "n_frames": n, "shots": shots, "kept": kept, "coverage_gaps": gaps,
            "_factor": factor}


def coverage_gaps(pts: np.ndarray, score: np.ndarray, kept_t: list[float], win: float = 2.0,
                  motion: float = 20.0) -> list[dict]:
    """Spans with heavy motion but < 2 kept frames: fast action we may have under-sampled."""
    if len(pts) < 2:
        return []
    out = []
    t0, end = float(pts[0]), float(pts[-1])
    w = t0
    while w < end:
        a, b = np.searchsorted(pts, w), np.searchsorted(pts, w + win)
        if b > a and float(score[a:b].mean()) > motion:
            nk = sum(1 for x in kept_t if w <= x < w + win)
            if nk < 2:
                if out and abs(out[-1]["end"] - w) < 1e-6:
                    out[-1]["end"] = round(w + win, 2)
                else:
                    out.append({"start": round(w, 2), "end": round(w + win, 2)})
        w += win
    return out


def _frame_name(t: float) -> str:
    return f"t{int(round(t * 1000)):09d}.jpg"


def extract(video: Path, kept: list[dict], width: int, height: int, out_dir: Path, workers: int = 8) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    scale = f"scale={FRAME_LONG_EDGE}:-2" if width >= height else f"scale=-2:{FRAME_LONG_EDGE}"

    def one(k):
        dst = out_dir / _frame_name(k["t"])
        k["path"] = str(dst)
        if dst.exists():
            return
        tmp = dst.with_name("." + dst.name)
        cmd = ["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-ss", f"{max(0.0, k['t'] - 0.0005):.4f}",
               "-i", str(video), "-map", "0:v:0", "-frames:v", "1", "-vf", scale, "-q:v", "3", "-f", "image2", str(tmp)]
        subprocess.run(cmd, capture_output=True)
        if tmp.exists():
            tmp.replace(dst)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(one, kept))
    missing = [k for k in kept if not Path(k["path"]).exists()]
    if missing:
        log(f"extract: {len(missing)} frames failed (first at {missing[0]['t']}s); dropping them")
        kept[:] = [k for k in kept if Path(k["path"]).exists()]


def run_scan(video: Path, probe: dict, run_dir: Path) -> dict:
    v = probe["video"]
    return scan(video, v["width"], v["height"], run_dir / "video" / "scan.npz")


def run_select(video: Path, probe: dict, run_dir: Path, fps: float | None, kind: str | None) -> dict:
    v = probe["video"]
    d = np.load(run_dir / "video" / "scan.npz")
    region_thr = 6.0 if kind == "tutorial" else 10.0
    sel = select(d["pts"], d["score"], d["dhash"], d["thumbs"], probe["duration"], fps=fps, region_thr=region_thr)
    extract(video, sel["kept"], v["width"], v["height"], run_dir / "frames")
    write_json(run_dir / "video" / "selection.json", sel)
    return {"frames_scanned": sel["n_frames"], "shots": len(sel["shots"]), "kept": len(sel["kept"]),
            "fps": sel["fps"], "budget": sel["budget"], "fps_scale": sel["fps_scale"],
            "coverage_gaps": len(sel["coverage_gaps"])}
