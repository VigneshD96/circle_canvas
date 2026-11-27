# usage: python3 -I gen_video.py FIRST_FRAME.png OUT.mp4 "motion prompt" [duration]
import sys, json, base64, time, urllib.request, io
from PIL import Image
src, out, prompt = sys.argv[1], sys.argv[2], sys.argv[3]
dur = int(sys.argv[4]) if len(sys.argv) > 4 else 5
H = {"Authorization": "Bearer proxy-injected", "Content-Type": "application/json"}
im = Image.open(src).convert('RGB'); buf = io.BytesIO(); im.save(buf, 'JPEG', quality=92)
url = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
body = {"model": "heygen/heygen-video-1", "prompt": prompt, "duration": dur, "resolution": "480p", "aspect_ratio": "9:16",
        "frame_images": [{"type": "image_url", "image_url": {"url": url}, "frame_type": "first_frame"}]}
def call(u, data=None):
    req = urllib.request.Request(u, data=json.dumps(data).encode() if data else None, headers=H, method='POST' if data else 'GET')
    try:
        with urllib.request.urlopen(req, timeout=120) as r: return r.read(), r.headers.get('content-type', '')
    except urllib.error.HTTPError as e: print('HTTP', e.code, e.read()[:600].decode(errors='ignore')); sys.exit(1)
raw, _ = call("https://openrouter.ai/api/v1/videos", body); j = json.loads(raw)
jid = j["id"]; print("job", jid, j.get("status"), flush=True)
t0 = time.time()
while True:
    time.sleep(10)
    raw, _ = call(f"https://openrouter.ai/api/v1/videos/{jid}"); st = json.loads(raw)
    if st["status"] in ("completed", "failed", "cancelled", "expired"): break
    if time.time() - t0 > 900: print("timeout"); sys.exit(1)
if st["status"] != "completed": print("FAILED", json.dumps(st)[:600]); sys.exit(1)
raw, ct = call(st.get("unsigned_urls", [f"https://openrouter.ai/api/v1/videos/{jid}/content"])[0])
open(out, "wb").write(raw)
print("saved", out, len(raw), "bytes; usage", json.dumps(st.get("usage") or st.get("cost") or {}), "in %.0fs" % (time.time() - t0))
