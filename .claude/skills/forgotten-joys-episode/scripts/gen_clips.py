#!/usr/bin/env python3
"""Animate each still into a clip with an OpenRouter video model (default heygen/heygen-video-1, 480p).

usage: python3 -I gen_clips.py EPISODE_DIR [--only 3,7] [--parallel 6]
Writes EPISODE_DIR/clips/cNN.mp4 with the generated audio REMOVED (HeyGen Video 1 always renders audio
and rejects generate_audio=false). The still is sent inline as the first frame (a data URL works).
Do not combine frame_images with input_references: HeyGen rejects that combination.
"""
import sys, os, json, base64, time, io, subprocess, urllib.request, urllib.error, concurrent.futures, argparse
from PIL import Image
KEEP = (" Static locked camera, no zoom, no pan, no cuts. Keep the hand-drawn storybook art style, paper texture, colours, "
        "characters and composition exactly as in the image. No new characters, no text.")

def run(src, out, prompt, dur, model, res, aspect):
    key = os.environ.get("OPENROUTER_API_KEY", "proxy-injected")
    H = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    buf = io.BytesIO(); Image.open(src).convert('RGB').save(buf, 'JPEG', quality=92)
    body = {"model": model, "prompt": prompt, "duration": dur, "resolution": res, "aspect_ratio": aspect,
            "frame_images": [{"type": "image_url", "frame_type": "first_frame", "image_url": {"url": "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()}}]}
    def call(u, data=None):
        req = urllib.request.Request(u, data=json.dumps(data).encode() if data else None, headers=H, method='POST' if data else 'GET')
        try:
            with urllib.request.urlopen(req, timeout=120) as r: return r.read()
        except urllib.error.HTTPError as e: raise RuntimeError(f"HTTP {e.code} {e.read()[:300]!r}")
    j = json.loads(call("https://openrouter.ai/api/v1/videos", body)); jid = j["id"]; t0 = time.time()
    while True:
        time.sleep(10); st = json.loads(call(f"https://openrouter.ai/api/v1/videos/{jid}"))
        if st["status"] in ("completed", "failed", "cancelled", "expired"): break
        if time.time() - t0 > 900: return f"{out}: TIMEOUT job {jid} (do not resubmit blindly; poll it again)"
    if st["status"] != "completed": return f"{out}: {st['status']} {json.dumps(st)[:300]}"
    raw = call(st.get("unsigned_urls", [f"https://openrouter.ai/api/v1/videos/{jid}/content"])[0])
    tmp = out + '.with_audio.mp4'; open(tmp, 'wb').write(raw)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-c', 'copy', '-an', out], check=True); os.remove(tmp)
    return f"saved {out} job {jid} cost {(st.get('usage') or {}).get('cost')}"

def main():
    a = argparse.ArgumentParser(); a.add_argument('ep'); a.add_argument('--only'); a.add_argument('--parallel', type=int, default=6)
    o = a.parse_args(); ep = json.load(open(os.path.join(o.ep, 'episode.json'))); os.makedirs(os.path.join(o.ep, 'clips'), exist_ok=True)
    only = {int(x) for x in o.only.split(',')} if o.only else None
    v = ep.get('video', {}); model, res = v.get('model', 'heygen/heygen-video-1'), v.get('resolution', '480p')
    jobs = []
    for i, sh in enumerate(ep['shots'], 1):
        if only and i not in only: continue
        src = os.path.join(o.ep, sh.get('still') or f'stills/s{i:02d}.png')
        dur = max(5, min(30, int(-(-sh['frames'] // 24)) + 1))   # whole seconds covering the shot, HeyGen minimum 5
        jobs.append((src, os.path.join(o.ep, 'clips', f'c{i:02d}.mp4'), sh['motion_prompt'] + KEEP, dur))
    with concurrent.futures.ThreadPoolExecutor(o.parallel) as ex:
        for r in ex.map(lambda j: run(*j, model, res, ep.get('aspect_ratio', '9:16')), jobs): print(r, flush=True)

if __name__ == '__main__': main()
