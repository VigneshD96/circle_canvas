# usage: python3 -I gen_image.py OUT.png MODEL "prompt" ref1.jpg [ref2 ...]
import sys, json, base64, urllib.request, os
out, model, prompt, refs = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
content = [{"type": "text", "text": prompt}]
for r in refs:
    mime = 'image/png' if r.endswith('.png') else 'image/jpeg'
    content.append({"type": "image_url", "image_url": {"url": f"data:{mime};base64," + base64.b64encode(open(r, 'rb').read()).decode()}})
body = {"model": model, "messages": [{"role": "user", "content": content}], "modalities": ["image", "text"], "image_config": {"aspect_ratio": "9:16"}, "usage": {"include": True}}
req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(body).encode(),
                             headers={"Authorization": "Bearer proxy-injected", "Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=300) as r:
    d = json.load(r)
msg = d["choices"][0]["message"]
imgs = msg.get("images") or []
if not imgs:
    print("NO IMAGE:", json.dumps(d)[:800]); sys.exit(1)
url = imgs[0]["image_url"]["url"]
open(out, "wb").write(base64.b64decode(url.split(",", 1)[1]))
print("saved", out, "cost", d.get("usage", {}).get("cost"))
