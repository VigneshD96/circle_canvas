#!/usr/bin/env python3
"""Cut clips to the shot timing, join them, add caption / bubbles / end-card title, lay in the music, export.

usage: python3 -I assemble.py EPISODE_DIR        -> EPISODE_DIR/episode.mp4
Timing comes from episode.json: each shot's `frames` (at 24 fps) and optional `in_offset` (seconds skipped at
the start of its clip) and `transition_in` ("cut" default, "dissolve3" = 3-frame dissolve, "fade12" = 0.5 s fade).
The last shot is the end card; the caption fades out and the title fades in over its transition.
"""
import sys, os, json, subprocess, shutil
FPS = 24
TR = {"cut": 0, "dissolve3": 3, "fade12": 12}
def sh(cmd): subprocess.run(cmd, check=True)
def main():
    ep_dir = sys.argv[1]; ep = json.load(open(os.path.join(ep_dir, 'episode.json'))); shots = ep['shots']
    seg = os.path.join(ep_dir, 'seg'); os.makedirs(seg, exist_ok=True)
    # 1. segments: each shot's clip trimmed to its frames, plus overlap frames if the NEXT shot transitions in
    starts, t = [], 0
    for i, s in enumerate(shots):
        nxt = TR[shots[i + 1].get('transition_in', 'cut')] if i + 1 < len(shots) else 0
        s['_len'] = s['frames'] + nxt; starts.append(t); t += s['frames']
        sh(['ffmpeg', '-v', 'error', '-y', '-ss', str(s.get('in_offset', 0)), '-i', os.path.join(ep_dir, 'clips', f'c{i+1:02d}.mp4'),
            '-frames:v', str(s['_len']), '-an', '-vf', 'fps=24,scale=1080:1944:flags=lanczos,crop=1080:1920:0:12,unsharp=5:5:0.5,format=yuv420p,setsar=1',
            '-c:v', 'libx264', '-crf', '14', '-preset', 'medium', os.path.join(seg, f's{i+1:02d}.mp4')])
        got = int(subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v', '-show_entries', 'stream=nb_read_frames', '-of', 'csv=p=0', os.path.join(seg, f's{i+1:02d}.mp4')], capture_output=True, text=True).stdout.strip())
        if got < s['_len']: print(f'WARNING shot {i+1}: clip has only {got} frames, needs {s["_len"]} (generate a longer clip or lower in_offset)')
    total = t; end_start = starts[-1] / FPS; end_tr = TR[shots[-1].get('transition_in', 'fade12')] / FPS
    # 2. join: concat for cuts, xfade for dissolves/fades
    inp = sum([['-i', os.path.join(seg, f's{i+1:02d}.mp4')] for i in range(len(shots))], [])
    # groups of consecutive hard cuts are concatenated; groups are joined with xfade (one transition per join)
    groups = [[0]]
    for i in range(1, len(shots)):
        if TR[shots[i].get('transition_in', 'cut')]: groups.append([i])
        else: groups[-1].append(i)
    fc = []
    for gi, g in enumerate(groups):
        fc.append(''.join(f'[{i}:v]' for i in g) + f'concat=n={len(g)}:v=1:a=0[g{gi}]')
    cur, cur_len = '[g0]', sum(shots[i]['_len'] for i in groups[0])
    for gi in range(1, len(groups)):
        n = TR[shots[groups[gi][0]].get('transition_in')]
        fc.append(f'{cur}[g{gi}]xfade=transition=fade:duration={n/FPS:.5f}:offset={(cur_len - n)/FPS:.5f}[x{gi}]')
        cur = f'[x{gi}]'; cur_len = cur_len - n + sum(shots[i]['_len'] for i in groups[gi])
    # 3. overlays
    ov = os.path.join(ep_dir, 'overlays'); k = len(shots)
    extra = ['-loop', '1', '-framerate', '24', '-i', os.path.join(ov, 'caption.png'), '-loop', '1', '-framerate', '24', '-i', os.path.join(ov, 'title.png')]
    fc.append(f'[{k}:v]format=rgba,fade=t=out:st={end_start:.3f}:d={end_tr:.3f}:alpha=1[cap]')
    fc.append(f'[{k+1}:v]format=rgba,fade=t=in:st={end_start:.3f}:d={end_tr:.3f}:alpha=1[ttl]')
    fc.append(f'{cur}[cap]overlay=0:0:shortest=1[o0]'); last = '[o0]'
    for bi, b in enumerate(ep.get('bubbles', [])):
        extra += ['-loop', '1', '-framerate', '24', '-i', os.path.join(ov, f'bubble{bi}.png')]
        t0 = starts[b['shot'] - 1] / FPS + b['at']; t1 = (starts[b['shot']] if b['shot'] < len(shots) else total) / FPS
        x = b['x']; off = -700 if b.get('from', 'left') == 'left' else 1780
        xe = f"if(lt(t,{t0}),{off},if(lt(t,{t0+0.25}),{off}+({x}-({off}))*(1-pow(1-(t-{t0})/0.25,3)),{x}))-350"
        fc.append(f"{last}[{k+2+bi}:v]overlay=x='{xe}':y={b['y']}:enable='between(t,{t0:.3f},{t1:.3f})'[o{bi+1}]"); last = f'[o{bi+1}]'
    fc.append(f"{last}[ttl]overlay=0:0:enable='gte(t,{end_start - 0.02:.3f})'[out]")
    pic = os.path.join(ep_dir, 'picture.mp4')
    sh(['ffmpeg', '-v', 'error', '-y'] + inp + extra + ['-filter_complex', ';'.join(fc), '-map', '[out]', '-frames:v', str(total), '-r', '24',
        '-c:v', 'libx264', '-crf', '15', '-preset', 'slow', '-pix_fmt', 'yuv420p', pic])
    # 4. audio: the supplied track from `start`, cut to length, faded, normalised to -14 LUFS (two passes)
    dur = total / FPS; out = os.path.join(ep_dir, 'episode.mp4'); a = ep.get('audio')
    if not a: shutil.copy(pic, out); print('no audio configured; picture only'); return
    src = os.path.join(ep_dir, a['file']); tmp = os.path.join(ep_dir, 'audio_cut.wav'); fin = os.path.join(ep_dir, 'audio_final.wav')
    fo = a.get('fade_out', 1.6)
    loop = ['-stream_loop', '-1'] if a.get('loop') else []
    sh(['ffmpeg', '-v', 'error', '-y'] + loop + ['-ss', str(a.get('start', 0)), '-i', src, '-af', f'atrim=0:{dur},afade=t=in:d=0.15,afade=t=out:st={dur-fo}:d={fo},apad=pad_dur=0.3', '-ac', '2', '-ar', '44100', tmp])
    I = float([l for l in subprocess.run(['ffmpeg', '-i', tmp, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr.splitlines() if l.strip().startswith('I:')][-1].split()[1])
    sh(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', f'volume={a.get("lufs", -14) - I}dB,alimiter=limit=0.9', fin])
    def lufs(f): return float([l for l in subprocess.run(['ffmpeg', '-i', f, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr.splitlines() if l.strip().startswith('I:')][-1].split()[1])
    for _ in range(2):   # mux, measure the encoded result, correct the residual (limiter/AAC shift it a little)
        sh(['ffmpeg', '-v', 'error', '-y', '-i', pic, '-i', fin, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', f'{dur:.4f}', out])
        err = a.get('lufs', -14) - lufs(out)
        if abs(err) < 0.3: break
        fin2 = fin.replace('.wav', '_adj.wav'); sh(['ffmpeg', '-v', 'error', '-y', '-i', fin, '-af', f'volume={err}dB', fin2]); os.replace(fin2, fin)
    print(f'wrote {out}: {total} frames, {dur:.2f} s')
if __name__ == '__main__': main()
