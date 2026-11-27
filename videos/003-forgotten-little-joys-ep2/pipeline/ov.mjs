import { createRequire } from 'module'; import fs from 'fs';
const { chromium } = createRequire(import.meta.url)('playwright');
const b = await chromium.launch(), p = await b.newPage();
await p.goto('file://' + process.cwd() + '/ov.html');
const o = await p.evaluate(() => window.make());
for (const [k, v] of Object.entries(o)) fs.writeFileSync(k + '.png', Buffer.from(v.split(',')[1], 'base64'));
await b.close(); console.log(Object.keys(o));
