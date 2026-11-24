// node stills.mjs out_dir t1 t2 ...   -> full frames as PNG
import { createRequire } from 'module';
const { chromium } = createRequire(import.meta.url)('playwright');
import fs from 'fs';
const here = new URL('.', import.meta.url).pathname;
const [out, ...ts] = process.argv.slice(2);
fs.mkdirSync(out, { recursive: true });
const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 600, height: 1000 } });
const errs = []; p.on('pageerror', e => errs.push(String(e))); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
await p.goto('file://' + here + 'woman-walk.html?render');
await p.evaluate(() => window.readyP);
for (const t of ts) {
  const url = await p.evaluate(t => { window.SCENE.renderAt(+t); return window.SCENE.canvas.toDataURL('image/png'); }, t);
  fs.writeFileSync(`${out}/t${t}.png`, Buffer.from(url.split(',')[1], 'base64'));
}
if (errs.length) console.log('ERRORS', errs.join('\n'));
await b.close();
