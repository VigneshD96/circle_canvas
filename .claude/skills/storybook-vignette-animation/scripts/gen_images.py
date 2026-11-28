#!/usr/bin/env python3
"""Generate the character sheet(s) and shot stills for an episode through OpenRouter.

usage: python3 -I gen_images.py EPISODE_DIR [--only 3,7] [--sheets] [--parallel 6]
Reads EPISODE_DIR/episode.json, writes EPISODE_DIR/stills/sNN.png (and sheets/*.png).
The OpenRouter key is never read here: send the placeholder header and let the
environment's proxy inject the real key (or export OPENROUTER_API_KEY when run locally).
"""
import sys, os, json, base64, urllib.request, concurrent.futures, argparse
HERE = os.path.dirname(os.path.abspath(__file__)); SKILL = os.path.dirname(HERE)

def gen(out, model, prompt, refs, aspect):
    content = [{"type": "text", "text": prompt}]
    for r in refs:
        mime = 'image/png' if r.lower().endswith('.png') else 'image/jpeg'
        content.append({"type": "image_url", "image_url": {"url": f"data:{mime};base64," + base64.b64encode(open(r, 'rb').read()).decode()}})
    body = {"model": model, "messages": [{"role": "user", "content": content}], "modalities": ["image", "text"],
            "image_config": {"aspect_ratio": aspect}, "usage": {"include": True}}
    key = os.environ.get("OPENROUTER_API_KEY", "proxy-injected")
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r: d = json.load(r)
    imgs = d["choices"][0]["message"].get("images") or []
    if not imgs: return f"NO IMAGE {json.dumps(d)[:300]}"
    open(out, "wb").write(base64.b64decode(imgs[0]["image_url"]["url"].split(",", 1)[1]))
    return f"saved {out} cost {d.get('usage', {}).get('cost')}"

def resolve(ep_dir, r):
    for base in (ep_dir, SKILL):
        p = os.path.join(base, r)
        if os.path.exists(p): return p
    raise FileNotFoundError(r)

def main():
    a = argparse.ArgumentParser(); a.add_argument('ep'); a.add_argument('--only'); a.add_argument('--sheets', action='store_true'); a.add_argument('--parallel', type=int, default=6)
    o = a.parse_args(); ep = json.load(open(os.path.join(o.ep, 'episode.json')))
    style = open(os.path.join(SKILL, 'references', 'style_block.txt')).read().strip() + ' '
    chars = ep.get('characters', {}); model = ep.get('image_model', 'google/gemini-nano-banana-2.1')
    jobs = []
    if o.sheets:
        os.makedirs(os.path.join(o.ep, 'sheets'), exist_ok=True)
        for name, c in chars.items():
            if c.get('sheet_prompt'):
                jobs.append((os.path.join(o.ep, 'sheets', f'{name}.png'), style + c['sheet_prompt'], [resolve(o.ep, r) for r in c.get('sheet_refs', [])]))
    else:
        os.makedirs(os.path.join(o.ep, 'stills'), exist_ok=True)
        only = {int(x) for x in o.only.split(',')} if o.only else None
        for i, sh in enumerate(ep['shots'], 1):
            if only and i not in only: continue
            if sh.get('still'): continue          # supplied still, nothing to generate
            who = ''.join(chars[c]['look'] + ' ' for c in sh.get('cast', []) if c in chars)
            jobs.append((os.path.join(o.ep, 'stills', f's{i:02d}.png'), style + who + sh['image_prompt'], [resolve(o.ep, r) for r in sh.get('refs', [])]))
    with concurrent.futures.ThreadPoolExecutor(o.parallel) as ex:
        for res in ex.map(lambda j: gen(j[0], model, j[1], j[2], ep.get('aspect_ratio', '9:16')), jobs): print(res, flush=True)

if __name__ == '__main__': main()
