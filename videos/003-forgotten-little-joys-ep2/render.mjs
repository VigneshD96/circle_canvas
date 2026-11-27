// node render.mjs out.mp4  -> every frame piped to ffmpeg (H.264, CRF 16)
import { createRequire } from 'module';
const { chromium } = createRequire(import.meta.url)('playwright');
import { spawn } from 'child_process';
const here = new URL('.', import.meta.url).pathname;
const out = process.argv[2];
const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 600, height: 1000 } });
await p.goto('file://' + here + 'episode2.html?render');
const { FPS, DUR } = await p.evaluate(async () => { await window.readyP; return { FPS: window.SCENE.FPS, DUR: window.SCENE.DUR }; });
const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '16', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
for (let f = 0; f < FPS * DUR; f++) {
  const url = await p.evaluate(t => { window.SCENE.renderAt(t); return window.SCENE.canvas.toDataURL('image/png'); }, f / FPS);
  if (!ff.stdin.write(Buffer.from(url.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
}
ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close(); console.log('rendered', out);
