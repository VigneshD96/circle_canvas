"""Identity hints for the intake questions. Hints only: never used to decide public/private."""
from __future__ import annotations

import re
from pathlib import Path

_SXE = re.compile(r"(?i)\bS(\d{1,2})[ ._-]?E(\d{1,3})\b")
_NXN = re.compile(r"(?i)(?<![\d])(\d{1,2})x(\d{2,3})(?![\d])")
_EP = re.compile(r"(?i)\b(?:ep(?:isode)?|e)[ ._-]?(\d{1,4})\b")
_YTID = re.compile(r"\[([A-Za-z0-9_-]{11})\]")
_DATE = re.compile(r"\b((?:19|20)\d{2})[-_.]?(0[1-9]|1[0-2])[-_.]?(0[1-9]|[12]\d|3[01])\b")
_JUNK = re.compile(
    r"(?i)\b(1080p|720p|2160p|480p|4k|x26[45]|h\.?26[45]|hevc|web[- .]?dl|webrip|bluray|brrip|hdtv|aac\d?|"
    r"ddp?5\.1|dts|10bit|proper|repack|remux|amzn|nf|hulu|dsnp|hmax)\b.*$"
)


def _clean_title(s: str) -> str:
    s = _JUNK.sub("", s)
    s = re.sub(r"[._]+", " ", s)
    s = re.sub(r"\s+-\s*$|\(\s*\)|\[\s*\]", "", s)
    return re.sub(r"\s{2,}", " ", s).strip(" -_")


def hints(path: str | Path, tags: dict | None = None) -> dict:
    stem = Path(path).stem
    tags = {k.lower(): v for k, v in (tags or {}).items()}
    h: dict = {"filename": Path(path).name}
    m = _SXE.search(stem) or _NXN.search(stem)
    if m:
        h["season"], h["episode"] = int(m.group(1)), int(m.group(2))
        h["series"] = _clean_title(stem[: m.start()]) or None
        rest = _clean_title(stem[m.end():])
        if rest:
            h["episode_title"] = rest
        h["kind_guess"] = "tv_episode"
    else:
        e = _EP.search(stem)
        if e:
            h["episode"] = int(e.group(1))
            h["series"] = _clean_title(stem[: e.start()]) or None
            h["kind_guess"] = "episode (podcast or show)"
    y = _YTID.search(stem)
    if y:
        h["youtube_id"] = y.group(1)
        h["title"] = _clean_title(stem[: y.start()])
    d = _DATE.search(stem)
    if d:
        h["date"] = f"{d.group(1)}-{d.group(2)}-{d.group(3)}"
    if "title" not in h and not m:
        h["title"] = _clean_title(stem)
    for k in ("title", "show", "artist", "album_artist", "comment", "description", "purl", "date",
              "season_number", "episode_id", "episode_sort", "network", "synopsis"):
        if tags.get(k):
            h[f"tag_{k}"] = str(tags[k])[:300]
    parts = []
    if h.get("series"):
        parts.append(h["series"])
    if h.get("season"):
        parts.append(f"S{h['season']:02d}E{h['episode']:02d}")
    elif h.get("episode"):
        parts.append(f"episode {h['episode']}")
    if h.get("episode_title"):
        parts.append(f"“{h['episode_title']}”")
    if not parts and h.get("tag_title"):
        parts.append(h["tag_title"])
    if not parts and h.get("title"):
        parts.append(h["title"])
    h["guess"] = " ".join(parts) or None
    return h
