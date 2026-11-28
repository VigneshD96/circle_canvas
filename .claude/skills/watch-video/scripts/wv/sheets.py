"""Contact sheets: kept frames packed into labelled grids that the agent reads as images.

Layout by aspect + kind (long edge <= 1568 px so nothing is downscaled by the model):
  landscape 3x3 tiles of 480 px wide | portrait 4x2 of 270 px wide | square 3x3 of 400 px | screen (tutorial) 2x2 of 720 px
Every tile carries its source timestamp; shot starts carry a CUT marker. Image cost ~= w*h/750 tokens.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .util import fmt_short, fmt_ts

HEADER_H = 30
MIN_FONT_PX = 16
_FONT_PATHS = ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf",
               "/System/Library/Fonts/Helvetica.ttc"]


def _font(size: int):
    for p in _FONT_PATHS:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                continue
    return ImageFont.load_default(size=size)


def layout(aspect: float, kind: str | None) -> dict:
    if kind == "tutorial" and aspect >= 1.2:
        cols, rows, tw = 2, 2, 720
    elif aspect >= 1.2:
        cols, rows, tw = 3, 3, 480
    elif aspect <= 0.8:
        cols, rows, tw = 4, 2, 270
    else:
        cols, rows, tw = 3, 3, 400
    th = int(round(tw / aspect))
    font_px = max(MIN_FONT_PX, tw // 22)
    return {"cols": cols, "rows": rows, "tile_w": tw, "tile_h": th, "per_sheet": cols * rows, "font_px": font_px,
            "sheet_w": cols * tw, "sheet_h": rows * th + HEADER_H}


def est_tokens(w: int, h: int) -> int:
    return int(w * h / 750)


def _tile(path: str, lay: dict) -> Image.Image:
    im = Image.open(path).convert("RGB")
    im.thumbnail((lay["tile_w"], lay["tile_h"]), Image.LANCZOS)
    canvas = Image.new("RGB", (lay["tile_w"], lay["tile_h"]), (0, 0, 0))
    canvas.paste(im, ((lay["tile_w"] - im.width) // 2, (lay["tile_h"] - im.height) // 2))
    return canvas


def _label(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, font, fg=(255, 255, 255), bg=(0, 0, 0)):
    l, t, r, b = draw.textbbox((x, y), text, font=font)
    draw.rectangle((l - 3, t - 2, r + 3, b + 2), fill=bg)
    draw.text((x, y), text, font=font, fill=fg)


def render(tiles: list[dict], header: str, lay: dict, out: Path, tag_fn=None) -> tuple[int, int]:
    n = len(tiles)
    rows = (n + lay["cols"] - 1) // lay["cols"]
    w, h = lay["cols"] * lay["tile_w"], rows * lay["tile_h"] + HEADER_H
    sheet = Image.new("RGB", (w, h), (18, 18, 18))
    draw = ImageDraw.Draw(sheet)
    font = _font(lay["font_px"])
    hfont = _font(max(MIN_FONT_PX, 17))
    _label(draw, 8, 6, header, hfont, bg=(18, 18, 18))
    for k, t in enumerate(tiles):
        x = (k % lay["cols"]) * lay["tile_w"]
        y = HEADER_H + (k // lay["cols"]) * lay["tile_h"]
        sheet.paste(_tile(t["path"], lay), (x, y))
        _label(draw, x + 6, y + 5, fmt_short(t["t"]), font)
        tag = tag_fn(t) if tag_fn else ("CUT" if t.get("reason") == "cut" else None)
        if tag:
            tw = draw.textlength(tag, font=font)
            _label(draw, int(x + lay["tile_w"] - tw - 9), y + 5, tag, font, fg=(0, 0, 0), bg=(255, 214, 0))
        draw.rectangle((x, y, x + lay["tile_w"] - 1, y + lay["tile_h"] - 1), outline=(60, 60, 60))
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_name("." + out.name)
    sheet.save(tmp, "JPEG", quality=85)
    tmp.replace(out)
    return w, h


def build_sheets(kept: list[dict], chunks: list[dict], lay: dict, out_dir: Path) -> list[dict]:
    """Sheets never straddle chunks. Returns the sheet index."""
    index, sid = [], 0
    for ch in chunks:
        frames = [k for k in kept if ch["start"] <= k["t"] < ch["end"]]
        for i in range(0, len(frames), lay["per_sheet"]):
            group = frames[i:i + lay["per_sheet"]]
            sid += 1
            path = out_dir / f"sheet_{sid:03d}.jpg"
            header = (f"sheet {sid:03d} | chunk {ch['id']:02d} | {fmt_ts(group[0]['t'])} - {fmt_ts(group[-1]['t'])}"
                      f" | {len(group)} frames")
            w, h = render(group, header, lay, path)
            index.append({"id": sid, "chunk": ch["id"], "path": str(path), "start": group[0]["t"], "end": group[-1]["t"],
                          "w": w, "h": h, "tokens": est_tokens(w, h),
                          "tiles": [{"t": g["t"], "reason": g["reason"], "shot": g["shot"], "frame": g["path"]} for g in group]})
    return index


def storyboard(kept: list[dict], duration: float, lay: dict, out_dir: Path, max_tiles: int = 54) -> list[dict]:
    """Even spread over the whole video (prefers shot starts) for the global skim."""
    if not kept:
        return []
    step = duration / max_tiles
    picks, used = [], set()
    for k in range(max_tiles):
        lo, hi = k * step, (k + 1) * step
        cands = [f for f in kept if lo <= f["t"] < hi and f["idx"] not in used]
        if not cands:
            continue
        cuts = [f for f in cands if f["reason"] == "cut"]
        f = (cuts or cands)[0]
        used.add(f["idx"])
        picks.append(f)
    out = []
    for i in range(0, len(picks), lay["per_sheet"]):
        group = picks[i:i + lay["per_sheet"]]
        n = i // lay["per_sheet"] + 1
        path = out_dir / f"storyboard_{n:02d}.jpg"
        w, h = render(group, f"storyboard {n:02d} | {fmt_ts(group[0]['t'])} - {fmt_ts(group[-1]['t'])}", lay, path)
        out.append({"id": n, "path": str(path), "start": group[0]["t"], "end": group[-1]["t"], "tokens": est_tokens(w, h)})
    return out


def context_strip(prev: list[dict], nxt: list[dict], lay: dict, out: Path) -> dict | None:
    tiles = [dict(t, _tag="PREV CHUNK") for t in prev] + [dict(t, _tag="NEXT CHUNK") for t in nxt]
    if not tiles:
        return None
    small = dict(lay, cols=len(tiles), tile_w=lay["tile_w"] * 2 // 3, tile_h=lay["tile_h"] * 2 // 3)
    small["font_px"] = max(MIN_FONT_PX, small["tile_w"] // 22)
    w, h = render(tiles, "boundary context (read-only, not your range)", small, out, tag_fn=lambda t: t["_tag"])
    return {"path": str(out), "tokens": est_tokens(w, h)}
