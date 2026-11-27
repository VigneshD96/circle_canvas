#!/bin/bash
S=/tmp/claude-0/-home-user-circle-canvas/0149c0f9-3df3-5805-89ac-9ce1c4ce0889/scratchpad/ep2ai; cd $S; mkdir -p shots
n=$1
python3 -I - "$n" <<'PY'
import sys,subprocess
sys.path.insert(0,'tools'); 
PY
python3 -c "
import sys; sys.path.insert(0,'tools'); from shots import *
n=int(sys.argv[1]); p,refs=SHOTS[n]
import subprocess
refs=[('refs/'+r if r.startswith('r_') else r) for r in refs]
r=subprocess.run(['python3','-I','tools/gen_image.py',f'shots/s{n:02d}.png','google/gemini-nano-banana-2.1',STYLE+p]+refs,capture_output=True,text=True)
print(n, r.stdout.strip(), r.stderr.strip()[-300:])
" "$n"
