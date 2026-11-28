import subprocess, os
S = '/tmp/claude-0/-home-user-circle-canvas/0149c0f9-3df3-5805-89ac-9ce1c4ce0889/scratchpad/ep2ai'
os.chdir(S); os.makedirs('seg', exist_ok=True)
CUTS = [0, 2.375, 4.667, 6.292, 7.833, 9.375, 11.667, 16.458, 18.708, 21.25, 23.833, 25.875, 28.083, 32.917, 37.542, 37.292, 44.667, 49.333, 56.417, 59]
FR = [round(c * 24) for c in CUTS]
INOFF = {9: 0.95, 11: 0.3}            # skip the start of these clips (shot numbers, 1-based)
TAIL = {9: 3, 18: 12}                 # extra frames for the dissolve (9->10) and the end-card fade (18->19)
lens = []
for i in range(19):
    n = i + 1; frames = FR[i + 1] - FR[i] + TAIL.get(n, 0); lens.append(frames)
    if os.path.exists(f'seg/s{n:02d}.mp4'): continue
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(INOFF.get(n, 0)), '-i', f'clips/c{n:02d}.mp4', '-frames:v', str(frames), '-an',
                    '-vf', 'fps=24,scale=1080:1944:flags=lanczos,crop=1080:1920:0:12,unsharp=5:5:0.5,format=yuv420p,setsar=1',
                    '-c:v', 'libx264', '-crf', '14', '-preset', 'medium', f'seg/s{n:02d}.mp4'], check=True)
# picture: hard cuts, a 3-frame dissolve into the rooftop, a 0.5 s fade into the end card
inp = sum([['-i', f'seg/s{n:02d}.mp4'] for n in range(1, 20)], [])
d = lambda f: f / 24
fc = ''.join(f'[{i}:v]' for i in range(0, 8)) + 'concat=n=8:v=1:a=0[A];'
fc += f'[8:v][9:v]xfade=transition=fade:duration={d(3):.5f}:offset={d(lens[8] - 3):.5f}[B];'
fc += ''.join(f'[{i}:v]' for i in range(10, 17) if i != 12) + 'concat=n=6:v=1:a=0[C];'   # shot 13 removed
fc += f'[17:v][18:v]xfade=transition=fade:duration={d(12):.5f}:offset={d(lens[17] - 12):.5f}[D];'
fc += '[A][B][C][D]concat=n=4:v=1:a=0[pic];'
# overlays: caption (fades out with the end card), two sliding bubbles, end-card title (fades in)
fc += '[19:v]format=rgba,fade=t=out:st=51.584:d=0.5:alpha=1[cap];'
fc += '[20:v]format=rgba,fade=t=in:st=51.584:d=0.5:alpha=1[ttl];'
fc += '[pic][cap]overlay=0:0:shortest=1[p1];'
# "aaya papaaa??": slides in from the left at 21.6 s, held until the cut at 23.833
fc += "[p1][21:v]overlay=x='if(lt(t,21.6),-700,if(lt(t,21.85),-700+(560+700)*(1-pow(1-(t-21.6)/0.25,3)),560))-350':y=640:enable='between(t,21.6,23.833)'[p2];"
# "thank youuu": slides in from the right at 36.167 s, held until the cut at 37.292
fc += "[p2][22:v]overlay=x='if(lt(t,36.167),1780,if(lt(t,36.417),1780-(1780-800)*(1-pow(1-(t-36.167)/0.25,3)),800))-350':y=600:enable='between(t,36.167,37.292)'[p3];"
fc += '[p3][ttl]overlay=0:0:enable=\'gte(t,51.567)\'[out]'
cmd = ['ffmpeg', '-v', 'error', '-y'] + inp + ['-loop', '1', '-framerate', '24', '-i', 'ov/caption.png', '-loop', '1', '-framerate', '24', '-i', 'ov/title.png',
       '-loop', '1', '-framerate', '24', '-i', 'ov/aaya.png', '-loop', '1', '-framerate', '24', '-i', 'ov/thanks.png',
       '-filter_complex', fc, '-map', '[out]', '-t', '54.1667', '-r', '24', '-c:v', 'libx264', '-crf', '15', '-preset', 'slow', '-pix_fmt', 'yuv420p', 'picture_v3.mp4']
subprocess.run(cmd, check=True)

print('done')
