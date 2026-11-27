#!/bin/bash
S=/tmp/claude-0/-home-user-circle-canvas/0149c0f9-3df3-5805-89ac-9ce1c4ce0889/scratchpad/ep2ai; cd $S
python3 -c "
import sys,subprocess; sys.path.insert(0,'tools'); from motions import *
n=int(sys.argv[1]); p,d=M[n]
r=subprocess.run(['python3','-I','tools/gen_video.py',f'shots/s{n:02d}.png',f'clips/c{n:02d}.mp4',p+KEEP,str(d)],capture_output=True,text=True)
print(n, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else '', r.stderr.strip()[-200:])" "$1"
