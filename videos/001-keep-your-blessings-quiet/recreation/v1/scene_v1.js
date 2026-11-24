// Woman walking: style recreation of video 001.
// Every frame is a pure function of t. No Math.random, no wall clock.
(function () {
'use strict';
const W = 1080, H = 1920, FPS = 30, DUR = 8;
const BW = 1080, BH = 608, BY = 656;            // 16:9 picture band inside the 9:16 frame
const TAU = Math.PI * 2;
const T_CYC = DUR / 7;                          // one full walk cycle (two steps), 7 cycles in 8 s
const STANCE = 0.6;
const STRIDE = 128;                             // ankle travel relative to hip during stance (px)
const SPEED = STRIDE / (STANCE * T_CYC);        // ground speed so planted feet never slide
const GROUND = 520;                             // footpath line where her soles land (band y)
const CHAR_X = 470;                             // her hip stays here; the world scrolls
const OFF = 64, CS = 0.88;                      // character drawn 64 px low on its own layer, then scaled 0.88 about her feet

// light comes from the low sun at the top right
const LD = norm(1, -0.62);
function norm(x, y) { const l = Math.hypot(x, y); return { x: x / l, y: y / l }; }

const C = {
  line: '#1a0805', lineLit: '#e8853f',
  skin: '#e58a4f', skinSh: '#a9532c', skinRim: '#ffb77a',
  blush: 'rgba(226,96,52,0.55)', freckle: 'rgba(130,54,26,0.75)',
  hair: '#3a1e18', hairSh: '#200f0b', hairHi: '#7b4532', hairRim: '#d27a3e',
  cami: '#1d1715', camiSh: '#0e0a09', camiRim: '#8a4a2a',
  jean: '#3a3646', jeanSh: '#1e1c26', jeanRim: '#b0703f', stitch: '#b68443',
  shoe: '#f1e6da', shoeSh: '#b9a593', shoeRim: '#fff6ea', sole: '#d9cbbb',
  eyeW: '#fbe3cf', iris: '#2a140d', irisC: '#0d0605',
};

function rng(seed) { let a = seed >>> 0; return () => { a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const lerp = (a, b, u) => a + (b - a) * u;
const ss = u => u * u * (3 - 2 * u);
const easeIO = u => 0.5 - 0.5 * Math.cos(Math.PI * clamp(u, 0, 1));

// ---------- canvases ----------
const cv = document.createElement('canvas'); cv.width = W; cv.height = H;
const ctx = cv.getContext('2d');
const band = document.createElement('canvas'); band.width = BW; band.height = BH;
const bx = band.getContext('2d');
const mk = (w = BW, h = BH) => { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; };
const LINE = mk(), FILL = mk(), MASK = mk(), CH = mk();
const chx = CH.getContext('2d');
let TG = null;
const lx = LINE.getContext('2d'), fx = FILL.getContext('2d'), mx = MASK.getContext('2d');

// ---------- path helpers ----------
function polyArea(pts) { let s = 0; for (let i = 0; i < pts.length; i++) { const a = pts[i], b = pts[(i + 1) % pts.length]; s += a[0] * b[1] - b[0] * a[1]; } return s; }
function addPoly(P, pts) { if (polyArea(pts) < 0) pts = pts.slice().reverse(); P.moveTo(pts[0][0], pts[0][1]); for (let i = 1; i < pts.length; i++) P.lineTo(pts[i][0], pts[i][1]); P.closePath(); }
function addCircle(P, x, y, r) { P.moveTo(x + r, y); P.arc(x, y, r, 0, TAU, false); P.closePath(); }
// tapered limb through points [[x,y,width],...] as one non-zero union
function limbPath(pts) {
  const P = new Path2D();
  for (let i = 0; i < pts.length - 1; i++) {
    const [ax, ay, aw] = pts[i], [bx_, by, bw] = pts[i + 1];
    const dx = bx_ - ax, dy = by - ay, l = Math.hypot(dx, dy) || 1, nx = -dy / l, ny = dx / l;
    addPoly(P, [[ax + nx * aw / 2, ay + ny * aw / 2], [bx_ + nx * bw / 2, by + ny * bw / 2], [bx_ - nx * bw / 2, by - ny * bw / 2], [ax - nx * aw / 2, ay - ny * aw / 2]]);
  }
  for (const [x, y, w] of pts) addCircle(P, x, y, w / 2);
  return P;
}
// local path (built with a callback) transformed by a matrix
function xf(build, m) { const L = new Path2D(); build(L); const P = new Path2D(); P.addPath(L, m); return P; }
function mat(x, y, rot = 0, s = 1) { return new DOMMatrix().translateSelf(x, y).rotateSelf(rot * 180 / Math.PI).scaleSelf(s, s); }

// ---------- the cel-shaded, rim-lit, coloured-line part renderer ----------
// shade: how far the shadow crescent reaches in from the dark side; rim: lit-edge band width
function part(P, col, o = {}) {
  const lw = o.lw ?? 3.0, sh = o.shade ?? 8, rim = o.rim ?? 2.6, soft = o.soft ?? 2.2;
  // 1. line layer: dilated shape in dark brown, turned orange on the lit side
  lx.setTransform(1, 0, 0, 1, 0, 0); lx.globalCompositeOperation = 'source-over'; lx.clearRect(0, 0, BW, BH);
  lx.fillStyle = C.line; lx.strokeStyle = C.line; lx.lineJoin = 'round'; lx.lineWidth = lw * 2;
  lx.fill(P); lx.stroke(P);
  if (!o.noLitLine) {
    lx.globalCompositeOperation = 'source-atop';
    lx.translate(LD.x * lw * 1.7, LD.y * lw * 1.7); lx.fillStyle = o.lineLit || C.lineLit; lx.fill(P);
    lx.setTransform(1, 0, 0, 1, 0, 0);
  }
  // 2. fill layer: base, soft shadow crescent away from light, rim band on lit edge
  fx.setTransform(1, 0, 0, 1, 0, 0); fx.globalCompositeOperation = 'source-over'; fx.clearRect(0, 0, BW, BH); fx.filter = 'none';
  fx.fillStyle = col[0]; fx.fill(P);
  mask(P, LD.x * sh, LD.y * sh, col[1]);
  fx.globalCompositeOperation = 'source-atop'; fx.filter = `blur(${soft}px)`; fx.drawImage(MASK, 0, 0); fx.filter = 'none';
  if (rim > 0) { mask(P, -LD.x * rim, -LD.y * rim, col[2]); fx.filter = 'blur(0.8px)'; fx.drawImage(MASK, 0, 0); fx.filter = 'none'; }
  if (o.detail) { fx.globalCompositeOperation = 'source-atop'; o.detail(fx); fx.setTransform(1, 0, 0, 1, 0, 0); }
  fx.globalCompositeOperation = 'source-over';
  const g = o.ctx || TG;
  g.drawImage(LINE, 0, 0); g.drawImage(FILL, 0, 0);
}
function mask(P, dx, dy, color) {
  mx.setTransform(1, 0, 0, 1, 0, 0); mx.globalCompositeOperation = 'source-over'; mx.clearRect(0, 0, BW, BH);
  mx.fillStyle = '#000'; mx.fill(P);
  mx.globalCompositeOperation = 'destination-out'; mx.translate(dx, dy); mx.fill(P); mx.setTransform(1, 0, 0, 1, 0, 0);
  mx.globalCompositeOperation = 'source-in'; mx.fillStyle = color; mx.fillRect(0, 0, BW, BH);
  mx.globalCompositeOperation = 'source-over';
}
const dimCol = (cols, k) => cols.map(c => shadeHex(c, k));
function shadeHex(h, k) { const n = parseInt(h.slice(1), 16); const r = (n >> 16) & 255, g = (n >> 8) & 255, b = n & 255; const f = v => Math.round(v * k).toString(16).padStart(2, '0'); return '#' + f(r) + f(g) + f(b); }

// ---------- seeded tables ----------
const R1 = rng(101), R2 = rng(202), R3 = rng(303);
const BLINKS = []; { let t = 0.9; while (t < DUR) { BLINKS.push(t); t += 1.8 + R1() * 1.6; } }
const FRECKLES = Array.from({ length: 22 }, () => [R2(), R2(), 0.55 + R2() * 0.7]);

// ---------- background (pre-rendered painted strips, no outlines, soft focus) ----------
const BG = {};
function buildBackground() {
  const rs = rng(7);
  // sky with a low sun at the top right
  const sky = mk(); const s = sky.getContext('2d');
  let g = s.createLinearGradient(0, 0, 0, 470);
  g.addColorStop(0, '#8fb6e2'); g.addColorStop(0.45, '#bcd2e8'); g.addColorStop(0.78, '#f3d6b2'); g.addColorStop(1, '#f6c48f');
  s.fillStyle = g; s.fillRect(0, 0, BW, BH);
  const sunX = 1010, sunY = 40;
  let rg = s.createRadialGradient(sunX, sunY, 0, sunX, sunY, 700);
  rg.addColorStop(0, 'rgba(255,240,200,0.95)'); rg.addColorStop(0.08, 'rgba(255,226,170,0.75)'); rg.addColorStop(0.35, 'rgba(255,196,130,0.28)'); rg.addColorStop(1, 'rgba(255,190,120,0)');
  s.fillStyle = rg; s.fillRect(0, 0, BW, BH);
  // soft painted clouds
  s.filter = 'blur(10px)';
  for (let i = 0; i < 7; i++) { const x = rs() * BW, y = 40 + rs() * 140, w = 160 + rs() * 220; s.fillStyle = `rgba(255,238,222,${0.25 + rs() * 0.25})`; s.beginPath(); s.ellipse(x, y, w, 18 + rs() * 14, 0, 0, TAU); s.fill(); }
  s.filter = 'none';
  BG.sky = sky;

  // far skyline, hazy (parallax 0.08)
  const farW = BW + 400, far = mk(farW, BH), f = far.getContext('2d');
  let x = -20;
  while (x < farW) {
    const w = 40 + rs() * 90, h = 70 + rs() * 150;
    f.fillStyle = `rgb(${186 + rs() * 18 | 0},${180 + rs() * 14 | 0},${186 + rs() * 14 | 0})`;
    f.fillRect(x, 400 - h, w, h + 40);
    if (rs() < 0.3) f.fillRect(x + w * 0.4, 400 - h - 30, 4, 30);
    x += w + rs() * 10;
  }
  const hz = f.createLinearGradient(0, 230, 0, 420); hz.addColorStop(0, 'rgba(246,210,170,0.0)'); hz.addColorStop(1, 'rgba(246,206,160,0.55)');
  f.fillStyle = hz; f.fillRect(0, 0, farW, BH);
  BG.far = blurred(far, 3.5);

  // mid: low buildings + rounded trees (parallax 0.42)
  const midW = BW + Math.ceil(SPEED * DUR * 0.42) + 300, mid = mk(midW, BH), m = mid.getContext('2d');
  x = -40;
  while (x < midW) {   // low buildings, warm walls lit from the right
    const w = 120 + rs() * 160, h = 60 + rs() * 70, base = 440;
    const wall = ['#d9b08f', '#c99c84', '#e2c3a4', '#b98f7a'][rs() * 4 | 0];
    m.fillStyle = wall; m.fillRect(x, base - h, w, h + 20);
    m.fillStyle = 'rgba(120,70,50,0.25)'; m.fillRect(x, base - h, w * 0.18, h + 20);
    m.fillStyle = 'rgba(255,230,190,0.35)'; m.fillRect(x + w - 6, base - h, 6, h + 20);
    m.fillStyle = 'rgba(90,70,80,0.55)'; for (let k = 0; k < Math.floor(w / 46); k++) m.fillRect(x + 14 + k * 46, base - h + 18, 22, 20);
    m.fillStyle = '#8c6a5a'; m.fillRect(x - 4, base - h - 6, w + 8, 8);
    x += w + 40 + rs() * 120;
  }
  x = 30;
  while (x < midW) { tree(m, x, 452, 58 + rs() * 36, rs); x += 120 + rs() * 120; }
  // hedge line along the verge
  for (let hx = -20; hx < midW; hx += 26) { m.fillStyle = rs() < 0.5 ? '#6f7a3c' : '#7c8642'; m.beginPath(); m.ellipse(hx, 462, 30, 18 + rs() * 6, 0, 0, TAU); m.fill(); }
  m.fillStyle = 'rgba(255,205,130,0.25)'; for (let hx = -20; hx < midW; hx += 26) { m.beginPath(); m.ellipse(hx + 10, 452, 12, 6, 0, 0, TAU); m.fill(); }
  BG.mid = blurred(mid, 2.4); BG.midW = midW;

  // lamp posts on the verge (parallax 0.8), drawn per frame from a list
  BG.lamps = []; for (let lxp = 200; lxp < BW + SPEED * DUR + 600; lxp += 520 + rs() * 120) BG.lamps.push(lxp);
  // dappled shadow blobs on the footpath (parallax 1)
  BG.dapples = []; for (let dxp = 0; dxp < BW + SPEED * DUR + 400; dxp += 60 + rs() * 140) BG.dapples.push([dxp, 494 + rs() * 46, 30 + rs() * 50, 4 + rs() * 7]);
  // sun glow sprite for the flare
  BG.glow = glowSprite(256, [255, 214, 150], 2.0);
}
function tree(m, x, base, r, rs) {
  m.fillStyle = '#6b4a36'; m.fillRect(x - 5, base - r * 1.1, 10, r * 1.1);
  const greens = ['#5f6b34', '#6e7a3a', '#7d8a44'];
  for (let k = 0; k < 7; k++) {
    const ox = (rs() - 0.5) * r * 1.2, oy = -r * 1.25 + (rs() - 0.5) * r * 0.8, rr = r * (0.45 + rs() * 0.3);
    const cx = x + ox, cy = base + oy, gr = m.createLinearGradient(cx - rr, cy + rr * 0.6, cx + rr, cy - rr * 0.6);
    gr.addColorStop(0, '#4b5a2c'); gr.addColorStop(0.55, greens[k % 3]); gr.addColorStop(1, '#c3b45e');
    m.fillStyle = gr; m.beginPath(); m.ellipse(cx, cy, rr, rr * 0.9, 0, 0, TAU); m.fill();
  }
}
function blurred(src, px) { const c = mk(src.width, src.height), g = c.getContext('2d'); g.filter = `blur(${px}px)`; g.drawImage(src, 0, 0); return c; }
function glowSprite(size, rgb, power) {
  const c = mk(size, size), g = c.getContext('2d'), im = g.createImageData(size, size), m = (size - 1) / 2;
  for (let j = 0; j < size; j++) for (let i = 0; i < size; i++) { const d = Math.hypot(i - m, j - m) / (size / 2), o = (j * size + i) * 4; im.data[o] = rgb[0]; im.data[o + 1] = rgb[1]; im.data[o + 2] = rgb[2]; im.data[o + 3] = d >= 1 ? 0 : 255 * Math.pow(1 - d, power); }
  g.putImageData(im, 0, 0); return c;
}

function drawBackground(t) {
  const cam = SPEED * CS * t;          // her feet are drawn at scale CS, so the ground moves at the scaled speed
  bx.drawImage(BG.sky, 0, 0);
  bx.drawImage(BG.far, -(cam * 0.08) % 400, 0);
  bx.drawImage(BG.mid, -cam * 0.42, 0);
  // grass verge
  let g = bx.createLinearGradient(0, 455, 0, 492); g.addColorStop(0, '#8d9046'); g.addColorStop(1, '#a29a52');
  bx.fillStyle = g; bx.fillRect(0, 455, BW, 40);
  // lamp posts (soft, slightly out of focus)
  bx.save(); bx.filter = 'blur(1.2px)';
  for (const p of BG.lamps) {
    const x = p - cam * 0.8; if (x < -60 || x > BW + 60) continue;
    bx.fillStyle = '#4a4148'; bx.fillRect(x - 4, 170, 8, 318);
    bx.fillStyle = '#3c343a'; bx.fillRect(x - 7, 470, 14, 20);
    bx.fillRect(x - 2, 168, 40, 6); bx.fillStyle = '#5a5058'; bx.beginPath(); bx.ellipse(x + 40, 176, 16, 7, 0, 0, TAU); bx.fill();
    bx.fillStyle = 'rgba(255,215,150,0.75)'; bx.fillRect(x + 3, 170, 2, 318);   // sun catching the right edge
  }
  bx.restore();
  // footpath: warm concrete slabs
  const top = 490, kerb = 548;
  g = bx.createLinearGradient(0, top, 0, kerb); g.addColorStop(0, '#d8b99a'); g.addColorStop(1, '#e8cba8');
  bx.fillStyle = g; bx.fillRect(0, top, BW, kerb - top);
  // long lamp-post shadows cast to the left across the path
  bx.save(); bx.filter = 'blur(2px)'; bx.fillStyle = 'rgba(120,78,60,0.22)';
  for (const p of BG.lamps) { const x = p - cam * 0.8; bx.beginPath(); bx.moveTo(x - 4, top); bx.lineTo(x + 4, top); bx.lineTo(x - 150, kerb); bx.lineTo(x - 166, kerb); bx.fill(); }
  bx.restore();
  // dappled tree shadows
  bx.save(); bx.filter = 'blur(5px)'; bx.fillStyle = 'rgba(120,74,52,0.18)';
  for (const [dx_, dy, w, h] of BG.dapples) { const x = dx_ - cam; if (x < -100 || x > BW + 100) continue; bx.beginPath(); bx.ellipse(x, dy, w, h, 0, 0, TAU); bx.fill(); }
  bx.restore();
  // slab joints, in step with her feet
  bx.strokeStyle = 'rgba(150,104,78,0.55)'; bx.lineWidth = 2;
  const SLAB = 150;
  for (let k = Math.floor(cam / SLAB) - 1; k < (cam + BW) / SLAB + 2; k++) {
    const x = k * SLAB - cam; bx.beginPath(); bx.moveTo(x + 18, top + 1); bx.lineTo(x - 8, kerb - 1); bx.stroke();
  }
  bx.fillStyle = 'rgba(255,236,206,0.6)'; bx.fillRect(0, top, BW, 2);
  // kerb
  bx.fillStyle = '#efd7bb'; bx.fillRect(0, kerb, BW, 6);
  g = bx.createLinearGradient(0, kerb + 6, 0, kerb + 18); g.addColorStop(0, '#a98a74'); g.addColorStop(1, '#7c6457');
  bx.fillStyle = g; bx.fillRect(0, kerb + 6, BW, 12);
  // road in the foreground, slightly soft
  const road = kerb + 18;
  g = bx.createLinearGradient(0, road, 0, BH); g.addColorStop(0, '#57525c'); g.addColorStop(1, '#3d3a44');
  bx.fillStyle = g; bx.fillRect(0, road, BW, BH - road);
  bx.save(); bx.filter = 'blur(1.6px)';
  bx.fillStyle = 'rgba(255,214,160,0.18)'; bx.fillRect(0, road, BW, 3);
  bx.fillStyle = '#ece0cc';
  const DASH = 260; for (let k = Math.floor(cam * 1.15 / DASH) - 1; k < (cam * 1.15 + BW) / DASH + 2; k++) { const x = k * DASH - cam * 1.15; bx.fillRect(x, BH - 14, 130, 8); }
  bx.restore();
}

// ---------- the walk rig ----------
function footAt(p) {                 // ankle offset from hip-x, lift, and foot pitch for one leg at phase p
  p = ((p % 1) + 1) % 1;
  if (p < STANCE) {
    const u = p / STANCE;
    const x = STRIDE / 2 - STRIDE * u;
    let pitch = 0, lift = 0;
    if (u < 0.14) { pitch = lerp(-0.30, 0, ss(u / 0.14)); lift = Math.sin(-pitch) * 10; }
    else if (u > 0.7) { const k = ss((u - 0.7) / 0.3); pitch = 0.62 * k; lift = Math.sin(pitch) * 30; }
    return { x, lift, pitch };
  }
  const u = (p - STANCE) / (1 - STANCE);
  const x = -STRIDE / 2 + STRIDE * easeIO(u);
  const lift = 12 + 22 * Math.sin(Math.PI * Math.pow(u, 0.75));
  const pitch = u < 0.5 ? lerp(0.62, 0.15, ss(u / 0.5)) : lerp(0.15, -0.30, ss((u - 0.5) / 0.5));
  return { x, lift: u < 0.12 ? lerp(30, 12 + 22 * Math.sin(Math.PI * Math.pow(0.12, 0.75)), u / 0.12) : lift, pitch };
}
function ik(hx, hy, ax, ay, l1, l2, bend) {     // two-bone IK, bend +1 puts the knee/elbow toward +x
  let dx = ax - hx, dy = ay - hy, d = Math.hypot(dx, dy);
  const dm = Math.min(d, l1 + l2 - 0.5); if (d > dm) { ax = hx + dx / d * dm; ay = hy + dy / d * dm; d = dm; dx = ax - hx; dy = ay - hy; }
  const a = Math.atan2(dy, dx), c = clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), -1, 1), b = Math.acos(c);
  const ang = a - bend * b;
  return { kx: hx + Math.cos(ang) * l1, ky: hy + Math.sin(ang) * l1, ax, ay };
}

function pose(t) {
  const p = (t / T_CYC) % 1;              // near (left) leg phase; far leg is half a cycle later
  const bob = 3.5 * Math.cos(4 * Math.PI * p) - 1;    // low at each heel strike
  const hipX = CHAR_X, hipY = 290 + OFF + bob;
  const sway = 0.012 * Math.sin(TAU * p);
  return { p, hipX, hipY, sway, lean: 0.06 };
}

// ---------- body parts ----------
function shoePath(ax, ay, pitch) {
  return xf(P => {
    P.moveTo(-16, -6); P.bezierCurveTo(-18, 8, -14, 14, -6, 14);
    P.lineTo(34, 14); P.bezierCurveTo(44, 14, 46, 6, 40, 2);
    P.bezierCurveTo(30, -4, 18, -8, 8, -12); P.bezierCurveTo(0, -14, -12, -12, -16, -6); P.closePath();
  }, mat(ax, ay, pitch));
}
function drawLeg(pz, phase, far) {
  const f = footAt(phase);
  const hx = pz.hipX + (far ? -6 : 4), hy = pz.hipY + (far ? -2 : 2);
  const ax = pz.hipX + f.x + 4, ay = GROUND + OFF - 15 - f.lift;
  const L = ik(hx, hy, ax, ay, 108, 106, 1);
  const k = far ? 0.72 : 1;
  const jean = far ? dimCol([C.jean, C.jeanSh, C.jeanRim], k) : [C.jean, C.jeanSh, C.jeanRim];
  const shoe = far ? dimCol([C.shoe, C.shoeSh, C.shoeRim], 0.8) : [C.shoe, C.shoeSh, C.shoeRim];
  // shoe first so the hem overlaps it
  part(shoePath(L.ax, L.ay + 4, f.pitch), shoe, { shade: 5, rim: 1.8, lw: 2.6, detail: g => { g.setTransform(new DOMMatrix().translateSelf(L.ax, L.ay + 4).rotateSelf(f.pitch * 57.3)); g.fillStyle = far ? '#a89a8a' : C.sole; g.fillRect(-20, 8, 70, 8); g.fillStyle = far ? '#6d6058' : '#cdb9a5'; g.fillRect(4, -6, 3, 9); } });
  const P = limbPath([[hx, hy, 48], [L.kx, L.ky, 32], [L.ax, L.ay - 2, 25]]);
  part(P, jean, { shade: 9, rim: 2.8, lw: 3, detail: g => {
    g.strokeStyle = far ? 'rgba(150,110,60,0.5)' : 'rgba(182,132,67,0.75)'; g.lineWidth = 1.3; g.setLineDash([4, 3]);
    // outer seam down the leg
    g.beginPath(); g.moveTo(hx + 4, hy + 6); g.lineTo(L.kx + 2, L.ky); g.lineTo(L.ax + 1, L.ay - 4); g.stroke(); g.setLineDash([]);
    // hem fold
    g.strokeStyle = far ? 'rgba(20,18,26,0.6)' : 'rgba(20,18,26,0.7)'; g.lineWidth = 2; g.beginPath(); g.moveTo(L.ax - 13, L.ay - 8); g.lineTo(L.ax + 13, L.ay - 9); g.stroke();
  } });
}
function drawArm(pz, near) {
  const p = pz.p;
  const swing = (near ? -1 : 1) * 0.33 * Math.cos(TAU * p - 0.25);      // forward is positive, opposite the same-side leg
  const sx = pz.hipX + 6 + (near ? 2 : -10), sy = pz.hipY - 150 + (near ? 0 : -2);
  const upper = 72, lower = 68;
  const a1 = Math.PI / 2 - swing - pz.lean;                           // pointing down, rotated by swing
  const ex = sx + Math.cos(a1) * upper, ey = sy + Math.sin(a1) * upper;
  const bend = 0.22 + 0.32 * Math.max(0, swing / 0.33);
  const a2 = a1 - bend;
  const wx = ex + Math.cos(a2) * lower, wy = ey + Math.sin(a2) * lower;
  const cols = near ? [C.skin, C.skinSh, C.skinRim] : dimCol([C.skin, C.skinSh, C.skinRim], 0.8);
  const arm = limbPath([[sx, sy, 25], [ex, ey, 17], [wx, wy, 13]]);
  part(arm, cols, { shade: 6, rim: 2.4, lw: 2.8 });
  // relaxed hand: palm toward the leg, fingers loosely curled
  const hp = xf(Q => {
    Q.moveTo(-6, -2); Q.bezierCurveTo(-9, 8, -7, 20, 0, 23); Q.bezierCurveTo(7, 25, 11, 18, 10, 10);
    Q.bezierCurveTo(13, 9, 13, 3, 9, 1); Q.bezierCurveTo(6, -4, -2, -6, -6, -2); Q.closePath();
  }, mat(wx, wy, a2 - Math.PI / 2));
  part(hp, cols, { shade: 4, rim: 1.8, lw: 2.4, detail: g => {
    g.setTransform(mat(wx, wy, a2 - Math.PI / 2)); g.strokeStyle = 'rgba(120,48,22,0.8)'; g.lineWidth = 1.2;
    g.beginPath(); g.moveTo(-3, 13); g.quadraticCurveTo(2, 15, 6, 12); g.stroke(); g.beginPath(); g.moveTo(-2, 18); g.quadraticCurveTo(2, 19.5, 5, 17); g.stroke();
  } });
}
function torsoMatrix(pz) { return mat(pz.hipX, pz.hipY, pz.lean + pz.sway); }
function drawTorso(pz) {
  const m = torsoMatrix(pz);
  // skin: midriff, chest, shoulders
  const skin = xf(P => {
    P.moveTo(-22, -40); P.bezierCurveTo(-18, -70, -30, -110, -22, -146);
    P.bezierCurveTo(-14, -160, 10, -162, 18, -150);
    P.bezierCurveTo(26, -138, 38, -124, 36, -104);
    P.bezierCurveTo(34, -90, 18, -80, 19, -40); P.closePath();
  }, m);
  part(skin, [C.skin, C.skinSh, C.skinRim], { shade: 9, rim: 2.6, lw: 3 });
  // cami: from under the bust line up to the neckline, thin straps over the shoulder
  const cami = xf(P => {
    P.moveTo(-21, -64); P.bezierCurveTo(-24, -92, -29, -112, -23, -134);
    P.bezierCurveTo(-12, -130, 4, -126, 16, -132);
    P.bezierCurveTo(30, -126, 40, -114, 38, -102);
    P.bezierCurveTo(37, -90, 26, -84, 21, -80);
    P.bezierCurveTo(20, -74, 20, -68, 20, -62);
    P.bezierCurveTo(8, -60, -10, -60, -21, -64); P.closePath();
  }, m);
  part(cami, [C.cami, C.camiSh, C.camiRim], { shade: 10, rim: 2.6, lw: 3, lineLit: '#9a5532' });
  // strap
  const strap = xf(P => { P.moveTo(-14, -131); P.bezierCurveTo(-12, -144, -8, -153, -2, -159); P.lineTo(2, -158); P.bezierCurveTo(-4, -150, -8, -142, -9, -130); P.closePath(); }, m);
  const strap2 = xf(P => { P.moveTo(12, -131); P.bezierCurveTo(12, -142, 10, -152, 8, -158); P.lineTo(11, -158); P.bezierCurveTo(14, -150, 16, -142, 16, -131); P.closePath(); }, m);
  part(strap2, [C.cami, C.camiSh, C.camiRim], { shade: 2, rim: 1, lw: 1.6, lineLit: '#9a5532' });
  part(strap, [C.cami, C.camiSh, C.camiRim], { shade: 2, rim: 1, lw: 1.6, lineLit: '#9a5532' });
  // high-waisted jeans: waistband to upper thigh
  const jeans = xf(P => {
    P.moveTo(-22, -44); P.bezierCurveTo(-28, -30, -33, -12, -29, 6);
    P.bezierCurveTo(-28, 20, -14, 26, 0, 26); P.bezierCurveTo(14, 26, 26, 18, 26, 4);
    P.bezierCurveTo(27, -14, 22, -30, 21, -46);
    P.bezierCurveTo(8, -49, -10, -48, -22, -44); P.closePath();
  }, m);
  part(jeans, [C.jean, C.jeanSh, C.jeanRim], { shade: 10, rim: 2.8, lw: 3, detail: g => {
    g.setTransform(m); g.strokeStyle = 'rgba(182,132,67,0.8)'; g.lineWidth = 1.3; g.setLineDash([4, 3]);
    g.beginPath(); g.moveTo(-24, -34); g.bezierCurveTo(-8, -38, 10, -38, 24, -36); g.stroke();             // waistband stitch
    g.beginPath(); g.moveTo(10, -32); g.bezierCurveTo(14, -18, 20, -10, 26, -8); g.stroke();                 // front pocket
    g.setLineDash([]); g.fillStyle = '#c99a52'; g.beginPath(); g.arc(20, -40, 2.6, 0, TAU); g.fill();      // button
    g.strokeStyle = 'rgba(15,13,20,0.6)'; g.lineWidth = 2; g.beginPath(); g.moveTo(-14, -45); g.lineTo(-13, -33); g.stroke(); // belt loop
  } });
}

// ---------- head ----------
function headMatrix(pz, t) {
  const m = torsoMatrix(pz);
  const neckTop = m.transformPoint(new DOMPoint(6, -170));
  const nod = 0.025 * Math.sin(4 * Math.PI * pz.p - 0.6);
  return { m: mat(neckTop.x + 4, neckTop.y - 42, -0.05 + nod, 1.28), neckTop };
}
function drawNeck(pz) {
  const m = torsoMatrix(pz);
  const a = m.transformPoint(new DOMPoint(4, -146)), b = m.transformPoint(new DOMPoint(8, -176));
  part(limbPath([[a.x, a.y, 25], [b.x, b.y, 22]]), [C.skin, C.skinSh, C.skinRim], { shade: 7, rim: 2.2, lw: 2.8 });
}
function hairSway(pz, t, lag) { return 0.07 * Math.sin(4 * Math.PI * pz.p - lag) + 0.03 * Math.sin(TAU * t / 2.3 + lag); }

function drawBackHair(H, pz, t) {
  const m = H.m;
  // nape strands that hang behind the neck
  const sw = hairSway(pz, t, 1.2);
  strands(m, [[-30, 18, -38 + sw * 50, 44, 2.2], [-24, 22, -27 + sw * 60, 46, 1.7]], C.hair);
  // bun: clumpy blob high on the back of the head
  const rb = rng(55);
  const k = [1, 2, 3, 5].map(n => ({ n, a: rb() * 0.16 / n, p: rb() * TAU }));
  const bun = xf(P => {
    const cx = -22, cy = -52, r = 23;
    for (let i = 0; i <= 48; i++) { const a = TAU * i / 48; let rr = r; for (const h of k) rr += r * h.a * Math.sin(h.n * a + h.p); const x = cx + rr * Math.cos(a) * 1.08, y = cy + rr * Math.sin(a); i ? P.lineTo(x, y) : P.moveTo(x, y); }
    P.closePath();
  }, mat(0, 0).multiply(m).rotateSelf(sw * 20));
  part(bun, [C.hair, C.hairSh, C.hairRim], { shade: 8, rim: 2.4, lw: 3, lineLit: '#c86e36', detail: g => {
    g.setTransform(m); g.strokeStyle = C.hairHi; g.lineWidth = 3; g.lineCap = 'round';
    g.beginPath(); g.arc(-22, -52, 15, -1.4, -0.2); g.stroke();
    g.strokeStyle = 'rgba(16,6,4,0.7)'; g.lineWidth = 1.6;
    g.beginPath(); g.moveTo(-36, -56); g.quadraticCurveTo(-24, -42, -8, -50); g.stroke();
    g.beginPath(); g.moveTo(-30, -70); g.quadraticCurveTo(-18, -62, -10, -66); g.stroke();
  } });
  // flyaway loops on the bun
  strands(m, [[-36, -64, -48 + sw * 20, -58, 1.3], [-14, -73, -4 + sw * 20, -78, 1.2], [-42, -46, -50 + sw * 20, -36, 1.2]], C.hair);
}
function strands(m, list, color) {
  const g = TG; g.save(); g.setTransform(m); g.lineCap = 'round';
  for (const [x0, y0, x1, y1, w] of list) {
    const cx = (x0 + x1) / 2 + (y1 - y0) * 0.25, cy = (y0 + y1) / 2 - (x1 - x0) * 0.25;
    g.strokeStyle = C.line; g.lineWidth = w + 1.6; g.beginPath(); g.moveTo(x0, y0); g.quadraticCurveTo(cx, cy, x1, y1); g.stroke();
    g.strokeStyle = color; g.lineWidth = w * 0.7; g.beginPath(); g.moveTo(x0, y0); g.quadraticCurveTo(cx, cy, x1, y1); g.stroke();
  }
  g.restore();
}
function drawHead(pz, t) {
  const H = headMatrix(pz, t), m = H.m;
  drawBackHair(H, pz, t);
  // face: 3/4 view turned toward camera, facing right
  const face = xf(P => {
    P.moveTo(-36, -4);
    P.bezierCurveTo(-38, -44, 18, -52, 31, -24);
    P.bezierCurveTo(36, -14, 38, -6, 38, 0);
    P.bezierCurveTo(40, 4, 45, 9, 44, 13);       // nose tip
    P.bezierCurveTo(43, 16, 39, 16, 38, 17);
    P.bezierCurveTo(37, 30, 28, 42, 14, 44);     // cheek to chin
    P.bezierCurveTo(4, 45, -8, 40, -14, 33);     // jaw
    P.bezierCurveTo(-24, 26, -34, 14, -36, -4); P.closePath();
  }, m);
  part(face, [C.skin, C.skinSh, C.skinRim], { shade: 10, rim: 2.6, lw: 3, soft: 3, detail: g => {
    g.setTransform(m);
    // nose tone (style: nose made of tone, not line)
    g.fillStyle = 'rgba(176,80,40,0.45)'; g.beginPath(); g.moveTo(34, 2); g.quadraticCurveTo(43, 10, 40, 15); g.quadraticCurveTo(35, 16, 31, 13); g.closePath(); g.fill();
    // blush
    for (const [x, y, rx, ry] of [[2, 20, 11, 7], [33, 21, 5, 5]]) { const gr = g.createRadialGradient(x, y, 0, x, y, rx); gr.addColorStop(0, C.blush); gr.addColorStop(1, 'rgba(226,96,52,0)'); g.fillStyle = gr; g.beginPath(); g.ellipse(x, y, rx, ry, 0, 0, TAU); g.fill(); }
    // freckles across nose bridge and cheeks
    g.fillStyle = C.freckle;
    for (const [u, v, s] of FRECKLES) { const x = -8 + u * 44, y = 12 + v * 10 - (x > 22 ? 3 : 0); g.beginPath(); g.arc(x, y, 0.9 * s, 0, TAU); g.fill(); }
  } });
  // ear (near side), mostly clear of hair because it is pulled up
  const ear = xf(P => { P.moveTo(-18, 2); P.bezierCurveTo(-26, -6, -34, 0, -32, 10); P.bezierCurveTo(-31, 20, -24, 24, -18, 18); P.closePath(); }, m);
  drawFace(m, t, pz);
  drawFrontHair(m, pz, t);
  part(ear, [C.skin, C.skinSh, C.skinRim], { shade: 4, rim: 2, lw: 2.4, detail: g => { g.setTransform(m); g.strokeStyle = 'rgba(150,62,28,0.8)'; g.lineWidth = 1.3; g.beginPath(); g.moveTo(-21, 6); g.quadraticCurveTo(-28, 4, -27, 12); g.quadraticCurveTo(-26, 16, -22, 15); g.stroke(); } });
}
function eyeOpen(t) {
  for (const b of BLINKS) { const d = t - b; if (d >= 0 && d < 0.16) return d < 0.06 ? 1 - d / 0.06 : (d - 0.06) / 0.1; }
  return 1;
}
function drawFace(m, t, pz) {
  const g = TG; g.save(); g.setTransform(m);
  const open = eyeOpen(t);
  const look = 2.2;
  eye(g, 4, 2, 11, 10, open, look, false);     // near eye, larger
  eye(g, 28, 1, 6.5, 9.5, open, look * 0.6, true);   // far eye, foreshortened
  // brows: thick dark wedges, gentle arch
  g.fillStyle = C.line;
  brow(g, [[-9, -12], [4, -18.5], [16, -15.5]], 4.2);
  brow(g, [[23, -16.5], [29, -18], [34, -14.5]], 3.4);
  // mouth: small closed smile, lower lip tint
  g.strokeStyle = '#3a1009'; g.lineWidth = 2.2; g.lineCap = 'round';
  g.beginPath(); g.moveTo(17, 29); g.quadraticCurveTo(25, 33.5, 32, 28.5); g.stroke();
  g.strokeStyle = 'rgba(120,30,18,0.6)'; g.lineWidth = 1.4; g.beginPath(); g.moveTo(16, 27.5); g.lineTo(17.5, 30); g.stroke();
  g.fillStyle = 'rgba(196,74,50,0.5)'; g.beginPath(); g.ellipse(25, 34.5, 4.2, 1.6, 0, 0, TAU); g.fill();
  g.restore();
}
function brow(g, pts, w) {
  g.beginPath(); g.moveTo(pts[0][0], pts[0][1] + w * 0.25);
  g.quadraticCurveTo(pts[1][0], pts[1][1], pts[2][0], pts[2][1]);
  g.quadraticCurveTo(pts[1][0], pts[1][1] + w * 1.15, pts[0][0], pts[0][1] + w * 0.9); g.closePath(); g.fill();
}
function eye(g, cx, cy, rx, ry, open, look, far) {
  if (open < 0.12) {   // closed: a soft downward lash arc
    g.strokeStyle = C.line; g.lineWidth = 2.6; g.beginPath(); g.moveTo(cx - rx, cy + 1); g.quadraticCurveTo(cx, cy + ry * 0.5, cx + rx, cy + 1); g.stroke(); return;
  }
  const oy = ry * open;
  g.save();
  g.beginPath(); g.ellipse(cx, cy + ry - oy, rx, oy, 0, 0, TAU); g.fillStyle = C.eyeW; g.fill();
  g.clip();
  const ix = cx + look + (far ? 1 : 0.5), iy = cy + 1;
  const irx = far ? rx * 0.62 : rx * 0.6, iry = ry * 0.78;
  const gr = g.createRadialGradient(ix, iy + 1, 0, ix, iy, iry); gr.addColorStop(0, '#4a2416'); gr.addColorStop(1, C.iris);
  g.fillStyle = gr; g.beginPath(); g.ellipse(ix, iy, irx, iry, 0, 0, TAU); g.fill();
  g.fillStyle = C.irisC; g.beginPath(); g.ellipse(ix + 0.3, iy + 0.5, irx * 0.55, iry * 0.55, 0, 0, TAU); g.fill();
  g.fillStyle = '#fff8ee'; g.beginPath(); g.arc(ix - irx * 0.35, iy - iry * 0.4, far ? 1.6 : 2.4, 0, TAU); g.fill();
  g.beginPath(); g.arc(ix + irx * 0.35, iy + iry * 0.35, far ? 0.8 : 1.2, 0, TAU); g.fill();
  // upper-lid shadow on the eyeball
  g.fillStyle = 'rgba(180,90,60,0.25)'; g.fillRect(cx - rx, cy + ry - oy - oy, rx * 2, oy * 0.35);
  g.restore();
  // thick upper lash line with outer flicks (outer corner: left for the near eye, right for the far eye)
  const top = cy + ry - 2 * oy;
  g.fillStyle = C.line; g.beginPath();
  g.moveTo(cx - rx - 1, cy + ry - oy + 1); g.bezierCurveTo(cx - rx, top - 1, cx + rx, top - 1, cx + rx + 1, cy + ry - oy);
  g.bezierCurveTo(cx + rx * 0.6, top + 2.6, cx - rx * 0.6, top + 2.6, cx - rx - 1, cy + ry - oy + 1); g.fill();
  const s = far ? 1 : -1, ox = cx + s * rx, oy2 = cy + ry - oy - 1;
  g.lineWidth = 1.7; g.strokeStyle = C.line; g.lineCap = 'round';
  for (let i = 0; i < (far ? 2 : 3); i++) { g.beginPath(); g.moveTo(ox - s * i * 2.6, oy2 - i * 1.6 - 1); g.lineTo(ox + s * (4 + i * 1.2), oy2 - i * 3.4 - 4); g.stroke(); }
  // faint lower lid hint
  g.strokeStyle = 'rgba(120,50,30,0.45)'; g.lineWidth = 1; g.beginPath(); g.ellipse(cx, cy + ry - oy, rx * 0.8, oy, 0, 0.6, Math.PI - 0.6); g.stroke();
}
function drawFrontHair(m, pz, t) {
  // swept-back top mass with a hairline over the forehead, ear left clear
  const hair = xf(P => {
    P.moveTo(34, -22);
    P.bezierCurveTo(26, -18, 14, -22, 4, -17);
    P.bezierCurveTo(-6, -12, -12, -6, -15, 2);
    P.bezierCurveTo(-17, 10, -14, 20, -16, 28);
    P.bezierCurveTo(-24, 30, -34, 22, -38, 10);
    P.bezierCurveTo(-44, -10, -36, -38, -14, -46);
    P.bezierCurveTo(6, -52, 26, -44, 34, -22); P.closePath();
  }, m);
  part(hair, [C.hair, C.hairSh, C.hairRim], { shade: 8, rim: 2.6, lw: 3, lineLit: '#c86e36', detail: g => {
    g.setTransform(m); g.lineCap = 'round';
    g.strokeStyle = C.hairHi; g.lineWidth = 3.4; g.beginPath(); g.moveTo(-30, -26); g.bezierCurveTo(-18, -42, 6, -44, 22, -34); g.stroke();
    g.strokeStyle = 'rgba(16,6,4,0.75)'; g.lineWidth = 1.6;
    for (const [a, b, c, d] of [[28, -26, -20, -34], [14, -20, -26, -18], [0, -14, -30, -4]]) { g.beginPath(); g.moveTo(a, b); g.quadraticCurveTo((a + c) / 2, b - 10, c, d); g.stroke(); }
  } });
  // loose face-framing strands that swing with each step
  const sw = hairSway(pz, t, 0.4);
  strands(m, [[33, -24, 39 + sw * 30, -6, 1.5], [28, -26, 31 + sw * 30, -14, 1.2]], C.hair);
}

function drawShadow(pz) {
  const g = TG, G0 = GROUND + OFF;
  g.save(); g.filter = 'blur(6px)';
  g.fillStyle = 'rgba(110,62,40,0.32)';
  g.beginPath(); g.ellipse(pz.hipX - 70, G0 + 4, 120, 9, 0, 0, TAU); g.fill();
  g.fillStyle = 'rgba(90,48,30,0.35)';
  for (const ph of [pz.p, pz.p + 0.5]) { const f = footAt(ph); const k = clamp(1 - f.lift / 40, 0.2, 1); g.beginPath(); g.ellipse(pz.hipX + f.x + 10, G0 + 2, 26 * k, 4.5 * k, 0, 0, TAU); g.fill(); }
  g.restore();
}

function drawCharacter(t) {
  const pz = pose(t);
  chx.setTransform(1, 0, 0, 1, 0, 0); chx.clearRect(0, 0, BW, BH); TG = chx;
  drawShadow(pz);
  drawArm(pz, false);
  drawLeg(pz, pz.p + 0.5, true);
  drawLeg(pz, pz.p, false);
  drawTorso(pz);
  drawNeck(pz);
  drawHead(pz, t);
  drawArm(pz, true);
  chx.setTransform(1, 0, 0, 1, 0, 0);
  bx.save(); bx.setTransform(CS, 0, 0, CS, CHAR_X * (1 - CS), GROUND - (GROUND + OFF) * CS);
  bx.drawImage(CH, 0, 0); bx.restore();
}

function grade() {
  // sun flare and warm wash
  bx.save(); bx.globalCompositeOperation = 'lighter';
  bx.globalAlpha = 0.55; bx.drawImage(BG.glow, 1010 - 260, 40 - 260, 520, 520);
  bx.globalAlpha = 0.25; bx.drawImage(BG.glow, 820 - 40, 150 - 40, 80, 80); bx.drawImage(BG.glow, 700 - 22, 230 - 22, 44, 44);
  bx.restore();
  bx.save(); bx.globalCompositeOperation = 'soft-light';
  const g = bx.createLinearGradient(BW, 0, 0, BH); g.addColorStop(0, 'rgba(255,190,110,0.55)'); g.addColorStop(1, 'rgba(120,60,90,0.25)');
  bx.fillStyle = g; bx.fillRect(0, 0, BW, BH); bx.restore();
  const v = bx.createRadialGradient(BW * 0.5, BH * 0.5, BH * 0.45, BW * 0.5, BH * 0.55, BW * 0.75);
  v.addColorStop(0, 'rgba(30,12,8,0)'); v.addColorStop(1, 'rgba(30,12,8,0.32)');
  bx.fillStyle = v; bx.fillRect(0, 0, BW, BH);
}

function drawTitle() {
  ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
  ctx.font = '800 50px "Montserrat"';
  const lines = [[['Keep Your Blessings ', '#ffffff'], ['Quiet', '#f4ee2c']], [["Until They're ", '#ffffff'], ['Permanent', '#f4ee2c']]];
  const ys = [548, 611];
  lines.forEach((ln, i) => {
    const w = ln.reduce((s, [txt]) => s + ctx.measureText(txt).width, 0);
    let x = (W - w) / 2;
    for (const [txt, col] of ln) { ctx.fillStyle = col; ctx.fillText(txt, x, ys[i]); x += ctx.measureText(txt).width; }
  });
}

let ready = false;
function renderAt(t) {
  const f = Math.min(DUR * FPS - 1, Math.floor(t * FPS + 1e-6)); t = f / FPS;
  bx.setTransform(1, 0, 0, 1, 0, 0); bx.globalCompositeOperation = 'source-over'; bx.filter = 'none';
  drawBackground(t);
  drawCharacter(t);
  grade();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  drawTitle();
  ctx.drawImage(band, 0, BY);
  return cv;
}

window.SCENE = { W, H, FPS, DUR, renderAt, canvas: cv, band };
window.readyP = (async () => { try { await document.fonts.load('800 50px "Montserrat"'); } catch (e) {} buildBackground(); ready = true; })();
})();
