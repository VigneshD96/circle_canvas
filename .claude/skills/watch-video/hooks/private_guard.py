#!/usr/bin/env python3
"""PreToolUse guard for /watch-video: while a PRIVATE (or unsure) video is being watched in this Claude session,
block web tools so nothing about the video can leak into a search query or fetched URL.

Registered in ~/.claude/settings.json (see README). Reads the per-session marker written by
`watch.py intake --session ${CLAUDE_SESSION_ID}`. Sessions without a marker are never affected.
Stdlib only, fast, and fails OPEN on its own errors (a broken guard must not break Claude Code).
"""
import json
import os
import re
import sys
import time
from pathlib import Path

MARKER = Path(os.environ.get("WATCH_VIDEO_CACHE", "~/.cache/watch-video")).expanduser() / "active.json"
TTL_S = 12 * 3600
WEB_NAME = re.compile(r"(?i)(web|search|fetch|browser|navigate|crawl|scrape|google|http)")
BASH_NET = re.compile(r"(?i)\b(curl|wget|httpie|aria2c|yt-dlp)\b|https?://")


def is_web(tool: str, tool_input: dict) -> bool:
    if tool in ("WebSearch", "WebFetch"):
        return True
    if tool.startswith(("mcp__claude-in-chrome__", "mcp__plugin_playwright", "mcp__playwright")):
        return True
    if tool.startswith("mcp__") and WEB_NAME.search(tool):
        return True
    if tool == "Bash" and BASH_NET.search(str(tool_input.get("command", ""))):
        return True
    return False


def main() -> None:
    try:
        ev = json.load(sys.stdin)
        tool = ev.get("tool_name", "")
        if not is_web(tool, ev.get("tool_input") or {}):
            return
        sessions = (json.loads(MARKER.read_text()) if MARKER.exists() else {}).get("sessions", {})
        entry = sessions.get(ev.get("session_id", "")) or sessions.get("_any")
        if not entry or time.time() - entry.get("at", 0) > TTL_S or entry.get("visibility") == "public":
            return
        reason = (f"watch-video: this session is watching a video marked '{entry.get('visibility')}' "
                  f"({entry.get('run_dir', '')}). Web tools are blocked so nothing about it leaves the machine. "
                  "If the user confirms the video is public, run `watch.py intake <video> --visibility public "
                  "--session <id>`; to end the watch, run `watch.py release --session <id>`.")
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                                 "permissionDecisionReason": reason}}))
    except Exception:
        return  # fail open


if __name__ == "__main__":
    main()
