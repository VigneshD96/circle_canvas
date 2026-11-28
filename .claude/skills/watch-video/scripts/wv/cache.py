"""Run directory, stage fingerprints, locks.

A stage is skipped only when its fingerprint (name + params + pipeline version + upstream fingerprints)
matches and all its outputs exist. Changing any param or upstream output changes every descendant's
fingerprint, so descendants re-run automatically.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from . import PIPELINE_VERSION
from .util import log, read_json, write_json

CACHE_ROOT = Path(os.environ.get("WATCH_VIDEO_CACHE", "~/.cache/watch-video")).expanduser()
ACTIVE_MARKER = CACHE_ROOT / "active.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def source_sig(path: Path) -> dict:
    st = path.stat()
    return {"path": str(path.resolve()), "size": st.st_size, "mtime_ns": st.st_mtime_ns}


def _slug(path: Path) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", path.stem.lower()).strip("-")
    return s[:40] or "video"


class Run:
    def __init__(self, run_dir: Path):
        self.dir = Path(run_dir)
        self._lock = threading.Lock()
        self.meta = read_json(self.dir / "meta.json", {}) or {}
        self.meta.setdefault("stages", {})

    # ---- construction -------------------------------------------------
    @classmethod
    def for_video(cls, video: Path, create: bool = True) -> "Run":
        video = Path(video).expanduser().resolve()
        sig = source_sig(video)
        key = hashlib.sha1(f"{sig['path']}|{sig['size']}|{sig['mtime_ns']}".encode()).hexdigest()[:12]
        run_dir = CACHE_ROOT / f"{key}-{_slug(video)}"
        if create:
            run_dir.mkdir(parents=True, exist_ok=True)
        r = cls(run_dir)
        if create and not r.meta.get("run_id"):
            r.meta.update({"run_id": run_dir.name, "source": sig, "created": _now(), "pipeline": PIPELINE_VERSION})
            r.save()
        return r

    @classmethod
    def resolve(cls, target: str | Path) -> "Run":
        """Accept a run dir or a video path."""
        t = Path(target).expanduser()
        if t.is_dir() and (t / "meta.json").exists():
            return cls(t)
        if not t.exists():
            raise FileNotFoundError(f"not found: {t}")
        return cls.for_video(t)

    # ---- paths / meta -------------------------------------------------
    def p(self, *parts) -> Path:
        return self.dir.joinpath(*parts)

    @property
    def video(self) -> Path:
        return Path(self.meta["source"]["path"])

    @property
    def run_id(self) -> str:
        return self.meta["run_id"]

    def save(self) -> None:
        with self._lock:
            write_json(self.dir / "meta.json", self.meta)

    def intake(self) -> dict:
        return read_json(self.p("intake.json"), {}) or {}

    # ---- stages -------------------------------------------------------
    def fingerprint(self, name: str, deps: list[str], params: dict) -> str:
        dep_fps = {}
        for d in deps:
            st = self.meta["stages"].get(d)
            if not st:
                raise RuntimeError(f"stage {name} needs {d}, which has not run")
            dep_fps[d] = st["fp"]
        blob = json.dumps({"n": name, "v": PIPELINE_VERSION, "p": params, "d": dep_fps}, sort_keys=True, default=str)
        return hashlib.sha1(blob.encode()).hexdigest()[:16]

    def is_fresh(self, name: str, deps: list[str], params: dict, outputs: list[str]) -> bool:
        st = self.meta["stages"].get(name)
        try:
            fp = self.fingerprint(name, deps, params)
        except RuntimeError:
            return False
        return bool(st and st["fp"] == fp and all(self.p(o).exists() for o in outputs))

    def stage(self, name: str, deps: list[str], params: dict, outputs: list[str], fn, force: bool = False) -> bool:
        """Run fn() unless fresh. Returns True if it ran."""
        fp = self.fingerprint(name, deps, params)
        st = self.meta["stages"].get(name)
        if not force and st and st["fp"] == fp and all(self.p(o).exists() for o in outputs):
            log(f"{name}: cached")
            return False
        log(f"{name}: running")
        t0 = time.time()
        fn()
        missing = [o for o in outputs if not self.p(o).exists()]
        if missing:
            raise RuntimeError(f"stage {name} did not write {missing}")
        with self._lock:
            self.meta["stages"][name] = {"fp": fp, "outputs": outputs, "secs": round(time.time() - t0, 1), "at": _now()}
        self.save()
        log(f"{name}: done in {time.time() - t0:.1f}s")
        return True


class FileLock:
    """Non-blocking exclusive lock on a file. Raises BlockingIOError if held."""

    def __init__(self, path: Path, wait: bool = False):
        self.path, self.wait, self.fd = Path(path), wait, None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.fd = os.open(self.path, os.O_CREAT | os.O_RDWR)
        fcntl.flock(self.fd, fcntl.LOCK_EX | (0 if self.wait else fcntl.LOCK_NB))
        os.ftruncate(self.fd, 0)
        os.write(self.fd, str(os.getpid()).encode())
        return self

    def __exit__(self, *a):
        fcntl.flock(self.fd, fcntl.LOCK_UN)
        os.close(self.fd)


def is_locked(path: Path) -> bool:
    if not Path(path).exists():
        return False
    fd = os.open(path, os.O_RDWR)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(fd, fcntl.LOCK_UN)
        return False
    except BlockingIOError:
        return True
    finally:
        os.close(fd)


def set_active(run: Run, visibility: str, session: str | None) -> None:
    """Marker read by hooks/private_guard.py: per Claude session, which video is being watched and its visibility."""
    from .util import read_json as _rj

    data = _rj(ACTIVE_MARKER, {}) or {}
    sessions = {k: v for k, v in (data.get("sessions") or {}).items() if time.time() - v.get("at", 0) < 7 * 86400}
    sessions[session or "_any"] = {"run_dir": str(run.dir), "visibility": visibility, "at": time.time()}
    write_json(ACTIVE_MARKER, {"sessions": sessions})
