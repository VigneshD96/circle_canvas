"""Small shared helpers: subprocess, atomic writes, time formatting, logging."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Privacy: no library telemetry. Set before any HF / pyannote import.
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
os.environ.setdefault("PYANNOTE_METRICS_ENABLED", "0")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")


def log(msg: str) -> None:
    """Progress lines go to stderr so stdout stays machine-readable."""
    print(f"[watch-video] {msg}", file=sys.stderr, flush=True)


def run(cmd: list[str], *, capture: bool = True, check: bool = True, **kw) -> subprocess.CompletedProcess:
    p = subprocess.run(cmd, capture_output=capture, text=True, **kw)
    if check and p.returncode != 0:
        tail = (p.stderr or "")[-2000:]
        raise RuntimeError(f"command failed ({p.returncode}): {' '.join(cmd[:6])} ...\n{tail}")
    return p


def atomic_write_bytes(path: Path, data: bytes) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def atomic_write_text(path: Path, text: str) -> None:
    atomic_write_bytes(path, text.encode("utf-8"))


def write_json(path: Path, obj) -> None:
    atomic_write_text(path, json.dumps(obj, indent=1, ensure_ascii=False, default=_json_default))


def read_json(path: Path, default=None):
    path = Path(path)
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _json_default(o):
    try:
        import numpy as np

        if isinstance(o, np.generic):
            return o.item()
        if isinstance(o, np.ndarray):
            return o.tolist()
    except ImportError:
        pass
    if isinstance(o, Path):
        return str(o)
    raise TypeError(f"not JSON serializable: {type(o)}")


def fmt_ts(sec: float, ms: bool = True) -> str:
    """12.345 -> '00:00:12.3' (tenths) ; ms=False -> '00:00:12'."""
    if sec is None:
        return "--:--:--"
    neg = sec < 0
    sec = abs(sec)
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    out = f"{h:02d}:{m:02d}:{s:04.1f}" if ms else f"{h:02d}:{m:02d}:{int(s):02d}"
    return ("-" if neg else "") + out


def fmt_short(sec: float) -> str:
    """Compact label for tiles: 'M:SS.s' or 'H:MM:SS'."""
    if sec >= 3600:
        return f"{int(sec // 3600)}:{int(sec % 3600 // 60):02d}:{int(sec % 60):02d}"
    return f"{int(sec // 60)}:{sec % 60:04.1f}"


def parse_ts(v) -> float:
    """Accept seconds or [[H:]M:]S(.f)."""
    if isinstance(v, (int, float)):
        return float(v)
    parts = str(v).strip().split(":")
    total = 0.0
    for p in parts:
        total = total * 60 + float(p)
    return total


def fmt_dur(sec: float) -> str:
    sec = int(round(sec))
    if sec >= 3600:
        return f"{sec // 3600}h{sec % 3600 // 60:02d}m{sec % 60:02d}s"
    if sec >= 60:
        return f"{sec // 60}m{sec % 60:02d}s"
    return f"{sec}s"


def hf_hub_dir() -> Path:
    return Path(os.environ.get("HF_HOME", "~/.cache/huggingface")).expanduser() / "hub"


def local_model(repo: str, rev: str | None = None) -> str:
    """Local snapshot folder of a downloaded model (no network calls), else the repo id (first download)."""
    base = hf_hub_dir() / f"models--{repo.replace('/', '--')}"
    if rev is None:
        ref = base / "refs" / "main"
        rev = ref.read_text().strip() if ref.exists() else None
    snap = base / "snapshots" / rev if rev else None
    return str(snap) if snap and snap.is_dir() else repo
