# Reference videos

Reference Shorts broken down with the project-level `rea-video` skill (`.claude/skills/rea-video`).
Each video is stored as two parts (uploads were capped at 30 MB). Merge them losslessly with:

```bash
cd references/videos/dog_door
printf "file 'dog_door_part1.mp4'\nfile 'dog_door_part2.mp4'\n" > list.txt
ffmpeg -f concat -safe 0 -i list.txt -c copy dog_door.mp4
```

| Folder | Length | Format | Source |
|---|---|---|---|
| `dog_door/` | 109 s | 1080×1920, 30 fps | https://youtube.com/shorts/H6-VW-HNA8M |
| `flooded_basement/` | 71 s | 1080×1920, 24 fps | user upload |
| `potatoes/` | 52 s | 1080×1920, 30 fps | user upload ("Why Factories Shoot Potatoes Through Knives"), single file |
