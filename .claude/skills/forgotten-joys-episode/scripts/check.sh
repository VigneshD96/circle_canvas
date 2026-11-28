#!/bin/bash
# usage: check.sh EPISODE_DIR   -> frame count, duration, loudness, and a 1 fps contact sheet to look at
V="$1/episode.mp4"
ffprobe -v error -count_frames -show_entries stream=codec_type,width,height,nb_read_frames:format=duration -of compact "$V"
ffmpeg -i "$V" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):" | tail -2
ffmpeg -v error -y -i "$V" -vf "fps=1,scale=180:-1,tile=10x6" -frames:v 1 "$1/contact_sheet.png" && echo "contact sheet: $1/contact_sheet.png"
