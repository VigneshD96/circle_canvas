// usage: node overlays.mjs EPISODE_DIR   -> EPISODE_DIR/overlays/{caption,bubbleN,title}.png
// Needs Playwright with a Chromium (pre-installed in Claude cloud sessions).
import { createRequire } from 'module'; import fs from 'fs'; import path from 'path'; import { fileURLToPath } from 'url';
const here = path.dirname(fileURLToPath(import.meta.url)); const req = createRequire(import.meta.url);
let pw; try { pw = req('playwright'); } catch { pw = req(path.join(process.cwd(), 'node_modules', 'playwright')); }
const ep = JSON.parse(fs.readFileSync(path.join(process.argv[2], 'episode.json'), 'utf8'));
const outDir = path.join(process.argv[2], 'overlays'); fs.mkdirSync(outDir, { recursive: true });
const b = await pw.chromium.launch(), p = await b.newPage();
await p.goto('file://' + path.join(here, 'overlays.html'));
const o = await p.evaluate(e => window.make(e), ep);
for (const [k, v] of Object.entries(o)) fs.writeFileSync(path.join(outDir, k + '.png'), Buffer.from(v.split(',')[1], 'base64'));
await b.close(); console.log('overlays:', Object.keys(o).join(', '));
