// Woman walking, v2: her head is traced from the reel's 3/4 close-ups (apartment shot, 5.0 s).
// Every frame is a pure function of t. No Math.random, no wall clock.
(function () {
'use strict';
const W = 1080, H = 1920, FPS = 30, DUR = 8;
const BW = 1080, BH = 608, BY = 656;
const TAU = Math.PI * 2;
const T_CYC = DUR / 7, STANCE = 0.6;
const GROUND = 520, CHAR_X = 470, K = 0.88;          // character space -> stage: x*K, y*K about (CHAR_X, GROUND)
const STRIDE = 140;                                   // character-space ankle travel during stance
const SPEED = STRIDE * K / (STANCE * T_CYC);          // stage px/s: planted feet stay planted
const LD = norm(1, -0.6);
function norm(x, y) { const l = Math.hypot(x, y); return { x: x / l, y: y / l }; }

const C = {
  line: '#3a1408', lineDeep: '#240a04', lineLit: '#f0904a',
  skin: '#e99558', skinLit: '#f8b47a', skinSh: '#b65e2e', skinRim: '#ffc893',
  blush: [232, 98, 62], freckle: 'rgba(140,58,28,0.6)',
  hair: '#331a13', hairSh: '#1b0b07', hairMid: '#4f2a1e', hairSheen: '#8f5739', hairGlow: '#e7a774', hairLit: '#6a3a28',
  cami: '#1f1917', camiSh: '#0d0908', camiLit: '#3a2c27', camiRim: '#9a5531',
  jean: '#3a3646', jeanLit: '#4f4858', jeanSh: '#1d1b25', jeanRim: '#b8743f',
  shoe: '#f2e7db', shoeLit: '#fff8ee', shoeSh: '#baa592', shoeRim: '#fff6ea', sole: '#d9cbbb',
  eyeW: '#fdf1e6', iris: '#1c0d08', lid: '#160805', lip: '#d4664a',
};

function rng(seed) { let a = seed >>> 0; return () => { a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const lerp = (a, b, u) => a + (b - a) * u;
const ss = u => { u = clamp(u, 0, 1); return u * u * (3 - 2 * u); };
const eio = u => 0.5 - 0.5 * Math.cos(Math.PI * clamp(u, 0, 1));
const rgba = (c, a) => `rgba(${c[0]},${c[1]},${c[2]},${a})`;

// ---------- canvases ----------
const cv = document.createElement('canvas'); cv.width = W; cv.height = H;
const ctx = cv.getContext('2d');
const mk = (w = BW, h = BH) => { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; };
const band = mk(), bx = band.getContext('2d');
const LINE = mk(), FILL = mk(), MASK = mk();
const lx = LINE.getContext('2d'), fx = FILL.getContext('2d'), mx = MASK.getContext('2d');

// ---------- camera: track, then push in to a medium close-up ----------
let G = new DOMMatrix(), ZS = 1;
const FOCUS = { x: CHAR_X + 12, y: 300 };
function camAt(t) {
  const u = eio((t - 1.6) / 5.4);
  return { z: lerp(1, 2.05, u), sx: lerp(FOCUS.x, 440, u), sy: lerp(FOCUS.y, 548, u) };
}
function layerMatrix(cam, d) {
  const z = 1 + (cam.z - 1) * d, sx = FOCUS.x + (cam.sx - FOCUS.x) * d, sy = FOCUS.y + (cam.sy - FOCUS.y) * d;
  return new DOMMatrix().translateSelf(sx, sy).scaleSelf(z, z).translateSelf(-FOCUS.x, -FOCUS.y);
}

// ---------- path helpers ----------
function addPoly(P, pts) { let s = 0; for (let i = 0; i < pts.length; i++) { const a = pts[i], b = pts[(i + 1) % pts.length]; s += a[0] * b[1] - b[0] * a[1]; } if (s < 0) pts = pts.slice().reverse(); P.moveTo(pts[0][0], pts[0][1]); for (let i = 1; i < pts.length; i++) P.lineTo(pts[i][0], pts[i][1]); P.closePath(); }
function addCircle(P, x, y, r) { P.moveTo(x + r, y); P.arc(x, y, r, 0, TAU, false); P.closePath(); }
function limb(pts) {
  const P = new Path2D();
  for (let i = 0; i < pts.length - 1; i++) {
    const [ax, ay, aw] = pts[i], [bx_, by, bw] = pts[i + 1];
    const dx = bx_ - ax, dy = by - ay, l = Math.hypot(dx, dy) || 1, nx = -dy / l, ny = dx / l;
    addPoly(P, [[ax + nx * aw / 2, ay + ny * aw / 2], [bx_ + nx * bw / 2, by + ny * bw / 2], [bx_ - nx * bw / 2, by - ny * bw / 2], [ax - nx * aw / 2, ay - ny * aw / 2]]);
  }
  for (const [x, y, w] of pts) addCircle(P, x, y, w / 2);
  return P;
}
function cr(P, pts, closed = true) {
  const n = pts.length, at = i => closed ? pts[(i + n) % n] : pts[clamp(i, 0, n - 1)];
  P.moveTo(pts[0][0], pts[0][1]);
  for (let i = 0; i < (closed ? n : n - 1); i++) {
    const p0 = at(i - 1), p1 = at(i), p2 = at(i + 1), p3 = at(i + 2);
    P.bezierCurveTo(p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6, p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6, p2[0], p2[1]);
  }
  if (closed) P.closePath();
}
function shape(pts) { const P = new Path2D(); cr(P, pts, true); return P; }
function T(P, m) { const Q = new Path2D(); Q.addPath(P, m); return Q; }
function mat(x, y, rot = 0, s = 1) { return new DOMMatrix().translateSelf(x, y).rotateSelf(rot * 180 / Math.PI).scaleSelf(s, s); }
function ribbon(x0, y0, cx, cy, x1, y1, w0, w1) {
  const N = 14, L = [], R = [];
  for (let i = 0; i <= N; i++) {
    const u = i / N, a = (1 - u) * (1 - u), b = 2 * (1 - u) * u, c = u * u;
    const x = a * x0 + b * cx + c * x1, y = a * y0 + b * cy + c * y1;
    const tx = 2 * (1 - u) * (cx - x0) + 2 * u * (x1 - cx), ty = 2 * (1 - u) * (cy - y0) + 2 * u * (y1 - cy), l = Math.hypot(tx, ty) || 1;
    const w = lerp(w0, w1, u) / 2; L.push([x - ty / l * w, y + tx / l * w]); R.push([x + ty / l * w, y - tx / l * w]);
  }
  const P = new Path2D(); addPoly(P, L.concat(R.reverse())); return P;
}

// ---------- painted part renderer: col = [base, lit, shadow, rim]; P already in screen space ----------
function part(P, col, o = {}) {
  const s = Math.sqrt(ZS);
  const lw = (o.lw ?? 2.4) * s, sh = (o.shade ?? 8) * ZS, rim = (o.rim ?? 2.2) * s, hl = (o.hl ?? 14) * ZS;
  lx.setTransform(1, 0, 0, 1, 0, 0); lx.globalCompositeOperation = 'source-over'; lx.clearRect(0, 0, BW, BH);
  if (lw > 0) {
    lx.fillStyle = lx.strokeStyle = o.line || C.line; lx.lineJoin = 'round'; lx.lineWidth = lw * 2;
    lx.fill(P); lx.stroke(P);
    lx.translate(-LD.x * lw * 0.7, -LD.y * lw * 0.7); lx.lineWidth = lw * 2.2; lx.stroke(P); lx.setTransform(1, 0, 0, 1, 0, 0);
    if (!o.noLitLine) { lx.globalCompositeOperation = 'source-atop'; lx.translate(LD.x * lw * 1.8, LD.y * lw * 1.8); lx.fillStyle = o.lineLit || C.lineLit; lx.fill(P); lx.setTransform(1, 0, 0, 1, 0, 0); }
  }
  fx.setTransform(1, 0, 0, 1, 0, 0); fx.globalCompositeOperation = 'source-over'; fx.filter = 'none'; fx.clearRect(0, 0, BW, BH);
  fx.fillStyle = col[0]; fx.fill(P);
  fx.globalCompositeOperation = 'source-atop';
  if (col[1] && hl > 0) { mask(P, -LD.x * hl, -LD.y * hl, col[1]); fx.globalAlpha = o.hlA ?? 0.7; fx.filter = `blur(${hl * 0.45}px)`; fx.drawImage(MASK, 0, 0); fx.filter = 'none'; fx.globalAlpha = 1; }
  if (sh > 0) { mask(P, LD.x * sh, LD.y * sh, col[2]); fx.filter = `blur(${(o.soft ?? 2.4) * s}px)`; fx.drawImage(MASK, 0, 0); fx.filter = 'none'; }
  if (rim > 0 && col[3]) { mask(P, -LD.x * rim, -LD.y * rim, col[3]); fx.filter = `blur(${0.7 * s}px)`; fx.drawImage(MASK, 0, 0); fx.filter = 'none'; }
  if (o.detail) { o.detail(fx); fx.setTransform(1, 0, 0, 1, 0, 0); fx.globalAlpha = 1; fx.filter = 'none'; }
  fx.globalCompositeOperation = 'source-over';
  bx.drawImage(LINE, 0, 0); bx.drawImage(FILL, 0, 0);
}
function mask(P, dx, dy, color) {
  mx.setTransform(1, 0, 0, 1, 0, 0); mx.globalCompositeOperation = 'source-over'; mx.clearRect(0, 0, BW, BH);
  mx.fillStyle = '#000'; mx.fill(P);
  mx.globalCompositeOperation = 'destination-out'; mx.translate(dx, dy); mx.fill(P); mx.setTransform(1, 0, 0, 1, 0, 0);
  mx.globalCompositeOperation = 'source-in'; mx.fillStyle = color; mx.fillRect(0, 0, BW, BH); mx.globalCompositeOperation = 'source-over';
}
const SKIN = [C.skin, C.skinLit, C.skinSh, C.skinRim];
const dim = (cols, k) => cols.map(c => c && shadeHex(c, k));
function shadeHex(h, k) { const n = parseInt(h.slice(1), 16); const f = v => Math.round(clamp(v * k, 0, 255)).toString(16).padStart(2, '0'); return '#' + f((n >> 16) & 255) + f((n >> 8) & 255) + f(n & 255); }

// ---------- background ----------
const BG = {};
function buildBackground() {
  const rs = rng(7);
  const sky = mk(BW + 400, BH + 300), s = sky.getContext('2d');
  let g = s.createLinearGradient(0, 0, 0, 620);
  g.addColorStop(0, '#86afe0'); g.addColorStop(0.4, '#b9d0e9'); g.addColorStop(0.72, '#f3d8b6'); g.addColorStop(1, '#f6c48f');
  s.fillStyle = g; s.fillRect(0, 0, sky.width, sky.height);
  const rg = s.createRadialGradient(1210, 190, 0, 1210, 190, 760);
  rg.addColorStop(0, 'rgba(255,242,205,0.95)'); rg.addColorStop(0.08, 'rgba(255,226,170,0.7)'); rg.addColorStop(0.4, 'rgba(255,196,130,0.25)'); rg.addColorStop(1, 'rgba(255,190,120,0)');
  s.fillStyle = rg; s.fillRect(0, 0, sky.width, sky.height);
  s.filter = 'blur(12px)';
  for (let i = 0; i < 8; i++) { s.fillStyle = `rgba(255,238,222,${0.22 + rs() * 0.25})`; s.beginPath(); s.ellipse(rs() * sky.width, 180 + rs() * 150, 160 + rs() * 240, 18 + rs() * 16, 0, 0, TAU); s.fill(); }
  BG.sky = sky;
  const farW = BW + 900, far = mk(farW, BH), f = far.getContext('2d');
  let x = -20;
  while (x < farW) { const w = 40 + rs() * 90, h = 70 + rs() * 150; f.fillStyle = `rgb(${178 + rs() * 16 | 0},${176 + rs() * 14 | 0},${190 + rs() * 14 | 0})`; f.fillRect(x, 400 - h, w, h + 40); x += w + rs() * 10; }
  const hz = f.createLinearGradient(0, 230, 0, 420); hz.addColorStop(0, 'rgba(246,210,170,0)'); hz.addColorStop(1, 'rgba(246,206,160,0.55)'); f.fillStyle = hz; f.fillRect(0, 0, farW, BH);
  BG.far = blurred(far, 3.5);
  const midW = BW + Math.ceil(SPEED * DUR * 0.42) + 600, mid = mk(midW, BH), m = mid.getContext('2d');
  x = -40;
  while (x < midW) {
    const w = 120 + rs() * 160, h = 60 + rs() * 70, base = 440;
    m.fillStyle = ['#d9b08f', '#c99c84', '#e2c3a4', '#b98f7a'][rs() * 4 | 0]; m.fillRect(x, base - h, w, h + 20);
    m.fillStyle = 'rgba(120,70,50,0.25)'; m.fillRect(x, base - h, w * 0.18, h + 20);
    m.fillStyle = 'rgba(255,230,190,0.35)'; m.fillRect(x + w - 6, base - h, 6, h + 20);
    m.fillStyle = 'rgba(90,70,80,0.5)'; for (let k = 0; k < Math.floor(w / 46); k++) m.fillRect(x + 14 + k * 46, base - h + 18, 22, 20);
    m.fillStyle = '#8c6a5a'; m.fillRect(x - 4, base - h - 6, w + 8, 8);
    x += w + 40 + rs() * 120;
  }
  x = 30; while (x < midW) { tree(m, x, 452, 58 + rs() * 36, rs); x += 120 + rs() * 120; }
  for (let hx = -20; hx < midW; hx += 26) { const gg = m.createLinearGradient(hx - 30, 470, hx + 30, 446); gg.addColorStop(0, '#596732'); gg.addColorStop(1, '#a5a052'); m.fillStyle = gg; m.beginPath(); m.ellipse(hx, 462, 30, 18 + rs() * 6, 0, 0, TAU); m.fill(); }
  BG.mid = blurred(mid, 2.4);
  BG.lamps = []; for (let p = 200; p < BW + SPEED * DUR + 800; p += 520 + rs() * 120) BG.lamps.push(p);
  BG.dapples = []; for (let p = 0; p < BW + SPEED * DUR + 600; p += 60 + rs() * 140) BG.dapples.push([p, 494 + rs() * 46, 30 + rs() * 50, 4 + rs() * 7]);
  BG.glow = glowSprite(256, [255, 214, 150], 2.0);
}
function tree(m, x, base, r, rs) {
  m.fillStyle = '#6b4a36'; m.fillRect(x - 5, base - r * 1.1, 10, r * 1.1);
  const greens = ['#5f6b34', '#6e7a3a', '#7d8a44'];
  for (let k = 0; k < 7; k++) {
    const ox = (rs() - 0.5) * r * 1.2, oy = -r * 1.25 + (rs() - 0.5) * r * 0.8, rr = r * (0.45 + rs() * 0.3), cx = x + ox, cy = base + oy;
    const gr = m.createLinearGradient(cx - rr, cy + rr * 0.6, cx + rr, cy - rr * 0.6); gr.addColorStop(0, '#4b5a2c'); gr.addColorStop(0.55, greens[k % 3]); gr.addColorStop(1, '#c3b45e');
    m.fillStyle = gr; m.beginPath(); m.ellipse(cx, cy, rr, rr * 0.9, 0, 0, TAU); m.fill();
  }
}
function blurred(src, px) { const c = mk(src.width, src.height), g = c.getContext('2d'); g.filter = `blur(${px}px)`; g.drawImage(src, 0, 0); return c; }
function glowSprite(size, rgb, power) {
  const c = mk(size, size), g = c.getContext('2d'), im = g.createImageData(size, size), m = (size - 1) / 2;
  for (let j = 0; j < size; j++) for (let i = 0; i < size; i++) { const d = Math.hypot(i - m, j - m) / (size / 2), o = (j * size + i) * 4; im.data[o] = rgb[0]; im.data[o + 1] = rgb[1]; im.data[o + 2] = rgb[2]; im.data[o + 3] = d >= 1 ? 0 : 255 * Math.pow(1 - d, power); }
  g.putImageData(im, 0, 0); return c;
}
function drawBackground(t, cam) {
  const scroll = SPEED * t;
  const set = d => { const m = layerMatrix(cam, d); bx.setTransform(m.a, m.b, m.c, m.d, m.e, m.f); };
  set(0.03); bx.drawImage(BG.sky, -200, -150);
  set(0.1); bx.drawImage(BG.far, -(scroll * 0.08) % 600 - 100, 0);
  set(0.45); bx.filter = `blur(${(cam.z - 1) * 2.5}px)`; bx.drawImage(BG.mid, -scroll * 0.42 - 100, 0); bx.filter = 'none';
  set(0.85);
  let g = bx.createLinearGradient(0, 455, 0, 492); g.addColorStop(0, '#8d9046'); g.addColorStop(1, '#a29a52'); bx.fillStyle = g; bx.fillRect(-400, 455, BW + 800, 40);
  bx.filter = `blur(${1.2 + (cam.z - 1) * 3}px)`;
  for (const p of BG.lamps) {
    const x = p - scroll * 0.8; if (x < -300 || x > BW + 300) continue;
    bx.fillStyle = '#4a4148'; bx.fillRect(x - 4, 170, 8, 318); bx.fillStyle = '#3c343a'; bx.fillRect(x - 7, 470, 14, 20);
    bx.fillRect(x - 2, 168, 40, 6); bx.fillStyle = '#5a5058'; bx.beginPath(); bx.ellipse(x + 40, 176, 16, 7, 0, 0, TAU); bx.fill();
    bx.fillStyle = 'rgba(255,215,150,0.75)'; bx.fillRect(x + 3, 170, 2, 318);
  }
  bx.filter = 'none';
  set(1);
  const top = 490, kerb = 548;
  g = bx.createLinearGradient(0, top, 0, kerb); g.addColorStop(0, '#d8b99a'); g.addColorStop(1, '#e8cba8'); bx.fillStyle = g; bx.fillRect(-400, top, BW + 800, kerb - top);
  bx.save(); bx.filter = 'blur(2px)'; bx.fillStyle = 'rgba(120,78,60,0.22)';
  for (const p of BG.lamps) { const x = p - scroll * 0.8; bx.beginPath(); bx.moveTo(x - 4, top); bx.lineTo(x + 4, top); bx.lineTo(x - 150, kerb); bx.lineTo(x - 166, kerb); bx.fill(); }
  bx.filter = 'blur(5px)'; bx.fillStyle = 'rgba(120,74,52,0.18)';
  for (const [dx_, dy, w, h] of BG.dapples) { const x = dx_ - scroll; if (x < -300 || x > BW + 300) continue; bx.beginPath(); bx.ellipse(x, dy, w, h, 0, 0, TAU); bx.fill(); }
  bx.restore();
  bx.strokeStyle = 'rgba(150,104,78,0.55)'; bx.lineWidth = 2;
  for (let k = Math.floor((scroll - 400) / 150); k < (scroll + BW + 400) / 150; k++) { const x = k * 150 - scroll; bx.beginPath(); bx.moveTo(x + 18, top + 1); bx.lineTo(x - 8, kerb - 1); bx.stroke(); }
  bx.fillStyle = 'rgba(255,236,206,0.6)'; bx.fillRect(-400, top, BW + 800, 2);
  bx.fillStyle = '#efd7bb'; bx.fillRect(-400, kerb, BW + 800, 6);
  g = bx.createLinearGradient(0, kerb + 6, 0, kerb + 18); g.addColorStop(0, '#a98a74'); g.addColorStop(1, '#7c6457'); bx.fillStyle = g; bx.fillRect(-400, kerb + 6, BW + 800, 12);
  const road = kerb + 18; g = bx.createLinearGradient(0, road, 0, BH + 200); g.addColorStop(0, '#57525c'); g.addColorStop(1, '#3d3a44'); bx.fillStyle = g; bx.fillRect(-400, road, BW + 800, 300);
  bx.fillStyle = '#ece0cc'; for (let k = Math.floor((scroll * 1.15 - 400) / 260); k < (scroll * 1.15 + BW + 400) / 260; k++) bx.fillRect(k * 260 - scroll * 1.15, BH - 14, 130, 8);
  bx.setTransform(1, 0, 0, 1, 0, 0);
}

// ---------- walk rig (character space: origin on the ground under her hip, y up is negative) ----------
function footAt(p) {
  p = ((p % 1) + 1) % 1;
  if (p < STANCE) {
    const u = p / STANCE, x = STRIDE / 2 - STRIDE * u;
    let pitch = 0, lift = 0;
    if (u < 0.14) { pitch = lerp(-0.28, 0, ss(u / 0.14)); lift = Math.sin(-pitch) * 11; }
    else if (u > 0.7) { pitch = 0.6 * ss((u - 0.7) / 0.3); lift = Math.sin(pitch) * 32; }
    return { x, lift, pitch };
  }
  const u = (p - STANCE) / (1 - STANCE);
  const x = -STRIDE / 2 + STRIDE * eio(u);
  const arc = 12 + 22 * Math.sin(Math.PI * Math.pow(u, 0.75));
  const lift = u < 0.12 ? lerp(19, 12 + 22 * Math.sin(Math.PI * Math.pow(0.12, 0.75)), u / 0.12) : arc;
  const pitch = u < 0.5 ? lerp(0.6, 0.15, ss(u / 0.5)) : lerp(0.15, -0.28, ss((u - 0.5) / 0.5));
  return { x, lift, pitch };
}
function ik(hx, hy, ax, ay, l1, l2, bend) {
  let dx = ax - hx, dy = ay - hy, d = Math.hypot(dx, dy);
  const dm = Math.min(d, l1 + l2 - 0.5); if (d > dm) { ax = hx + dx / d * dm; ay = hy + dy / d * dm; d = dm; dx = ax - hx; dy = ay - hy; }
  const a = Math.atan2(dy, dx), b = Math.acos(clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), -1, 1)), ang = a - bend * b;
  return { kx: hx + Math.cos(ang) * l1, ky: hy + Math.sin(ang) * l1, ax, ay };
}
let CM = new DOMMatrix();
function csLimb(pts) { const s = CM.a; return limb(pts.map(([x, y, w]) => { const p = CM.transformPoint(new DOMPoint(x, y)); return [p.x, p.y, w * s]; })); }
function pose(t) {
  const p = (t / T_CYC) % 1;
  return { p, hx: 0, hy: -266 + 4 * Math.cos(4 * Math.PI * p) - 1, lean: 0.055, sway: 0.012 * Math.sin(TAU * p) };
}
const BLINKS = []; { const r = rng(101); let t = 0.8; while (t < DUR) { BLINKS.push(t); t += 1.9 + r() * 1.5; } }
function eyeOpen(t) { for (const b of BLINKS) { const d = t - b; if (d >= 0 && d < 0.17) return d < 0.06 ? 1 - d / 0.06 : (d - 0.06) / 0.11; } return 1; }
function face(t) {
  const g = ss((t - 5.5) / 0.7);
  return { lookX: lerp(3.5, -3.8, g), lookY: lerp(-1, 0.5, g), smile: lerp(0.35, 1, g), squint: 0.25 * g, tilt: lerp(-0.07, -0.02, g), open: eyeOpen(t) };
}

// ---------- body ----------
function drawLeg(pz, phase, far) {
  const f = footAt(phase);
  const hx = pz.hx + (far ? -7 : 5), hy = pz.hy + (far ? -2 : 2);
  const ax = pz.hx + f.x + 4, ay = -16 - f.lift;
  const L = ik(hx, hy, ax, ay, 128, 124, 1);
  const jean = far ? dim([C.jean, C.jeanLit, C.jeanSh, C.jeanRim], 0.74) : [C.jean, C.jeanLit, C.jeanSh, C.jeanRim];
  const shoeC = far ? dim([C.shoe, C.shoeLit, C.shoeSh, C.shoeRim], 0.8) : [C.shoe, C.shoeLit, C.shoeSh, C.shoeRim];
  const sm = CM.multiply(mat(L.ax, L.ay + 4, f.pitch));
  part(T(shape([[-16, -8], [-17, 6], [-10, 14], [10, 15], [34, 14], [44, 9], [40, 1], [24, -6], [8, -12], [-6, -13]]), sm), shoeC, { shade: 5, rim: 1.6, lw: 2.2, hl: 6, detail: g => {
    g.setTransform(sm); g.fillStyle = far ? '#a89a8a' : C.sole; g.fillRect(-20, 9, 70, 8);
    g.strokeStyle = far ? '#6d6058' : '#c9b5a1'; g.lineWidth = 1.4; g.beginPath(); g.moveTo(2, -9); g.lineTo(14, -2); g.moveTo(6, -11); g.lineTo(18, -4); g.stroke();
  } });
  part(csLimb([[hx, hy, 54], [L.kx, L.ky, 35], [L.ax, L.ay - 2, 27]]), jean, { shade: 9, rim: 2.6, lw: 2.6, hl: 12, detail: g => {
    g.setTransform(CM); g.lineCap = 'round';
    g.strokeStyle = far ? 'rgba(150,110,60,0.45)' : 'rgba(190,140,72,0.75)'; g.lineWidth = 1.4; g.setLineDash([4, 3]);
    g.beginPath(); g.moveTo(hx + 6, hy + 8); g.lineTo(L.kx + 3, L.ky); g.lineTo(L.ax + 2, L.ay - 5); g.stroke(); g.setLineDash([]);
    g.strokeStyle = 'rgba(16,14,22,0.55)'; g.lineWidth = 2; g.beginPath(); g.moveTo(L.kx - 10, L.ky - 4); g.quadraticCurveTo(L.kx - 2, L.ky + 4, L.kx + 8, L.ky + 2); g.stroke();
    g.strokeStyle = 'rgba(16,14,22,0.7)'; g.beginPath(); g.moveTo(L.ax - 14, L.ay - 8); g.lineTo(L.ax + 14, L.ay - 9); g.stroke();
  } });
}
function torsoM(pz) { return mat(pz.hx, pz.hy, pz.lean + pz.sway); }
function drawArm(pz, near) {
  const swing = (near ? -1 : 1) * 0.3 * Math.cos(TAU * pz.p - 0.25);
  const sh = torsoM(pz).transformPoint(new DOMPoint(near ? 4 : -6, -154));
  const sx = sh.x, sy = sh.y, upper = 80, lower = 74;
  const a1 = Math.PI / 2 - swing - pz.lean, ex = sx + Math.cos(a1) * upper, ey = sy + Math.sin(a1) * upper;
  const a2 = a1 - (0.2 + 0.32 * Math.max(0, swing / 0.3)), wx = ex + Math.cos(a2) * lower, wy = ey + Math.sin(a2) * lower;
  const cols = near ? SKIN : dim(SKIN, 0.8);
  part(csLimb([[sx, sy, 21], [lerp(sx, ex, 0.5), lerp(sy, ey, 0.5), 18], [ex, ey, 14.5], [lerp(ex, wx, 0.45), lerp(ey, wy, 0.45), 15], [wx, wy, 11]]), cols, { shade: 6, rim: 2.2, lw: 2.2, hl: 8 });
  const hm = CM.multiply(mat(wx, wy, a2 - Math.PI / 2));
  part(T(shape([[-5, -2], [-7, 8], [-6, 19], [-3, 28], [1, 31], [5, 29], [7, 21], [10, 13], [13, 7], [10, 1], [3, -4]]), hm), cols, { shade: 4, rim: 1.6, lw: 1.8, hl: 5, detail: g => {
    g.setTransform(hm); g.strokeStyle = 'rgba(130,50,22,0.6)'; g.lineWidth = 0.9; g.lineCap = 'round';
    g.beginPath(); g.moveTo(-1, 16); g.quadraticCurveTo(0, 23, 0.5, 28); g.moveTo(2.5, 15); g.quadraticCurveTo(3.5, 21, 3.5, 26); g.moveTo(7, 9); g.quadraticCurveTo(5, 12, 4, 15); g.stroke();
  } });
}
function drawTorso(pz) {
  const tm = CM.multiply(torsoM(pz));
  part(T(shape([[-21, -40], [-20, -72], [-25, -104], [-27, -134], [-21, -154], [-8, -165], [10, -164], [22, -153], [30, -136], [39, -116], [33, -98], [22, -82], [19, -60], [19, -40]]), tm), SKIN, { shade: 9, rim: 2.4, lw: 2.4, hl: 14, detail: g => {
    g.setTransform(tm); g.lineCap = 'round';
    g.strokeStyle = 'rgba(150,62,28,0.55)'; g.lineWidth = 1.4; g.beginPath(); g.moveTo(4, -152); g.quadraticCurveTo(14, -150, 22, -152); g.stroke();
    const gr = g.createRadialGradient(10, -158, 0, 10, -158, 22); gr.addColorStop(0, 'rgba(150,60,30,0.45)'); gr.addColorStop(1, 'rgba(150,60,30,0)'); g.fillStyle = gr; g.fillRect(-20, -185, 60, 50);
    g.strokeStyle = 'rgba(150,62,28,0.4)'; g.lineWidth = 1.2; g.beginPath(); g.moveTo(3, -56); g.quadraticCurveTo(5, -50, 4, -45); g.stroke();
  } });
  part(T(shape([[-20, -64], [-24, -94], [-28, -116], [-24, -138], [-12, -133], [4, -129], [17, -134], [31, -127], [41, -113], [37, -99], [26, -89], [21, -79], [20, -64], [0, -61]]), tm), [C.cami, C.camiLit, C.camiSh, C.camiRim], { shade: 10, rim: 2.4, lw: 2.4, hl: 10, lineLit: '#a05a34', detail: g => {
    g.setTransform(tm); g.strokeStyle = 'rgba(255,190,140,0.18)'; g.lineWidth = 2; g.beginPath(); g.moveTo(18, -128); g.quadraticCurveTo(36, -118, 37, -102); g.stroke();
    g.strokeStyle = 'rgba(0,0,0,0.45)'; g.lineWidth = 1.2; g.beginPath(); g.moveTo(-18, -96); g.quadraticCurveTo(-6, -92, 6, -97); g.stroke();
  } });
  for (const [a, b, c, d] of [[-14, -134, -3, -164], [16, -132, 9, -164]]) {
    const st = new Path2D(); addPoly(st, [[a - 1.6, b], [c - 1.4, d], [c + 1.4, d], [a + 1.6, b]]);
    part(T(st, tm), [C.cami, C.camiLit, C.camiSh, C.camiRim], { shade: 1, rim: 0.8, lw: 1.3, hl: 0, lineLit: '#a05a34' });
  }
  part(T(shape([[-22, -46], [-30, -26], [-34, -4], [-28, 14], [-8, 22], [14, 20], [26, 8], [26, -14], [22, -32], [21, -48], [0, -50]]), tm), [C.jean, C.jeanLit, C.jeanSh, C.jeanRim], { shade: 10, rim: 2.6, lw: 2.6, hl: 12, detail: g => {
    g.setTransform(tm); g.strokeStyle = 'rgba(190,140,72,0.8)'; g.lineWidth = 1.3; g.setLineDash([4, 3]);
    g.beginPath(); g.moveTo(-23, -36); g.quadraticCurveTo(0, -41, 24, -38); g.stroke();
    g.beginPath(); g.moveTo(9, -34); g.quadraticCurveTo(15, -18, 26, -10); g.stroke();
    g.beginPath(); g.moveTo(-26, -10); g.quadraticCurveTo(-14, -6, -4, -12); g.stroke();
    g.setLineDash([]); g.fillStyle = '#d3a45a'; g.beginPath(); g.arc(19, -42, 2.6, 0, TAU); g.fill();
    g.strokeStyle = 'rgba(14,12,20,0.6)'; g.lineWidth = 2; g.beginPath(); g.moveTo(-13, -48); g.lineTo(-12, -36); g.stroke();
  } });
}
function drawNeck(pz) {
  const tm = torsoM(pz), a = tm.transformPoint(new DOMPoint(5, -156)), b = tm.transformPoint(new DOMPoint(9, -173));
  part(csLimb([[a.x, a.y, 22], [b.x, b.y, 17]]), SKIN, { shade: 7, rim: 1.6, lw: 1.8, hl: 5, lineLit: '#c8723c' });
}

// ---------- head: coordinates traced from the reel, origin at the bridge of the nose ----------
const HS = 0.6;
const HEAD = {
  face: [[-30, -47], [10, -60], [43, -46], [50, -20], [50, 0], [48, 18], [43, 34], [33, 48], [20, 58], [8, 61], [-6, 57], [-22, 46], [-35, 33], [-42, 12], [-41, -18]],
  ear: [[-41, 7], [-49, 1], [-59, 3], [-66, 13], [-65, 27], [-57, 37], [-47, 38], [-41, 31]],
  shell: [[47, -30], [38, -48], [22, -57], [6, -60], [-10, -56], [-24, -47], [-34, -33], [-40, -16], [-47, -5], [-58, -8], [-70, -2], [-77, 8], [-82, 22], [-90, 22], [-95, 6], [-94, -18], [-84, -46], [-60, -68], [-30, -79], [0, -81], [26, -75], [46, -62], [55, -46], [54, -34]],
  bun: [[-92, -50, 30], [-110, -26, 19], [-74, -74, 20], [-112, -62, 16]],
};
const FR = rng(77);
const FRECKLES = Array.from({ length: 26 }, () => [FR(), FR(), 0.6 + FR() * 0.6]);
const FLY = Array.from({ length: 15 }, () => {
  const a = -3.3 + FR() * 2.6, cxr = -92 + FR() * 16, cyr = -52 + FR() * 10, r = 30 + FR() * 10;
  return [cxr + Math.cos(a) * r, cyr + Math.sin(a) * r * 0.9, a + (FR() - 0.5) * 1.6, 9 + FR() * 16, 0.7 + FR() * 0.6, FR() * TAU];
});
function headM(pz, fc) {
  const top = torsoM(pz).transformPoint(new DOMPoint(11, -170));
  return CM.multiply(mat(top.x, top.y, fc.tilt + 0.022 * Math.sin(4 * Math.PI * pz.p - 0.6), HS)).translateSelf(-9, -64);
}
function sway(pz, t, lag) { return 0.06 * Math.sin(4 * Math.PI * pz.p - lag) + 0.025 * Math.sin(TAU * t / 2.3 + lag); }

function drawHead(pz, t) {
  const fc = face(t), hm = headM(pz, fc), sw = sway(pz, t, 0.8);
  // behind the face: nape mass, far-side curtain, bun
  for (const L of [[-66, -8, -94, 14, -88 + sw * 30, 40, 18], [49, -36, 66, 4, 57 + sw * 40, 52, 9]]) {
    part(T(leaf(...L), hm), [C.hairSh, C.hairLit, C.hairSh, C.hairGlow], { shade: 3, rim: 2, lw: 0.6, hl: 5, hlA: 0.5, line: '#1c0b06', lineLit: '#b8703f', soft: 1.6, detail: g => {
      g.setTransform(hm); taper(g, L[0], L[1], L[2], L[3], L[4], L[5], 3, 0.5, 'rgba(110,62,40,0.5)'); taper(g, L[0] + 3, L[1], L[2] + 4, L[3], L[4] + 2, L[5], 1.4, 0.3, 'rgba(14,5,3,0.5)');
    } });
  }
  drawBun(hm, sw);
  part(T(shape(HEAD.face), hm), SKIN, { shade: 7, rim: 2.2, lw: 1.7, hl: 10, soft: 3.2, detail: g => faceDetail(g, hm, fc) });
  drawFeatures(hm, fc);
  drawShell(hm);

  part(T(shape(HEAD.ear), hm), SKIN, { shade: 4, rim: 2, lw: 1.5, hl: 4, detail: g => {
    g.setTransform(hm); g.strokeStyle = 'rgba(160,62,26,0.85)'; g.lineWidth = 1.8; g.lineCap = 'round';
    g.lineWidth = 1.4; g.beginPath(); g.moveTo(-46, 9); g.bezierCurveTo(-55, 6, -60, 16, -57, 24); g.bezierCurveTo(-54, 30, -49, 31, -47, 28); g.stroke();
    g.beginPath(); g.moveTo(-50, 16); g.quadraticCurveTo(-53, 21, -49, 23); g.stroke();
    g.fillStyle = 'rgba(255,170,110,0.55)'; g.beginPath(); g.ellipse(-62, 19, 2.2, 8, 0.1, 0, TAU); g.fill();
  } });
  wisps(hm, [
    [-35, -34, -50, -8, -34 + sw * 40, 16, -42 + sw * 70, 42, 3.2],
    [-31, -40, -44, -4, -26 + sw * 40, 22, -33 + sw * 60, 50, 2.2],
    [-38, -24, -50, 2, -46 + sw * 40, 22, -50 + sw * 60, 38, 1.8],
    [-27, -44, -38, -14, -22 + sw * 30, 8, -24 + sw * 40, 30, 1.4],
    [51, -36, 62, -6, 52 + sw * 40, 20, 58 + sw * 60, 50, 2.8],
    [55, -30, 66, 0, 60 + sw * 40, 26, 64 + sw * 50, 44, 1.6],
    [48, -44, 60, -20, 56 + sw * 40, 6, 62 + sw * 50, 30, 2],
    [53, -40, 66, -14, 64 + sw * 30, 12, 70 + sw * 40, 34, 1.2],
    [44, -50, 58, -30, 54 + sw * 30, -6, 58 + sw * 40, 16, 1.6],
    [12, -60, 22, -54, 30 + sw * 20, -44, 34 + sw * 30, -30, 1.4],
    [20, -58, 32, -52, 40 + sw * 20, -44, 44 + sw * 30, -34, 1.1],
  ]);
  edgeStrands(hm, pz, t);
  flyaways(hm, pz, t);
}
function faceDetail(g, hm, fc) {
  g.setTransform(hm);
  let gr = g.createLinearGradient(0, 30, 0, 70); gr.addColorStop(0, 'rgba(255,170,110,0)'); gr.addColorStop(1, 'rgba(255,170,110,0.35)'); g.fillStyle = gr; g.fillRect(-50, 30, 110, 40);
  gr = g.createLinearGradient(0, -60, 0, -30); gr.addColorStop(0, 'rgba(120,46,20,0.55)'); gr.addColorStop(1, 'rgba(120,46,20,0)'); g.fillStyle = gr; g.fillRect(-50, -62, 110, 34);
  for (const [x, y, r] of [[-18, -8, 24], [29, -12, 16]]) { gr = g.createRadialGradient(x, y, 0, x, y, r); gr.addColorStop(0, 'rgba(176,82,44,0.18)'); gr.addColorStop(1, 'rgba(176,82,44,0)'); g.fillStyle = gr; g.fillRect(x - r, y - r, r * 2, r * 2); }
  gr = g.createLinearGradient(2, 0, 12, 0); gr.addColorStop(0, 'rgba(170,70,32,0.5)'); gr.addColorStop(1, 'rgba(170,70,32,0)');
  g.fillStyle = gr; g.beginPath(); g.moveTo(3, -6); g.quadraticCurveTo(4, 8, 6, 16); g.quadraticCurveTo(10, 19, 12, 16); g.quadraticCurveTo(8, 6, 9, -6); g.closePath(); g.fill();
  g.fillStyle = 'rgba(176,66,36,0.55)'; g.beginPath(); g.ellipse(12, 18.5, 7.5, 3, -0.05, 0, TAU); g.fill();
  g.fillStyle = 'rgba(255,214,170,0.75)'; g.beginPath(); g.ellipse(14, 12, 3.2, 2.4, 0, 0, TAU); g.fill();
  const lift = fc.smile * 3;
  for (const [x, y, rx, ry, a] of [[-27, 15 - lift, 20, 13, 0.6], [36, 11 - lift, 11, 9, 0.55], [12, 6, 8, 5, 0.3]]) {
    g.save(); g.translate(x, y); g.scale(1, ry / rx); gr = g.createRadialGradient(0, 0, 0, 0, 0, rx); gr.addColorStop(0, rgba(C.blush, a)); gr.addColorStop(1, rgba(C.blush, 0)); g.fillStyle = gr; g.fillRect(-rx, -rx, rx * 2, rx * 2); g.restore();
  }
  g.fillStyle = C.freckle;
  for (const [u, v, s] of FRECKLES) { const x = -36 + u * 76, y = 4 + v * 12 - lift; if (x > 0 && x < 18 && y < 8) continue; g.beginPath(); g.arc(x, y, 0.75 * s, 0, TAU); g.fill(); }
}
function drawFeatures(hm, fc) {
  const g = bx; g.save(); g.setTransform(hm);
  eye(g, { o: [-38, -6], i: [1, -4], top: [-18, -22], bot: [-17, 9] }, fc, false);
  eye(g, { o: [45, -14], i: [17, -7], top: [30, -28], bot: [30, 3] }, fc, true);
  g.fillStyle = C.lid;
  brow(g, [[-34, -31], [-16, -42], [-1, -43]], 6.2, -0.15 * fc.smile);
  brow(g, [[16, -46], [31, -50], [46, -40]], 5.4, -0.15 * fc.smile);
  mouth(g, fc);
  g.restore();
}
function brow(g, p, w, raise) {
  const dy = raise * 6;
  g.beginPath(); g.moveTo(p[0][0], p[0][1] + w * 0.35 + dy);
  g.bezierCurveTo(p[0][0] + 6, p[1][1] - 2 + dy, p[1][0], p[1][1] - 1 + dy, p[2][0], p[2][1] + dy);
  g.quadraticCurveTo(p[2][0] + 1.5, p[2][1] + w * 0.6 + dy, p[2][0] - 2, p[2][1] + w + dy);
  g.bezierCurveTo(p[1][0], p[1][1] + w * 1.1 + dy, p[0][0] + 6, p[1][1] + w * 1.2 + dy, p[0][0], p[0][1] + w * 0.35 + dy);
  g.closePath(); g.fill();
}
function eye(g, E, fc, far) {
  const open = fc.open * (1 - fc.squint * 0.5);
  const [ox, oy] = E.o, [ix, iy] = E.i, [tx, ty] = E.top, [bx_, by] = E.bot;
  const topY = lerp(by - 3, ty, open), botY = by - fc.squint * 5, cxr = (ox + ix) / 2;
  if (open < 0.1) { g.strokeStyle = C.lid; g.lineWidth = 3; g.lineCap = 'round'; g.beginPath(); g.moveTo(ox, oy); g.quadraticCurveTo(tx, by - 4, ix, iy); g.stroke(); return; }
  const P = new Path2D();
  P.moveTo(ox, oy); P.bezierCurveTo(ox + (tx - ox) * 0.25, topY, tx + (ix - tx) * 0.55, topY, ix, iy);
  P.bezierCurveTo(ix - (ix - bx_) * 0.2, botY, ox + (bx_ - ox) * 0.4, botY + 1, ox, oy); P.closePath();
  g.save(); g.fillStyle = C.eyeW; g.fill(P); g.clip(P);
  let gr = g.createLinearGradient(0, topY, 0, botY); gr.addColorStop(0, 'rgba(200,120,90,0.45)'); gr.addColorStop(0.35, 'rgba(200,120,90,0)'); g.fillStyle = gr; g.fill(P);
  const icx = cxr + (far ? 3 : 6) + fc.lookX * (far ? 0.6 : 1), icy = (topY + botY) / 2 + 1 + fc.lookY;
  const irx = far ? 10 : 12.6, iry = far ? 12.6 : 14.2;
  gr = g.createRadialGradient(icx - 2, icy + 3, 1, icx, icy, iry); gr.addColorStop(0, '#5a2a18'); gr.addColorStop(0.55, '#2a120b'); gr.addColorStop(1, C.iris);
  g.fillStyle = gr; g.beginPath(); g.ellipse(icx, icy, irx, iry, 0, 0, TAU); g.fill();
  g.fillStyle = '#0a0403'; g.beginPath(); g.ellipse(icx + 0.4, icy + 0.6, irx * 0.5, iry * 0.52, 0, 0, TAU); g.fill();
  gr = g.createLinearGradient(0, topY, 0, topY + 9); gr.addColorStop(0, 'rgba(10,3,2,0.55)'); gr.addColorStop(1, 'rgba(10,3,2,0)'); g.fillStyle = gr; g.fill(P);
  g.fillStyle = 'rgba(255,250,242,0.95)'; g.beginPath(); g.ellipse(icx - irx * 0.38, icy - iry * 0.42, far ? 2.6 : 3.8, far ? 3 : 4.4, -0.3, 0, TAU); g.fill();
  g.beginPath(); g.arc(icx + irx * 0.42, icy + iry * 0.1, far ? 1 : 1.6, 0, TAU); g.fill();
  g.fillStyle = 'rgba(214,120,70,0.5)'; g.beginPath(); g.ellipse(icx + 1, icy + iry * 0.66, irx * 0.5, iry * 0.18, 0, 0, TAU); g.fill();
  g.restore();
  const s = far ? 1 : -1, wing = far ? 4.5 : 6.5;
  g.fillStyle = C.lid; g.beginPath();
  g.moveTo(ox + s * wing, oy - wing * 0.7); g.lineTo(ox, oy + 0.5);
  g.bezierCurveTo(ox + (tx - ox) * 0.25, topY, tx + (ix - tx) * 0.55, topY, ix, iy);
  g.bezierCurveTo(tx + (ix - tx) * 0.55, topY - 3.2, ox + (tx - ox) * 0.25, topY - 4.6, ox - s * 1.5, oy - 3.4);
  g.closePath(); g.fill();
  g.strokeStyle = C.lid; g.lineCap = 'round'; g.lineWidth = 1.5;
  for (let i = 0; i < (far ? 1 : 2); i++) { const bx2 = lerp(ox, tx, 0.18 + i * 0.16), by2 = lerp(oy, topY, 0.55 + i * 0.2) - 3; g.beginPath(); g.moveTo(bx2, by2); g.quadraticCurveTo(bx2 + s * 2, by2 - 4, bx2 + s * 4.5, by2 - 5.5); g.stroke(); }
  g.strokeStyle = 'rgba(110,40,18,0.7)'; g.lineWidth = 1.1; g.beginPath(); g.moveTo(ox + (ix - ox) * 0.08, oy + 2); g.quadraticCurveTo(bx_, botY + 1.5, ox + (ix - ox) * 0.7, botY); g.stroke();
  g.strokeStyle = 'rgba(140,56,26,0.45)'; g.lineWidth = 1.1; g.beginPath(); g.moveTo(ox + (ix - ox) * 0.15, topY - 7); g.quadraticCurveTo(tx, topY - 10, ix - (ix - ox) * 0.12, topY - 5); g.stroke();
}
function mouth(g, fc) {
  const s = fc.smile, L = [-11 - s * 2, 25 - s * 2], R = [27 + s * 1.5, 25 - s * 3], dip = 31 + s * 4;
  g.fillStyle = rgba([212, 100, 74], 0.75); g.beginPath(); g.moveTo(L[0] + 6, dip - 2.5); g.quadraticCurveTo(8, dip + 7 + s * 1.5, R[0] - 5, dip - 3.2); g.quadraticCurveTo(8, dip + 1, L[0] + 6, dip - 2.5); g.fill();
  if (s > 0.55) {
    const k = (s - 0.55) / 0.45;
    g.fillStyle = '#4a1209'; g.beginPath(); g.moveTo(L[0] + 3, L[1] + 1.5); g.quadraticCurveTo(8, dip + 1 + 5 * k, R[0] - 2, R[1] + 1.5); g.quadraticCurveTo(8, dip - 1, L[0] + 3, L[1] + 1.5); g.fill();
    g.fillStyle = '#fff5ea'; g.beginPath(); g.moveTo(L[0] + 5, L[1] + 2.2); g.quadraticCurveTo(8, dip - 0.5 + 2.5 * k, R[0] - 4, R[1] + 2.2); g.quadraticCurveTo(8, dip - 1.5, L[0] + 5, L[1] + 2.2); g.fill();
  }
  g.strokeStyle = '#3c1007'; g.lineWidth = 2.2; g.lineCap = 'round';
  g.beginPath(); g.moveTo(L[0], L[1]); g.quadraticCurveTo(8, dip, R[0], R[1]); g.stroke();
  g.lineWidth = 1.4; g.beginPath(); g.moveTo(L[0] - 1.5, L[1] - 2.5); g.quadraticCurveTo(L[0] - 0.5, L[1] + 0.5, L[0] + 1.5, L[1] + 1.2); g.stroke();
  g.strokeStyle = 'rgba(150,60,30,0.22)'; g.lineWidth = 1.2; g.beginPath(); g.moveTo(-3, dip + 9); g.quadraticCurveTo(8, dip + 11, 18, dip + 8.5); g.stroke();
}
function drawBun(hm, sw) {
  const bm = hm.multiply(mat(-90, -50, sw * 0.4)).translateSelf(90, 50);
  const P = new Path2D(), r = rng(55);
  for (const [cx, cy, rr] of HEAD.bun) {
    const k = [1, 2, 3, 5].map(n => ({ n, a: r() * 0.24 / n, p: r() * TAU })), pts = [];
    for (let i = 0; i < 22; i++) { const a = TAU * i / 22; let q = rr; for (const h of k) q += rr * h.a * Math.sin(h.n * a + h.p); pts.push([cx + q * Math.cos(a), cy + q * Math.sin(a) * 0.92]); }
    cr(P, pts, true);
  }
  part(T(P, bm), [C.hair, C.hairLit, C.hairSh, C.hairGlow], { shade: 9, rim: 2.8, lw: 1.1, hl: 9, line: '#24100a', lineLit: '#d98a52', detail: g => {
    g.setTransform(bm); g.lineCap = 'round';
    const q = rng(91);
    for (const [cx, cy, rr] of HEAD.bun) {
      for (let i = 0; i < 9; i++) {
        const k = 0.3 + q() * 0.65, a0 = q() * TAU, span = 1.4 + q() * 2.2, dark = i % 2 === 0;
        g.strokeStyle = dark ? 'rgba(14,5,3,0.45)' : 'rgba(150,92,60,0.45)'; g.lineWidth = dark ? 1.1 : 0.9;
        g.beginPath(); g.ellipse(cx + (q() - 0.5) * 4, cy + (q() - 0.5) * 4, rr * k, rr * k * 0.85, q(), a0, a0 + span); g.stroke();
      }
      g.save(); g.filter = `blur(${2.2 * ZS}px)`; g.strokeStyle = 'rgba(160,98,64,0.5)'; g.lineWidth = rr * 0.22; g.beginPath(); g.arc(cx - 2, cy - 2, rr * 0.66, -1.9, -0.4); g.stroke(); g.restore();
    }
  } });
  // looping clumps wrapped around the bun
  const g = bx; g.save(); g.setTransform(bm);
  const loops = [[-92, -50, 24, -2.6, -0.4, 6], [-92, -50, 15, 0.6, 2.9, 5], [-74, -74, 15, -3.0, -0.6, 4.5], [-110, -28, 14, 1.8, 4.4, 4], [-104, -62, 13, -2.2, 0.2, 4], [-92, -50, 28, 2.2, 3.6, 3]];
  for (const [cx, cy, r0, a0, a1, w] of loops) {
    const am = (a0 + a1) / 2, k = 1 / Math.cos((a1 - a0) / 2), p0 = [cx + Math.cos(a0) * r0, cy + Math.sin(a0) * r0], pc = [cx + Math.cos(am) * r0 * k, cy + Math.sin(am) * r0 * k], p1 = [cx + Math.cos(a1) * r0, cy + Math.sin(a1) * r0];
    taper(g, ...p0, ...pc, ...p1, 0.5, w, 'rgba(104,58,38,0.6)', 0.6);
    taper(g, p0[0] + 1, p0[1] + 1.5, pc[0] + 1.5, pc[1] + 2, p1[0] + 1, p1[1] + 1.5, 0.3, 1.1, 'rgba(10,3,2,0.6)');
    taper(g, p0[0] - 0.5, p0[1] - 1, pc[0] - 1, pc[1] - 1.5, p1[0], p1[1] - 1, 0.2, 0.8, 'rgba(236,178,128,0.55)');
  }
  g.restore();
}
function drawShell(hm) {
  part(T(shape(HEAD.shell), hm), ['#2c150f', C.hairLit, C.hairSh, C.hairGlow], { shade: 7, rim: 2.4, lw: 0.7, hl: 8, hlA: 0.28, line: '#22100a', lineLit: '#d98a52', detail: g => {
    g.setTransform(hm); g.lineCap = 'round';
    let gr = g.createRadialGradient(-6, -64, 0, -6, -64, 60); gr.addColorStop(0, 'rgba(112,62,40,0.5)'); gr.addColorStop(1, 'rgba(112,62,40,0)'); g.fillStyle = gr; g.fillRect(-90, -130, 170, 130);
    gr = g.createLinearGradient(0, -40, -30, -60); gr.addColorStop(0, 'rgba(10,3,2,0.5)'); gr.addColorStop(1, 'rgba(10,3,2,0)'); g.fillStyle = gr; g.fillRect(-60, -70, 120, 50);   // darker at the hairline
    const bunC = [-92, -52], q = rng(33), sl = HEAD.shell;
    for (let i = 0; i < 46; i++) {   // strand clumps sweeping back to the bun
      const u = q() * 8.6, j = Math.floor(u), f = u - j, a = sl[j], b = sl[j + 1];
      const x = lerp(a[0], b[0], f), y = lerp(a[1], b[1], f) - 1;
      const ex = bunC[0] + 10 + (q() - 0.5) * 24, ey = bunC[1] + (q() - 0.5) * 30;
      const cx = (x + ex) / 2 + 14 + q() * 10, cy = Math.min(y, ey) - 16 - q() * 16;
      const kind = q();
      if (kind < 0.35) taper(g, x, y, cx, cy, ex, ey, 0.8, 5 + q() * 3, 'rgba(104,58,38,0.62)', 0.7);
      else if (kind < 0.75) taper(g, x, y, cx, cy, ex, ey, 0.5, 1.4 + q(), 'rgba(10,3,2,0.65)');
      else taper(g, x, y, cx, cy, ex, ey, 0.3, 0.9, 'rgba(214,150,104,0.45)');
    }
    g.save(); g.filter = `blur(${3.2 * ZS}px)`; g.strokeStyle = 'rgba(184,116,76,0.55)'; g.lineWidth = 9; g.beginPath(); g.moveTo(-74, -42); g.bezierCurveTo(-50, -70, 4, -78, 40, -58); g.stroke(); g.restore();
    for (let i = 0; i < 7; i++) { const o = i * 2.6 - 8; taper(g, -66 + o, -46 - o * 0.3 + (i % 3) * 3, 0, -84 - o * 0.4 + (i % 2) * 4, 36 + o, -60 + o * 0.5, 0.2, 0.8, `rgba(238,182,134,${0.2 + (i % 3) * 0.12})`); }
  } });
}
function edgeStrands(hm, pz, t) {
  const g = bx; g.save(); g.setTransform(hm); const q = rng(404), sl = HEAD.shell;
  for (let i = 0; i < 30; i++) {
    const u = 16 + q() * 7.9, j = Math.floor(u) % sl.length, f = u - Math.floor(u), a = sl[j], b = sl[(j + 1) % sl.length];
    const x = lerp(a[0], b[0], f), y = lerp(a[1], b[1], f);
    const tx = b[0] - a[0], ty = b[1] - a[1], l = Math.hypot(tx, ty) || 1, nx = ty / l, ny = -tx / l;   // outward normal
    const out = 0.5 + q() * 2.5, along = -(14 + q() * 18), wob = 0.15 * Math.sin(4 * Math.PI * pz.p + i);
    const x1 = x + nx * out + tx / l * along, y1 = y + ny * out + ty / l * along;
    const cx = (x + x1) / 2 + nx * (2 + q() * 3) + wob * 4, cy = (y + y1) / 2 + ny * (2 + q() * 3);
    taper(g, x - nx * 2, y - ny * 2, cx, cy, x1, y1, 1.0, 0.15, q() < 0.6 ? 'rgba(42,19,12,0.85)' : 'rgba(226,160,112,0.6)');
  }
  g.restore();
}
function leaf(x0, y0, cx, cy, x1, y1, wm) {   // a lock: thin at the root, full in the middle, thin at the tip
  const N = 18, L = [], Rr = [];
  for (let i = 0; i <= N; i++) {
    const u = i / N, a = (1 - u) * (1 - u), b = 2 * (1 - u) * u, c = u * u;
    const x = a * x0 + b * cx + c * x1, y = a * y0 + b * cy + c * y1;
    const tx = 2 * (1 - u) * (cx - x0) + 2 * u * (x1 - cx), ty = 2 * (1 - u) * (cy - y0) + 2 * u * (y1 - cy), l = Math.hypot(tx, ty) || 1;
    const w = (wm * Math.pow(Math.sin(Math.PI * clamp(u * 0.92 + 0.06, 0, 1)), 0.7) + 1) / 2;
    L.push([x - ty / l * w, y + tx / l * w]); Rr.push([x + ty / l * w, y - tx / l * w]);
  }
  const P = new Path2D(); addPoly(P, L.concat(Rr.reverse())); return P;
}
function taper(g, x0, y0, cx, cy, x1, y1, w0, w1, color, blur = 0) {
  g.save(); if (blur) g.filter = `blur(${blur * ZS}px)`; g.strokeStyle = color; g.lineCap = 'round';
  let px = x0, py = y0;
  for (let i = 1; i <= 12; i++) { const u = i / 12, a = (1 - u) * (1 - u), b = 2 * (1 - u) * u, c = u * u, x = a * x0 + b * cx + c * x1, y = a * y0 + b * cy + c * y1; g.lineWidth = lerp(w0, w1, u); g.beginPath(); g.moveTo(px, py); g.lineTo(x, y); g.stroke(); px = x; py = y; }
  g.restore();
}
function wisps(hm, list) {   // tapered wavy strands, no outline
  const g = bx; g.save(); g.setTransform(hm); g.lineCap = 'round';
  for (const [x0, y0, c1x, c1y, c2x, c2y, x1, y1, w] of list) {
    const pt = u => { const a = (1 - u) ** 3, b = 3 * (1 - u) ** 2 * u, c = 3 * (1 - u) * u * u, d = u ** 3; return [a * x0 + b * c1x + c * c2x + d * x1, a * y0 + b * c1y + c * c2y + d * y1]; };
    let prev = pt(0);
    for (let i = 1; i <= 16; i++) { const u = i / 16, q = pt(u); g.strokeStyle = 'rgba(40,18,11,0.9)'; g.lineWidth = w * (1 - u * 0.85); g.beginPath(); g.moveTo(prev[0], prev[1]); g.lineTo(q[0], q[1]); g.stroke(); prev = q; }
    prev = pt(0.15);
    for (let i = 4; i <= 14; i++) { const u = i / 16, q = pt(u); g.strokeStyle = 'rgba(214,146,98,0.45)'; g.lineWidth = w * 0.3 * (1 - u * 0.7); g.beginPath(); g.moveTo(prev[0] + 0.4, prev[1]); g.lineTo(q[0] + 0.4, q[1]); g.stroke(); prev = q; }
  }
  g.restore();
}
function hairRibbons(hm, list) {
  for (const [x0, y0, cx, cy, x1, y1, w0, w1] of list)
    part(T(ribbon(x0, y0, cx, cy, x1, y1, w0, w1), hm), [C.hair, C.hairSheen, C.hairSh, C.hairGlow], { shade: 1.2, rim: 0.7, lw: 0.35, hl: 1.5, line: '#1a0905', noLitLine: true, soft: 0.6 });
}
function flyaways(hm, pz, t) {
  const g = bx; g.save(); g.setTransform(hm); g.lineCap = 'round';
  for (const [x0, y0, a, len, w, ph] of FLY) {
    const a2 = a + 0.18 * Math.sin(4 * Math.PI * pz.p + ph) + 0.08 * Math.sin(TAU * t / 1.7 + ph);
    const x1 = x0 + Math.cos(a2) * len, y1 = y0 + Math.sin(a2) * len;
    const cx = (x0 + x1) / 2 + Math.cos(a2 + 1.4) * len * 0.6, cy = (y0 + y1) / 2 + Math.sin(a2 + 1.4) * len * 0.6;
    g.strokeStyle = 'rgba(46,20,13,0.7)'; g.lineWidth = w * 0.7; g.beginPath(); g.moveTo(x0, y0); g.quadraticCurveTo(cx, cy, x1, y1); g.stroke();
    g.strokeStyle = 'rgba(232,170,118,0.5)'; g.lineWidth = w * 0.35; g.beginPath(); g.moveTo(lerp(x0, x1, 0.4), lerp(y0, y1, 0.4)); g.quadraticCurveTo(cx, cy, x1, y1); g.stroke();
  }
  g.restore();
}

function drawShadow(pz) {
  bx.save(); bx.setTransform(CM.a, CM.b, CM.c, CM.d, CM.e, CM.f); bx.filter = `blur(${6 * ZS}px)`;
  bx.fillStyle = 'rgba(110,62,40,0.32)'; bx.beginPath(); bx.ellipse(-80, 5, 136, 10, 0, 0, TAU); bx.fill();
  bx.fillStyle = 'rgba(90,48,30,0.35)';
  for (const ph of [pz.p, pz.p + 0.5]) { const f = footAt(ph), k = clamp(1 - f.lift / 44, 0.2, 1); bx.beginPath(); bx.ellipse(f.x + 12, 2, 30 * k, 5 * k, 0, 0, TAU); bx.fill(); }
  bx.restore();
}
function drawCharacter(t, cam) {
  const pz = pose(t);
  G = layerMatrix(cam, 1); ZS = G.a * K;
  CM = G.multiply(new DOMMatrix([K, 0, 0, K, CHAR_X, GROUND]));
  drawShadow(pz);
  drawArm(pz, false);
  drawLeg(pz, pz.p + 0.5, true);
  drawLeg(pz, pz.p, false);
  drawTorso(pz);
  drawNeck(pz);
  drawHead(pz, t);
  drawArm(pz, true);
}
function grade(cam) {
  const m = layerMatrix(cam, 0.03);
  bx.save(); bx.setTransform(m.a, m.b, m.c, m.d, m.e, m.f); bx.globalCompositeOperation = 'lighter';
  bx.globalAlpha = 0.5; bx.drawImage(BG.glow, 750, -220, 520, 520);
  bx.globalAlpha = 0.22; bx.drawImage(BG.glow, 780, 110, 80, 80); bx.drawImage(BG.glow, 678, 208, 44, 44);
  bx.restore();
  bx.save(); bx.globalCompositeOperation = 'soft-light';
  const g = bx.createLinearGradient(BW, 0, 0, BH); g.addColorStop(0, 'rgba(255,190,110,0.5)'); g.addColorStop(1, 'rgba(120,60,90,0.22)');
  bx.fillStyle = g; bx.fillRect(0, 0, BW, BH); bx.restore();
  const v = bx.createRadialGradient(BW * 0.5, BH * 0.5, BH * 0.45, BW * 0.5, BH * 0.55, BW * 0.75);
  v.addColorStop(0, 'rgba(30,12,8,0)'); v.addColorStop(1, 'rgba(30,12,8,0.3)'); bx.fillStyle = v; bx.fillRect(0, 0, BW, BH);
}
function drawTitle() {
  ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic'; ctx.font = '800 50px "Montserrat"';
  const lines = [[['Keep Your Blessings ', '#ffffff'], ['Quiet', '#f4ee2c']], [["Until They're ", '#ffffff'], ['Permanent', '#f4ee2c']]];
  [548, 611].forEach((y, i) => {
    const ln = lines[i]; let x = (W - ln.reduce((s, [t]) => s + ctx.measureText(t).width, 0)) / 2;
    for (const [txt, col] of ln) { ctx.fillStyle = col; ctx.fillText(txt, x, y); x += ctx.measureText(txt).width; }
  });
}
function renderAt(t, camOverride) {
  const f = Math.min(DUR * FPS - 1, Math.floor(t * FPS + 1e-6)); t = f / FPS;
  const cam = camOverride || window.CAM_OVR || camAt(t);
  bx.setTransform(1, 0, 0, 1, 0, 0); bx.globalCompositeOperation = 'source-over'; bx.filter = 'none'; bx.globalAlpha = 1;
  drawBackground(t, cam);
  drawCharacter(t, cam);
  bx.setTransform(1, 0, 0, 1, 0, 0);
  grade(cam);
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  drawTitle(); ctx.drawImage(band, 0, BY);
  return cv;
}
window.SCENE = { W, H, FPS, DUR, renderAt, canvas: cv, band };
window.readyP = (async () => { try { await document.fonts.load('800 50px "Montserrat"'); } catch (e) {} buildBackground(); })();
})();
