// Forgotten Little Joys of Life, episode 2: "POV you were your dads tv remote".
// Built to videos/002-forgotten-little-joys-ep1/THEME.md. Every frame is a pure function of t.
(function () {
'use strict';
const W = 1080, H = 1920, FPS = 24, DUR = 59;
const TAU = Math.PI * 2;
// shot boundaries: the episode-1 timing grid (THEME.md section 4)
const CUTS = [0, 2.375, 4.667, 6.292, 7.833, 9.375, 11.667, 16.458, 18.708, 21.25, 23.833, 25.875, 28.083, 32.917, 37.542, 42.125, 44.667, 49.333, 56.417, 59];
const C = {
  ink: '#2a2018', paper: '#ECE5D6', glow: [233, 190, 128],
  skinK: '#B07052', skinKsh: '#8C5039', skinD: '#A2644A', skinDsh: '#7F4835',
  blush: [214, 72, 52], hair: '#2E2A29', red: '#CB4A3C', redSh: '#A0362B', shorts: '#2C2B30',
  shirt: '#86AED0', shirtSh: '#5F88AE', shirtLine: 'rgba(240,246,250,0.75)', shirtLine2: 'rgba(52,86,120,0.45)', pants: '#6E6156',
  wood: '#8E5B3A', woodSh: '#6C4128', woodLt: '#B07A50', grey: '#5E5A55', steel: '#A8A39A', steelSh: '#77726A',
  wall: '#E6CC9E', wallSh: '#D2AF7E', sofa: '#8E3B34', sofaSh: '#6E2A25', lace: '#F6F1E6',
  kulfi: '#F2D7A0', kulfiTop: '#EDB86A', pista: '#8AA048', stick: '#D9B27C', curtain: '#C99A4E', curtainSh: '#A27634',
  sky1: '#F0B07A', sky2: '#F6D5A8', sky3: '#E9C8B8', bubble: '#FFFFFF',
};
function rng(seed) { let a = seed >>> 0; return () => { a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const lerp = (a, b, u) => a + (b - a) * u;
const eo = u => 1 - Math.pow(1 - clamp(u, 0, 1), 3);
const ei = u => Math.pow(clamp(u, 0, 1), 3);
const eio = u => 0.5 - 0.5 * Math.cos(Math.PI * clamp(u, 0, 1));
const back = u => { u = clamp(u, 0, 1); const s = 1.7; return 1 + (s + 1) * Math.pow(u - 1, 3) + s * Math.pow(u - 1, 2); };
const twos = t => Math.floor(t * 12 + 1e-6) / 12;               // keyframed moves update on twos
const seg = (t, a, b) => clamp((t - a) / (b - a), 0, 1);
const rgba = (c, a) => `rgba(${c[0]},${c[1]},${c[2]},${a})`;

// ---------- canvases ----------
const mk = (w = W, h = H) => { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; };
const cv = mk(), ctx = cv.getContext('2d');
const SC = mk(), sx = SC.getContext('2d');      // the shot illustration
const SC2 = mk(), sx2 = SC2.getContext('2d');   // previous shot, for dissolves
const LY = mk(), ly = LY.getContext('2d');      // a layer for focus pulls
const CP = mk(), cp = CP.getContext('2d');

// ---------- drawing helpers ----------
function shape(pts, closed = true) {
  const P = new Path2D(), n = pts.length, at = i => closed ? pts[(i + n) % n] : pts[clamp(i, 0, n - 1)];
  P.moveTo(pts[0][0], pts[0][1]);
  for (let i = 0; i < (closed ? n : n - 1); i++) {
    const p0 = at(i - 1), p1 = at(i), p2 = at(i + 1), p3 = at(i + 2);
    P.bezierCurveTo(p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6, p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6, p2[0], p2[1]);
  }
  if (closed) P.closePath();
  return P;
}
function T(pts, x, y, s, r = 0) { const c = Math.cos(r), n = Math.sin(r); return pts.map(([a, b]) => [x + (a * c - b * n) * s, y + (a * n + b * c) * s]); }
// flat fill + soft airbrush shading toward the lower left + ink outline
function ink(g, P, fill, bb, o = {}) {
  g.fillStyle = fill; g.fill(P);
  if (bb && o.shade !== 0) {
    g.save(); g.clip(P);
    const gr = g.createLinearGradient(bb[2], bb[1], bb[0], bb[3]);
    gr.addColorStop(0, 'rgba(255,240,215,' + (o.hi ?? 0.12) + ')'); gr.addColorStop(0.5, 'rgba(0,0,0,0)'); gr.addColorStop(1, o.sh || 'rgba(70,25,15,0.28)');
    g.fillStyle = gr; g.fillRect(bb[0], bb[1], bb[2] - bb[0], bb[3] - bb[1]); g.restore();
  }
  if (o.lw !== 0) { g.lineWidth = o.lw || 4.6; g.strokeStyle = o.ink || C.ink; g.lineJoin = 'round'; g.lineCap = 'round'; g.stroke(P); }
}
function limb(g, pts, w, col, lw = 4.6) {
  const P = shape(pts, false);
  g.lineCap = 'round'; g.lineJoin = 'round';
  g.strokeStyle = C.ink; g.lineWidth = w + lw * 2; g.stroke(P);
  g.strokeStyle = col; g.lineWidth = w; g.stroke(P);
}
function blush(g, x, y, r, a = 0.55, sy = 0.75) {
  g.save(); g.translate(x, y); g.scale(1, sy);
  const gr = g.createRadialGradient(0, 0, 0, 0, 0, r); gr.addColorStop(0, rgba(C.blush, a)); gr.addColorStop(1, rgba(C.blush, 0));
  g.fillStyle = gr; g.fillRect(-r, -r, 2 * r, 2 * r); g.restore();
}
function glow(g, x, y, r, a = 0.9, col = C.glow) {
  const gr = g.createRadialGradient(x, y, 0, x, y, r); gr.addColorStop(0, rgba(col, a)); gr.addColorStop(0.55, rgba(col, a * 0.45)); gr.addColorStop(1, rgba(col, 0));
  g.fillStyle = gr; g.fillRect(x - r, y - r, 2 * r, 2 * r);
}
function sparkle(g, x, y, r, a = 1) {
  if (a <= 0 || r <= 0) return;
  g.save(); g.globalAlpha = a; g.translate(x, y);
  const gr = g.createRadialGradient(0, 0, 0, 0, 0, r * 1.6); gr.addColorStop(0, 'rgba(255,250,230,0.8)'); gr.addColorStop(1, 'rgba(255,250,230,0)');
  g.fillStyle = gr; g.fillRect(-r * 1.6, -r * 1.6, r * 3.2, r * 3.2);
  g.fillStyle = '#fffdf5'; g.beginPath();
  for (let i = 0; i < 8; i++) { const rr = i % 2 ? r * 0.22 : r, an = i * Math.PI / 4 - Math.PI / 2; g[i ? 'lineTo' : 'moveTo'](Math.cos(an) * rr, Math.sin(an) * rr); }
  g.closePath(); g.fill(); g.restore();
}
function ticks(g, x, y, r, n, a0, a1, a = 1) {
  g.save(); g.globalAlpha = a; g.strokeStyle = C.ink; g.lineWidth = 5; g.lineCap = 'round';
  for (let i = 0; i < n; i++) { const an = lerp(a0, a1, n > 1 ? i / (n - 1) : 0.5); g.beginPath(); g.moveTo(x + Math.cos(an) * r, y + Math.sin(an) * r); g.lineTo(x + Math.cos(an) * (r + 34), y + Math.sin(an) * (r + 34)); g.stroke(); }
  g.restore();
}
function bubble(g, text, x, y, u, from = 1) {      // u: slide-in progress 0..1, from: +1 right edge, -1 left edge
  if (u <= 0) return;
  g.save(); g.font = '36px "Patrick Hand"'; const w = g.measureText(text).width + 46, h = 62;
  const dx = (1 - eo(u)) * from * 700;
  const bx = x - w / 2 + dx, by = y - h / 2;
  g.beginPath(); g.roundRect(bx, by, w, h, 31); g.fillStyle = C.bubble; g.fill(); g.lineWidth = 3; g.strokeStyle = C.ink; g.stroke();
  g.beginPath(); g.moveTo(x + dx + w * 0.22, by + h - 2); g.lineTo(x + dx + w * 0.26, by + h + 26); g.stroke();
  g.fillStyle = C.ink; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(text, x + dx, y + 2); g.restore();
}

// ---------- textures ----------
let PAPER, MASK, NOISE = [];
function buildTextures() {
  const r = rng(11);
  PAPER = mk(); const p = PAPER.getContext('2d'), im = p.createImageData(W, H), d = im.data;
  const rowOff = new Float32Array(H); for (let y = 0; y < H; y++) rowOff[y] = (r() - 0.5) * 7 + (y % 3 === 0 ? -2.5 : 0);
  const blot = []; for (let i = 0; i < 40; i++) blot.push([r() * W, r() * H, 80 + r() * 220, (r() - 0.5) * 6]);
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    let v = rowOff[y] + (r() - 0.5) * 5;
    const o = (y * W + x) * 4; d[o] = 236 + v; d[o + 1] = 229 + v; d[o + 2] = 214 + v; d[o + 3] = 255;
  }
  p.putImageData(im, 0, 0);
  for (const [x, y, rr, v] of blot) { const gr = p.createRadialGradient(x, y, 0, x, y, rr); gr.addColorStop(0, v > 0 ? 'rgba(255,250,240,0.25)' : 'rgba(190,170,140,0.12)'); gr.addColorStop(1, 'rgba(0,0,0,0)'); p.fillStyle = gr; p.fillRect(x - rr, y - rr, 2 * rr, 2 * rr); }
  // irregular soft vignette mask, built small and scaled up smooth
  const m = mk(216, 384), mg = m.getContext('2d'), mi = mg.createImageData(216, 384), md = mi.data;
  const k = [1, 2, 3, 5].map(n => ({ n, a: r() * 0.05 / Math.sqrt(n), p: r() * TAU }));
  for (let y = 0; y < 384; y++) for (let x = 0; x < 216; x++) {
    const X = (x + 0.5) * 5, Y = (y + 0.5) * 5, ang = Math.atan2(Y - 1090, X - 540);
    let wob = 1; for (const h of k) wob += h.a * Math.sin(h.n * ang + h.p);
    const dd = Math.sqrt(Math.pow((X - 540) / 600, 2) + Math.pow((Y - 1090) / 860, 2)) / wob;
    const a = 1 - clamp((dd - 0.74) / 0.3, 0, 1); const o = (y * 216 + x) * 4; md[o] = md[o + 1] = md[o + 2] = 0; md[o + 3] = 255 * a * a * (3 - 2 * a);
  }
  mg.putImageData(mi, 0, 0); MASK = mk(); const M = MASK.getContext('2d'); M.imageSmoothingQuality = 'high'; M.drawImage(m, 0, 0, W, H);
  // TV static frames
  for (let f = 0; f < 12; f++) {
    const c = mk(120, 96), g = c.getContext('2d'), id = g.createImageData(120, 96), q = rng(500 + f);
    for (let i = 0; i < 120 * 96; i++) { const v = 60 + q() * 190; id.data[i * 4] = v; id.data[i * 4 + 1] = v; id.data[i * 4 + 2] = v + 6; id.data[i * 4 + 3] = 255; }
    g.putImageData(id, 0, 0); NOISE.push(c);
  }
}

// ---------- characters ----------
const BLINKS = []; { const r = rng(3); let t = 1.1; while (t < DUR) { BLINKS.push(t); t += 2.1 + r() * 1.8; } }
function blinkAt(t) { for (const b of BLINKS) if (t >= b && t < b + 0.125) return true; return false; }

function eyes(g, R, f, ex, ey, rx, ry, glasses) {
  for (const s of [-1, 1]) {
    const x = s * ex;
    if (f.eyes === 'closed' || f.eyes === 'happy' || f.blink) {
      g.strokeStyle = C.ink; g.lineWidth = 5; g.lineCap = 'round'; g.beginPath();
      if (f.eyes === 'happy') { g.arc(x, ey + ry * 0.25, rx * 0.62, Math.PI * 1.15, Math.PI * 1.85); }
      else { g.arc(x, ey - ry * 0.15, rx * 0.62, Math.PI * 0.15, Math.PI * 0.85); }
      g.stroke(); continue;
    }
    const P = new Path2D(); P.ellipse(x, ey, rx, ry, 0, 0, TAU);
    ink(g, P, '#FFFDF8', null, { lw: 4.4 });
    const pr = (f.eyes === 'wide' ? 0.17 : 0.24) * rx;
    const px = x + (f.lx || 0) * rx * 0.45, py = ey + (f.ly || 0) * ry * 0.45;
    g.fillStyle = '#171110'; g.beginPath(); g.arc(px, py, pr, 0, TAU); g.fill();
    g.fillStyle = '#fff'; g.beginPath(); g.arc(px - pr * 0.35, py - pr * 0.4, pr * 0.32, 0, TAU); g.fill();
    if (glasses) { g.lineWidth = 6; g.strokeStyle = '#3a2a22'; g.beginPath(); g.arc(x, ey, rx * 1.18, 0, TAU); g.stroke(); g.strokeStyle = 'rgba(255,255,255,0.5)'; g.lineWidth = 3; g.beginPath(); g.arc(x, ey, rx * 0.98, -2.4, -1.7); g.stroke(); }
  }
  if (glasses) { g.lineWidth = 6; g.strokeStyle = '#3a2a22'; g.beginPath(); g.moveTo(-ex + rx * 1.18, ey - 4); g.quadraticCurveTo(0, ey - 14, ex - rx * 1.18, ey - 4); g.stroke(); }
}
function mouth(g, R, type, y, w = 1) {
  g.strokeStyle = C.ink; g.lineWidth = 5; g.lineCap = 'round';
  const m = R * 0.16 * w;
  if (type === 'smile' || type === 'flat') { g.beginPath(); g.moveTo(-m, y); g.quadraticCurveTo(0, y + (type === 'smile' ? m * 0.8 : 4), m, y); g.stroke(); return; }
  let P = new Path2D();
  if (type === 'o') P.ellipse(0, y + 6, m * 0.42, m * 0.55, 0, 0, TAU);
  else if (type === 'shout') P.ellipse(0, y + 10, m * 0.75, m * 0.95, 0, 0, TAU);
  else if (type === 'grin' || type === 'open') { P.moveTo(-m * 1.25, y - 4); P.quadraticCurveTo(0, y + m * (type === 'grin' ? 1.9 : 1.4), m * 1.25, y - 4); P.closePath(); }
  else if (type === 'bite') { g.beginPath(); g.moveTo(-m * 0.7, y + 4); g.quadraticCurveTo(0, y + m * 0.7, m * 0.7, y + 4); g.stroke(); return; }
  g.fillStyle = '#5a1c14'; g.fill(P);
  g.save(); g.clip(P); g.fillStyle = '#d0634f'; g.beginPath(); g.ellipse(0, y + m * 1.3, m * 0.8, m * 0.6, 0, 0, TAU); g.fill();
  if (type === 'grin') { g.fillStyle = '#fff'; g.fillRect(-m * 1.3, y - 10, m * 2.6, m * 0.45); } g.restore();
  g.lineWidth = 4.6; g.stroke(P);
}
// the Kid's head (front view). R = head radius in px
function kidHead(g, x, y, R, f, rot = 0) {
  g.save(); g.translate(x, y); g.rotate(rot);
  const bb = [-R * 1.1, -R, R * 1.1, R];
  for (const s of [-1, 1]) { const P = new Path2D(); P.ellipse(s * R * 0.97, R * 0.12, R * 0.2, R * 0.25, 0, 0, TAU); ink(g, P, C.skinK, bb); blush(g, s * R * 0.97, R * 0.12, R * 0.18, 0.6); }
  const head = new Path2D(); head.ellipse(0, 0, R, R * 0.95, 0, 0, TAU);
  ink(g, head, C.skinK, bb, { lw: 0 });
  g.save(); g.clip(head); blush(g, -R * 0.55, R * 0.4, R * 0.42, 0.62); blush(g, R * 0.55, R * 0.4, R * 0.42, 0.62); blush(g, 0, R * 0.32, R * 0.2, 0.5); g.restore();
  g.lineWidth = 4.6; g.strokeStyle = C.ink; g.stroke(head);
  // messy black hair with a spiky fringe
  const hair = shape(T([[-1.04, 0.0], [-1.0, -0.45], [-0.78, -0.82], [-0.35, -1.04], [0.1, -1.08], [0.55, -0.95], [0.88, -0.7], [1.04, -0.3], [1.03, 0.02], [0.9, -0.36], [0.74, -0.3], [0.62, -0.5], [0.4, -0.36], [0.22, -0.56], [0.0, -0.4], [-0.2, -0.58], [-0.42, -0.38], [-0.62, -0.55], [-0.8, -0.34], [-0.94, -0.42]], 0, 0, R));
  ink(g, hair, C.hair, [-R, -R * 1.1, R, -R * 0.3], { hi: 0.18 });
  g.strokeStyle = 'rgba(255,255,255,0.18)'; g.lineWidth = 6; g.beginPath(); g.arc(-R * 0.1, -R * 0.2, R * 0.75, -2.5, -1.7); g.stroke();
  // crown cowlick
  g.lineWidth = 5; g.strokeStyle = C.ink; g.beginPath(); g.moveTo(R * 0.05, -R * 1.06); g.quadraticCurveTo(R * 0.2, -R * 1.28, R * 0.38, -R * 1.18); g.stroke();
  eyes(g, R, f, R * 0.4, R * 0.04, R * 0.33, R * 0.4, false);
  g.strokeStyle = C.ink; g.lineWidth = 5; g.lineCap = 'round';
  const by = -R * 0.46 + (f.brow === 'up' ? -10 : 0);
  for (const s of [-1, 1]) { g.beginPath(); if (f.brow === 'worried') { g.moveTo(s * R * 0.24, by - 4); g.quadraticCurveTo(s * R * 0.4, by - 14, s * R * 0.56, by + 4); } else { g.moveTo(s * R * 0.24, by + 2); g.quadraticCurveTo(s * R * 0.4, by - 10, s * R * 0.56, by); } g.stroke(); }
  g.beginPath(); g.moveTo(-R * 0.06, R * 0.37); g.quadraticCurveTo(0, R * 0.43, R * 0.07, R * 0.36); g.stroke();
  mouth(g, R, f.mouth || 'smile', R * 0.6);
  if (f.mouth === 'bite') { blush(g, -R * 0.42, R * 0.55, R * 0.2, 0.5); blush(g, R * 0.42, R * 0.55, R * 0.2, 0.5); }
  g.restore();
}
// Dad's head: spectacles, moustache, side-parted hair
function dadHead(g, x, y, R, f, rot = 0) {
  g.save(); g.translate(x, y); g.rotate(rot);
  const bb = [-R, -R * 1.1, R, R * 1.1];
  for (const s of [-1, 1]) { const P = new Path2D(); P.ellipse(s * R * 0.9, R * 0.12, R * 0.17, R * 0.24, 0, 0, TAU); ink(g, P, C.skinD, bb); blush(g, s * R * 0.9, R * 0.12, R * 0.15, 0.45); }
  const head = shape(T([[0, -1.08], [0.62, -0.92], [0.92, -0.35], [0.9, 0.35], [0.66, 0.82], [0.25, 1.06], [-0.25, 1.06], [-0.66, 0.82], [-0.9, 0.35], [-0.92, -0.35], [-0.62, -0.92]], 0, 0, R));
  ink(g, head, C.skinD, bb, { lw: 0 });
  g.save(); g.clip(head); blush(g, -R * 0.5, R * 0.42, R * 0.36, 0.45); blush(g, R * 0.5, R * 0.42, R * 0.36, 0.45); blush(g, 0, R * 0.3, R * 0.16, 0.4);
  g.fillStyle = 'rgba(60,40,35,0.10)'; g.beginPath(); g.ellipse(0, R * 0.78, R * 0.6, R * 0.32, 0, 0, TAU); g.fill(); g.restore();   // shave shadow
  g.lineWidth = 4.6; g.strokeStyle = C.ink; g.stroke(head);
  const hair = shape(T([[-0.94, 0.02], [-0.98, -0.5], [-0.7, -0.95], [-0.2, -1.16], [0.35, -1.12], [0.78, -0.88], [0.96, -0.45], [0.94, 0.02], [0.82, -0.4], [0.55, -0.66], [0.15, -0.74], [-0.3, -0.62], [-0.38, -0.78], [-0.62, -0.58], [-0.8, -0.38]], 0, 0, R));
  ink(g, hair, C.hair, [-R, -R * 1.2, R, -R * 0.3], { hi: 0.2 });
  g.strokeStyle = 'rgba(200,200,200,0.55)'; g.lineWidth = 4; g.beginPath(); g.moveTo(-R * 0.9, -R * 0.2); g.lineTo(-R * 0.84, -R * 0.45); g.moveTo(R * 0.9, -R * 0.2); g.lineTo(R * 0.85, -R * 0.45); g.stroke();   // grey temples
  eyes(g, R, f, R * 0.36, -R * 0.02, R * 0.25, R * 0.29, true);
  g.strokeStyle = C.ink; g.lineWidth = 6; g.lineCap = 'round';
  const by = -R * 0.46;
  for (const s of [-1, 1]) { g.beginPath(); g.moveTo(s * R * 0.2, by + (f.brow === 'worried' ? -6 : 2)); g.quadraticCurveTo(s * R * 0.36, by - 10, s * R * 0.54, by + (f.brow === 'worried' ? 6 : 0)); g.stroke(); }
  g.lineWidth = 5; g.beginPath(); g.moveTo(-R * 0.06, R * 0.34); g.quadraticCurveTo(0, R * 0.41, R * 0.07, R * 0.33); g.stroke();
  // moustache
  const mo = shape(T([[-0.36, 0.56], [-0.2, 0.44], [0, 0.48], [0.2, 0.44], [0.36, 0.56], [0.2, 0.58], [0, 0.55], [-0.2, 0.58]], 0, 0, R));
  ink(g, mo, C.hair, null, { lw: 3 });
  mouth(g, R, f.mouth || 'smile', R * 0.7, 0.9);
  g.restore();
}
function kidHand(g, x, y, s, type, rot = 0) {       // small hand on a full-body kid
  g.save(); g.translate(x, y); g.rotate(rot); g.scale(s, s);
  if (type === 'thumb') {
    ink(g, shape([[-20, -16], [18, -18], [24, 4], [16, 22], [-16, 22], [-24, 2]]), C.skinK, [-24, -20, 24, 22]);
    ink(g, shape([[-4, -18], [-8, -52], [6, -56], [10, -18]]), C.skinK, [-8, -56, 10, -18]); blush(g, 0, -48, 10, 0.6);
  } else {
    const P = new Path2D(); P.ellipse(0, 0, 22, 20, 0, 0, TAU); ink(g, P, C.skinK, [-22, -20, 22, 20]); blush(g, 4, 6, 14, 0.5);
    g.strokeStyle = C.ink; g.lineWidth = 3.5; g.beginPath(); g.moveTo(-10, 4); g.lineTo(10, 4); g.stroke();
  }
  g.restore();
}
// full-body Kid, front view. (x,y) = feet centre. o: {R, face, armL/armR: [[ex,ey],[hx,hy]] relative to shoulder, handL/handR, lean, legs}
function kid(g, x, y, s, o) {
  g.save(); g.translate(x, y); g.rotate(o.lean || 0);
  const f = o.face || {};
  const legSpread = o.legs ?? 34;
  const tip = o.tiptoe ? 1 : 0;
  // legs and feet
  for (const sgn of [-1, 1]) {
    limb(g, [[sgn * 30 * s, -150 * s], [sgn * legSpread * s, -20 * s - tip * 16 * s]], 36 * s, C.skinK);
    const P = new Path2D(); P.ellipse(sgn * (legSpread + 10) * s, -8 * s - tip * 10 * s, 30 * s, 14 * s, sgn * (tip ? 0.5 : 0.1), 0, TAU); ink(g, P, C.skinK, null); blush(g, sgn * (legSpread + 22) * s, -10 * s, 12 * s, 0.4);
  }
  // shorts
  ink(g, shape(T([[-78, -270], [78, -270], [86, -150], [8, -150], [0, -190], [-8, -150], [-86, -150]], 0, 0, s)), C.shorts, [-86 * s, -270 * s, 86 * s, -150 * s]);
  // arms behind torso when marked
  const sh = [[-80 * s, -420 * s], [80 * s, -420 * s]];
  const drawArm = (i) => {
    const a = i ? o.armR : o.armL; if (!a) return;
    const [x0, y0] = sh[i], e = [x0 + a[0][0] * s, y0 + a[0][1] * s], h = [x0 + a[1][0] * s, y0 + a[1][1] * s];
    limb(g, [[x0, y0], e, h], 34 * s, C.skinK);
    limb(g, [[x0, y0], [lerp(x0, e[0], 0.45), lerp(y0, e[1], 0.45)]], 50 * s, C.red);
    kidHand(g, h[0], h[1], s, i ? o.handR : o.handL, a[2] || 0);
  };
  if (o.armsBehind) { drawArm(0); drawArm(1); }
  // T-shirt
  ink(g, shape(T([[-82, -440], [-30, -460], [0, -446], [30, -460], [82, -440], [94, -330], [92, -262], [-92, -262], [-94, -330]], 0, 0, s)), C.red, [-94 * s, -460 * s, 94 * s, -262 * s], { sh: 'rgba(90,20,15,0.32)' });
  g.strokeStyle = C.ink; g.lineWidth = 4; g.beginPath(); g.moveTo(-30 * s, -458 * s); g.quadraticCurveTo(0, -425 * s, 30 * s, -458 * s); g.stroke();
  if (!o.armsBehind) { drawArm(0); drawArm(1); }
  kidHead(g, (o.headDx || 0) * s, -590 * s, 160 * s, f, o.headRot || 0);
  g.restore();
}
function shirtFill(g, P, bb) {     // Dad's blue checked shirt
  ink(g, P, C.shirt, bb, { lw: 0, sh: 'rgba(30,50,80,0.3)' });
  g.save(); g.clip(P);
  g.strokeStyle = C.shirtLine; g.lineWidth = 5;
  for (let x = bb[0] - 40; x < bb[2] + 40; x += 34) { g.beginPath(); g.moveTo(x, bb[1]); g.lineTo(x, bb[3]); g.stroke(); }
  for (let y = bb[1]; y < bb[3]; y += 34) { g.beginPath(); g.moveTo(bb[0], y); g.lineTo(bb[2], y); g.stroke(); }
  g.strokeStyle = C.shirtLine2; g.lineWidth = 2;
  for (let x = bb[0] - 23; x < bb[2] + 40; x += 34) { g.beginPath(); g.moveTo(x, bb[1]); g.lineTo(x, bb[3]); g.stroke(); }
  for (let y = bb[1] + 17; y < bb[3]; y += 34) { g.beginPath(); g.moveTo(bb[0], y); g.lineTo(bb[2], y); g.stroke(); }
  g.restore();
  g.lineWidth = 4.6; g.strokeStyle = C.ink; g.stroke(P);
}
// Dad seated, medium close-up. o: {face, point, kulfi, sway}
function dadMCU(g, x, y, s, o) {
  g.save(); g.translate(x, y);
  const body = shape(T([[-300, 700], [-290, 330], [-250, 180], [-120, 110], [0, 140], [120, 110], [250, 180], [290, 330], [300, 700]], 0, 0, s));
  shirtFill(g, body, [-310 * s, 100 * s, 310 * s, 720 * s]);
  // collar and placket
  ink(g, shape(T([[-120, 110], [-40, 230], [0, 150], [40, 230], [120, 110], [0, 140]], 0, 0, s)), '#9cc0dc', null, { lw: 4 });
  g.strokeStyle = C.ink; g.lineWidth = 4; g.beginPath(); g.moveTo(0, 150 * s); g.lineTo(0, 700 * s); g.stroke();
  for (let i = 0; i < 4; i++) { g.fillStyle = '#f4f0e6'; g.beginPath(); g.arc(12 * s, (250 + i * 110) * s, 7 * s, 0, TAU); g.fill(); g.stroke(); }
  // neck
  ink(g, shape(T([[-55, 40], [55, 40], [50, 150], [0, 175], [-50, 150]], 0, 0, s)), C.skinD, null);
  if (o.point) {   // right arm raised, index finger up
    const u = o.point;
    limb(g, [[230 * s, 230 * s], [lerp(260, 300, u) * s, lerp(420, 120, u) * s], [lerp(250, 270, u) * s, lerp(560, -120, u) * s]], 64 * s, C.skinD);
    limb(g, [[230 * s, 230 * s], [lerp(245, 270, u) * s, lerp(320, 180, u) * s]], 92 * s, C.shirt);
    const hx = lerp(250, 270, u) * s, hy = lerp(560, -120, u) * s;
    ink(g, shape(T([[-34, -10], [30, -14], [36, 24], [-30, 26]], hx, hy, s)), C.skinD, null);
    if (u > 0.9) { ink(g, shape(T([[-6, -12], [-8, -78], [8, -80], [12, -12]], hx + 10 * s, hy, s)), C.skinD, null); blush(g, hx + 10 * s, hy - 70 * s, 12 * s, 0.5); }
  }
  if (o.kulfi !== undefined) {   // holding (and offering) his kulfi
    const u = o.kulfi;
    const hx = lerp(150, -170, u) * s, hy = lerp(520, 430, u) * s;
    limb(g, [[200 * s, 260 * s], [lerp(260, 120, u) * s, lerp(470, 470, u) * s], [hx, hy]], 64 * s, C.skinD);
    limb(g, [[200 * s, 260 * s], [lerp(235, 190, u) * s, lerp(360, 360, u) * s]], 92 * s, C.shirt);
    kulfi(g, hx, hy - 70 * s, 0.95 * s, -0.15 + u * 0.1, {});
    const P = new Path2D(); P.ellipse(hx, hy, 40 * s, 34 * s, 0, 0, TAU); ink(g, P, C.skinD, null); blush(g, hx + 10 * s, hy, 18 * s, 0.4);
  }
  dadHead(g, (o.headDx || 0) * s, -110 * s + (o.sway || 0), 210 * s, o.face || {}, o.headRot || 0);
  g.restore();
}

// ---------- props and sets ----------
function kulfi(g, x, y, s, rot, o) {
  g.save(); g.translate(x, y); g.rotate(rot); g.scale(s, s);
  ink(g, shape([[-9, 60], [9, 60], [9, 150], [-9, 150]]), C.stick, null, { lw: 3.6 });
  const body = shape([[-44, -70], [-20, -92], [20, -92], [44, -70], [38, 30], [26, 66], [-26, 66], [-38, 30]]);
  g.save();
  if (o.bitten) { const cut = new Path2D(); cut.rect(-80, -140, 160, 260); cut.arc(14, -88, 34, 0, TAU, true); g.clip(cut, 'evenodd'); }
  ink(g, body, C.kulfi, [-44, -92, 44, 66], { lw: 0 });
  g.save(); g.clip(body);
  const gr = g.createLinearGradient(0, -92, 0, -20); gr.addColorStop(0, C.kulfiTop); gr.addColorStop(1, 'rgba(237,184,106,0)'); g.fillStyle = gr; g.fillRect(-50, -100, 100, 90);
  const q = rng(77); g.fillStyle = C.pista; for (let i = 0; i < 14; i++) { g.beginPath(); g.ellipse(-34 + q() * 68, -80 + q() * 140, 4.5, 3, q() * 3, 0, TAU); g.fill(); }
  g.fillStyle = 'rgba(255,255,250,0.55)'; g.beginPath(); g.ellipse(22, -40, 7, 28, 0.1, 0, TAU); g.fill();
  if (o.gold) { g.fillStyle = `rgba(255,205,70,${0.55 * o.gold})`; g.fillRect(-50, -100, 100, 180); }
  g.restore();
  g.lineWidth = 4.4; g.strokeStyle = C.ink; g.stroke(body);
  g.restore();
  if (o.drip) { g.fillStyle = C.kulfi; g.strokeStyle = C.ink; g.lineWidth = 3; g.beginPath(); g.ellipse(-30, 60 + o.drip * 160, 7, 10, 0, 0, TAU); g.fill(); g.stroke(); }
  g.restore();
}
function tvScreen(g, x, y, w, h, t, st) {    // st: {snow 0..1, pic 0..1, roll}
  g.save(); const P = new Path2D(); P.roundRect(x, y, w, h, Math.min(w, h) * 0.14); g.clip(P);
  if (st.pic > 0) {   // a cricket broadcast: sky, stands, field, pitch, tiny players, score strip
    g.fillStyle = '#9fc6df'; g.fillRect(x, y, w, h);
    g.fillStyle = '#c9b0a0'; g.fillRect(x, y + h * 0.18, w, h * 0.16);
    const q = rng(41); for (let i = 0; i < 60; i++) { g.fillStyle = ['#e2c6b4', '#b79686', '#f0e0d0'][i % 3]; g.fillRect(x + q() * w, y + h * (0.19 + q() * 0.13), 6, 4); }
    g.fillStyle = '#6fae4f'; g.fillRect(x, y + h * 0.34, w, h * 0.66);
    g.fillStyle = '#5c9a40'; for (let i = 0; i < 6; i++) g.fillRect(x, y + h * (0.34 + i * 0.12), w, h * 0.06);
    g.fillStyle = '#d8c08a'; g.beginPath(); g.moveTo(x + w * 0.46, y + h * 0.45); g.lineTo(x + w * 0.54, y + h * 0.45); g.lineTo(x + w * 0.6, y + h * 0.92); g.lineTo(x + w * 0.4, y + h * 0.92); g.fill();
    for (const [px, py, sc] of [[0.5, 0.86, 1.3], [0.5, 0.47, 0.8], [0.3, 0.6, 0.9], [0.72, 0.66, 1], [0.18, 0.78, 1.1]]) { g.fillStyle = '#fbfbf6'; g.beginPath(); g.arc(x + w * px, y + h * py - 12 * sc, 5 * sc, 0, TAU); g.fill(); g.fillRect(x + w * px - 4 * sc, y + h * py - 8 * sc, 8 * sc, 16 * sc); }
    g.fillStyle = '#1d3f8a'; g.fillRect(x + w * 0.06, y + h * 0.06, w * 0.34, h * 0.09); g.fillStyle = '#fff'; g.font = `${Math.round(h * 0.06)}px "Patrick Hand"`; g.textBaseline = 'middle'; g.fillText('IND 212/3', x + w * 0.08, y + h * 0.105);
    if (st.pic < 1) { g.globalAlpha = 1 - st.pic; }
  }
  if (st.snow > 0) {
    g.globalAlpha = st.pic > 0 ? st.snow : 1; g.imageSmoothingEnabled = false;
    g.drawImage(NOISE[Math.floor(t * 24) % NOISE.length], x, y, w, h); g.imageSmoothingEnabled = true; g.globalAlpha = 1;
    g.fillStyle = 'rgba(255,255,255,0.12)'; const ry = y + ((t * 1.7) % 1) * h; g.fillRect(x, ry, w, h * 0.06);
  }
  if (st.roll) { g.fillStyle = 'rgba(20,20,30,0.35)'; for (let i = 0; i < 5; i++) g.fillRect(x, y + ((st.roll * 3 + i * 0.21) % 1) * h, w, h * 0.04); }
  g.globalAlpha = 1;
  const gl = g.createRadialGradient(x + w * 0.35, y + h * 0.3, 0, x + w * 0.5, y + h * 0.5, w * 0.75); gl.addColorStop(0, 'rgba(255,255,255,0.18)'); gl.addColorStop(0.6, 'rgba(255,255,255,0)'); gl.addColorStop(1, 'rgba(0,0,0,0.35)');
  g.fillStyle = gl; g.fillRect(x, y, w, h); g.restore();
  g.lineWidth = 5; g.strokeStyle = C.ink; g.beginPath(); g.roundRect(x, y, w, h, Math.min(w, h) * 0.14); g.stroke();
}
function tv(g, x, y, s, t, st, knobAng = 0) {   // (x,y) = centre of the cabinet
  g.save(); g.translate(x, y); g.scale(s, s);
  // legs
  for (const lx of [-220, 220]) ink(g, shape([[lx - 14, 170], [lx + 14, 170], [lx + 10, 260], [lx - 6, 260]]), C.woodSh, null);
  const cab = new Path2D(); cab.roundRect(-290, -210, 580, 390, 30);
  ink(g, cab, C.wood, [-290, -210, 290, 180]);
  g.strokeStyle = 'rgba(255,220,180,0.25)'; g.lineWidth = 3; for (let i = 0; i < 5; i++) { g.beginPath(); g.moveTo(-270, -150 + i * 70); g.quadraticCurveTo(0, -140 + i * 70 + 10, 270, -152 + i * 70); g.stroke(); }
  const bez = new Path2D(); bez.roundRect(-262, -184, 380, 338, 40); ink(g, bez, '#3b3936', null);
  tvScreen(g, -240, -164, 336, 298, t, st);
  // control panel: channel dial, volume knob, speaker grille
  const pan = new Path2D(); pan.roundRect(140, -184, 126, 338, 18); ink(g, pan, C.woodSh, null, { lw: 4 });
  g.save(); g.translate(203, -110); g.rotate(knobAng);
  const k = new Path2D(); k.arc(0, 0, 44, 0, TAU); ink(g, k, '#d9d2c4', [-44, -44, 44, 44]);
  g.fillStyle = C.ink; g.fillRect(-6, -40, 12, 30);
  for (let i = 0; i < 12; i++) { const a = i * TAU / 12; g.fillRect(Math.cos(a) * 36 - 2, Math.sin(a) * 36 - 2, 4, 4); }
  g.restore();
  const v = new Path2D(); v.arc(203, -20, 22, 0, TAU); ink(g, v, '#d9d2c4', null);
  g.strokeStyle = C.ink; g.lineWidth = 3; for (let i = 0; i < 6; i++) { g.beginPath(); g.moveTo(165, 30 + i * 18); g.lineTo(241, 30 + i * 18); g.stroke(); }
  // lace doily and flower vase on top
  const lace = new Path2D(); lace.moveTo(-220, -212);
  for (let i = 0; i <= 12; i++) { const xx = -220 + i * 36.6; lace.quadraticCurveTo(xx - 18, -170, xx, -212); }
  lace.lineTo(220, -222); lace.lineTo(-220, -222); lace.closePath(); ink(g, lace, C.lace, null, { lw: 3 });
  g.fillStyle = 'rgba(160,140,120,0.5)'; for (let i = 0; i < 12; i++) { g.beginPath(); g.arc(-202 + i * 36.6, -196, 4, 0, TAU); g.fill(); }
  ink(g, shape([[150, -222], [190, -222], [196, -270], [176, -300], [164, -300], [144, -270]]), '#5d8fa0', null, { lw: 4 });
  for (const [fx, fy, c] of [[150, -330, '#e0573f'], [176, -350, '#f0b33a'], [198, -322, '#e0573f']]) { g.strokeStyle = '#5a7a3a'; g.lineWidth = 4; g.beginPath(); g.moveTo(170, -300); g.lineTo(fx, fy); g.stroke(); const P = new Path2D(); P.arc(fx, fy, 15, 0, TAU); ink(g, P, c, null, { lw: 3.5 }); }
  g.restore();
}
function livingRoom(g, t, o = {}) {
  let gr = g.createLinearGradient(0, 300, 0, 1500); gr.addColorStop(0, '#EBD3A6'); gr.addColorStop(1, C.wallSh);
  g.fillStyle = gr; g.fillRect(0, 0, W, H);
  g.fillStyle = '#C79A64'; g.fillRect(0, 1480, W, 440);   // floor
  g.strokeStyle = 'rgba(120,80,50,0.25)'; g.lineWidth = 3; for (let x = -200; x < 1300; x += 160) { g.beginPath(); g.moveTo(x, 1480); g.lineTo(x - 140, 1920); g.stroke(); }
  g.fillStyle = 'rgba(120,80,50,0.25)'; g.fillRect(0, 1474, W, 8);
  if (o.calendar) {   // wall calendar
    ink(g, shape([[o.calendar[0] - 70, o.calendar[1] - 100], [o.calendar[0] + 70, o.calendar[1] - 100], [o.calendar[0] + 70, o.calendar[1] + 100], [o.calendar[0] - 70, o.calendar[1] + 100]]), '#f4ecdc', null, { lw: 3.5 });
    g.fillStyle = '#e8794a'; g.fillRect(o.calendar[0] - 58, o.calendar[1] - 88, 116, 90); g.fillStyle = '#f3c050'; g.beginPath(); g.arc(o.calendar[0], o.calendar[1] - 44, 26, 0, TAU); g.fill();
    g.fillStyle = 'rgba(80,60,40,0.6)'; for (let r = 0; r < 4; r++) for (let c = 0; c < 6; c++) g.fillRect(o.calendar[0] - 56 + c * 20, o.calendar[1] + 14 + r * 18, 12, 9);
  }
}
function sofa(g, x, y, w, s) {
  const back = new Path2D(); back.roundRect(x - w / 2, y - 330 * s, w, 360 * s, 60 * s); ink(g, back, C.sofa, [x - w / 2, y - 330 * s, x + w / 2, y]);
  const seat = new Path2D(); seat.roundRect(x - w / 2 - 20, y - 20 * s, w + 40, 150 * s, 40 * s); ink(g, seat, C.sofaSh, null);
  for (const sd of [-1, 1]) { const a = new Path2D(); a.roundRect(x + sd * (w / 2 + 10) - 60 * s, y - 120 * s, 120 * s, 260 * s, 50 * s); ink(g, a, C.sofa, null); }
  // crochet cover on the backrest
  const lc = new Path2D(); lc.moveTo(x - w * 0.3, y - 330 * s); lc.lineTo(x + w * 0.3, y - 330 * s); lc.lineTo(x + w * 0.3, y - 210 * s);
  for (let i = 0; i <= 8; i++) { const xx = x + w * 0.3 - i * (w * 0.6 / 8); lc.quadraticCurveTo(xx + w * 0.0375, y - 180 * s, xx, y - 210 * s); }
  lc.closePath(); ink(g, lc, C.lace, null, { lw: 3.5 });
}
function doorway(g, t) {
  g.fillStyle = '#E9C88E'; g.fillRect(0, 0, W, H);
  const gr = g.createRadialGradient(560, 1050, 0, 560, 1050, 620); gr.addColorStop(0, 'rgba(255,214,140,0.9)'); gr.addColorStop(1, 'rgba(255,214,140,0)'); g.fillStyle = gr; g.fillRect(0, 0, W, H);
  // room beyond: a shelf and picture frames, soft
  g.strokeStyle = 'rgba(170,120,60,0.6)'; g.lineWidth = 6; g.strokeRect(470, 760, 150, 120); g.strokeRect(660, 700, 110, 150); g.beginPath(); g.moveTo(380, 1250); g.lineTo(820, 1250); g.stroke();
  // door frame
  g.fillStyle = '#d9b47c'; g.fillRect(150, 520, 40, 1300); g.fillRect(890, 520, 40, 1300);
  g.strokeStyle = C.ink; g.lineWidth = 4.6; g.strokeRect(150, 520, 40, 1300); g.strokeRect(890, 520, 40, 1300);
  // curtain rod and curtain gathered to the left
  ink(g, shape([[120, 528], [960, 528], [960, 548], [120, 548]]), '#8f8a85', null, { lw: 4 });
  const cur = shape([[170, 548], [420, 548], [380, 900], [300, 1060], [330, 1300], [300, 1820], [170, 1820]]);
  ink(g, cur, C.curtain, [170, 548, 420, 1820], { sh: 'rgba(90,50,10,0.35)' });
  g.strokeStyle = 'rgba(120,80,30,0.6)'; g.lineWidth = 4; for (const xx of [220, 270, 320]) { g.beginPath(); g.moveTo(xx, 560); g.quadraticCurveTo(xx + 20, 900, xx - 10, 1060); g.quadraticCurveTo(xx + 10, 1400, xx - 5, 1800); g.stroke(); }
  ink(g, shape([[250, 1040], [360, 1030], [366, 1080], [250, 1090]]), '#8a6a3a', null, { lw: 4 });   // tie-back
  g.fillStyle = '#d7b07a'; g.fillRect(0, 1780, W, 140);
}
function rooftopSky(g, blur = 0) {
  let gr = g.createLinearGradient(0, 300, 0, 1700); gr.addColorStop(0, '#F3C49A'); gr.addColorStop(0.45, '#F6D9AF'); gr.addColorStop(1, '#EAC9B2');
  g.fillStyle = gr; g.fillRect(0, 0, W, H);
  glow(g, 820, 820, 420, 0.8, [255, 214, 150]);
  g.save(); if (blur) g.filter = `blur(${blur}px)`;
  // distant rooftops and a water tank
  g.fillStyle = 'rgba(214,170,150,0.9)';
  for (const [x, w, h] of [[-20, 220, 260], [200, 160, 190], [360, 240, 300], [640, 180, 230], [820, 280, 280]]) g.fillRect(x, 1500 - h, w, h + 420);
  g.fillStyle = 'rgba(190,140,125,0.9)'; g.fillRect(410, 1140, 90, 70); g.beginPath(); g.ellipse(455, 1140, 45, 14, 0, 0, TAU); g.fill();
  g.strokeStyle = 'rgba(170,120,110,0.8)'; g.lineWidth = 3; g.beginPath(); g.moveTo(200, 1260); g.quadraticCurveTo(320, 1290, 420, 1255); g.stroke();
  g.restore();
}
function antenna(g, x, yTop, yBot, ang, s = 1) {   // TV aerial: pole + yagi boom with elements; ang rotates it (foreshortening)
  ink(g, shape([[x - 9, yTop], [x + 9, yTop], [x + 9, yBot], [x - 9, yBot]]), '#8d8a86', null, { lw: 4 });
  const c = Math.cos(ang), L = 300 * s;
  g.lineCap = 'round';
  g.strokeStyle = C.ink; g.lineWidth = 14; g.beginPath(); g.moveTo(x - L / 2 * c, yTop + 20); g.lineTo(x + L / 2 * c, yTop + 20); g.stroke();
  g.strokeStyle = '#b8b4ae'; g.lineWidth = 7; g.stroke();
  for (let i = 0; i < 7; i++) {
    const px = x + (-L / 2 + i * L / 6) * c, len = (110 - i * 10) * s;
    g.strokeStyle = C.ink; g.lineWidth = 10; g.beginPath(); g.moveTo(px, yTop + 20 - len / 2); g.lineTo(px, yTop + 20 + len / 2); g.stroke();
    g.strokeStyle = '#c9c5bf'; g.lineWidth = 4; g.stroke();
  }
  g.strokeStyle = C.ink; g.lineWidth = 4; g.beginPath(); g.moveTo(x + 6, yTop + 30); g.bezierCurveTo(x + 60, yTop + 200, x - 30, yBot - 200, x + 40, yBot); g.stroke();
}
function parapet(g, y) {
  const P = new Path2D(); P.rect(-10, y, W + 20, H - y + 10); ink(g, P, '#E3CBB0', [0, y, W, H]);
  g.fillStyle = '#cdb090'; g.fillRect(0, y, W, 26); g.strokeStyle = C.ink; g.lineWidth = 4; g.beginPath(); g.moveTo(0, y + 26); g.lineTo(W, y + 26); g.stroke();
  g.strokeStyle = 'rgba(150,110,80,0.5)'; g.lineWidth = 3; for (const [a, b] of [[120, 60], [520, 90], [860, 50]]) { g.beginPath(); g.moveTo(a, y + 60); g.lineTo(a + 30, y + 60 + b); g.lineTo(a + 10, y + 60 + b + 40); g.stroke(); }
}
// a big POV hand from the bottom: the Kid's (blushed fingertips) or Dad's (hairy, wristwatch)
function bigHand(g, x, y, s, type, who, rot = 0) {
  g.save(); g.translate(x, y); g.rotate(rot); g.scale(s, s);
  const skin = who === 'dad' ? C.skinD : C.skinK;
  const arm = shape([[-70, 0], [-82, 700], [82, 700], [70, 0]]); ink(g, arm, skin, [-82, 0, 82, 700], { lw: 0 });
  g.lineWidth = 4.6; g.strokeStyle = C.ink; g.beginPath(); g.moveTo(-70, 0); g.lineTo(-82, 700); g.moveTo(70, 0); g.lineTo(82, 700); g.stroke();
  if (who === 'dad') {
    g.strokeStyle = 'rgba(40,25,20,0.6)'; g.lineWidth = 2.5; const q = rng(9); for (let i = 0; i < 26; i++) { const hx = -60 + q() * 120, hy = 60 + q() * 300; g.beginPath(); g.moveTo(hx, hy); g.lineTo(hx + 6, hy - 12); g.stroke(); }
    ink(g, shape([[-80, 70], [80, 70], [82, 130], [-82, 130]]), '#6a4630', null, { lw: 4 });
    const d = new Path2D(); d.arc(0, 100, 44, 0, TAU); ink(g, d, '#d9cdb5', null, { lw: 5 }); g.lineWidth = 3; g.beginPath(); g.moveTo(0, 100); g.lineTo(0, 74); g.moveTo(0, 100); g.lineTo(18, 108); g.stroke();
  } else {
    g.strokeStyle = 'rgba(70,40,30,0.5)'; g.lineWidth = 3; g.beginPath(); g.moveTo(-60, 40); g.quadraticCurveTo(0, 60, 60, 40); g.stroke();
  }
  if (type === 'fist') {
    const P = shape([[-96, -30], [-110, -150], [-80, -250], [0, -275], [80, -250], [108, -160], [96, -30], [0, 10]]);
    ink(g, P, skin, [-110, -275, 108, 10]);
    g.save(); g.clip(P); blush(g, 0, -235, 110, 0.6, 0.5); g.restore();
    g.strokeStyle = C.ink; g.lineWidth = 4; for (const fx of [-50, 0, 50]) { g.beginPath(); g.moveTo(fx, -265); g.quadraticCurveTo(fx + 4, -230, fx, -200); g.stroke(); }
    g.beginPath(); g.moveTo(-96, -120); g.quadraticCurveTo(-30, -100, 10, -150); g.stroke();
  } else if (type === 'open') {
    const fing = [[-104, -150, -150, -330, 40], [-50, -200, -62, -440, 44], [8, -205, 10, -470, 46], [62, -195, 82, -445, 44], [104, -150, 140, -360, 40]];
    for (const [ax, ay, bx2, by2, w] of fing) { limb(g, [[ax, ay], [bx2, by2]], w, skin); }
    ink(g, shape([[-110, -10], [-118, -150], [-70, -230], [0, -240], [70, -230], [118, -150], [110, -10], [0, 20]]), skin, [-118, -240, 118, 20], { lw: 0 });
    for (const [ax, ay, bx2, by2] of fing) blush(g, bx2, by2 + 20, 34, 0.7, 1);
    blush(g, 0, -120, 120, 0.35, 0.8);
    g.strokeStyle = C.ink; g.lineWidth = 4.6; g.beginPath(); g.moveTo(-110, -10); g.quadraticCurveTo(-120, -110, -112, -160); g.moveTo(110, -10); g.quadraticCurveTo(120, -110, 112, -160); g.stroke();
    g.strokeStyle = 'rgba(90,40,25,0.45)'; g.lineWidth = 3; g.beginPath(); g.moveTo(-70, -150); g.quadraticCurveTo(0, -120, 70, -160); g.moveTo(-60, -90); g.quadraticCurveTo(-10, -70, 40, -100); g.stroke();
  } else if (type === 'pinch') {   // Dad's hand from the top holding a kulfi stick
    const P = shape([[-90, -20], [-100, -150], [-60, -230], [30, -240], [90, -200], [100, -60], [70, 10]]);
    ink(g, P, skin, [-100, -240, 100, 10]);
    g.strokeStyle = C.ink; g.lineWidth = 4; for (const fx of [-40, 10]) { g.beginPath(); g.moveTo(fx, -232); g.quadraticCurveTo(fx + 6, -200, fx, -170); g.stroke(); }
  }
  g.restore();
}

// ---------- the 19 shots ----------
const SH = [];
const add = (fn) => SH.push(fn);
const wallBg = (g, x, y, r) => { livingRoom(g, 0, {}); glow(g, x, y, r, 0.85); };

// 1 · establishing still life: the TV crackling, Dad's chai
add((g, t, lt) => {
  wallBg(g, 520, 1050, 700);
  glow(g, 470, 1000, 420, 0.4, [190, 220, 255]);
  const st = { snow: 0.55 + 0.25 * Math.sin(lt * 9), pic: 0.55 };
  g.fillStyle = '#9a6a44'; g.fillRect(80, 1330, 920, 40); g.strokeStyle = C.ink; g.lineWidth = 4.6; g.strokeRect(80, 1330, 920, 40);
  tv(g, 500, 1050, 1.25, t, st, 0);
  // steel tumbler of chai with steam
  ink(g, shape([[760, 1500], [870, 1500], [856, 1690], [774, 1690]]), C.steel, [760, 1500, 870, 1690], { sh: 'rgba(40,40,40,0.35)' });
  g.fillStyle = '#b77b4a'; g.beginPath(); g.ellipse(815, 1502, 55, 12, 0, 0, TAU); g.fill(); g.stroke();
  ink(g, shape([[700, 1690], [930, 1690], [910, 1720], [720, 1720]]), C.steel, null);
  g.strokeStyle = 'rgba(255,255,255,0.7)'; g.lineWidth = 6; g.lineCap = 'round';
  for (let i = 0; i < 3; i++) { const ph = lt * 2 + i * 2.1; g.globalAlpha = 0.5 + 0.3 * Math.sin(ph); g.beginPath(); g.moveTo(790 + i * 22, 1480); g.bezierCurveTo(770 + i * 22 + 20 * Math.sin(ph), 1420, 820 + i * 22 - 20 * Math.sin(ph), 1380, 800 + i * 22, 1320); g.stroke(); }
  g.globalAlpha = 1;
});
// 2 · Dad's hand reaches for the channel knob from the sofa, and can't reach
add((g, t, lt) => {
  wallBg(g, 560, 1000, 650);
  tv(g, 160, 1000, 2.6, t, { snow: 0.9, pic: 0.1 }, 0);
  const u = eo(seg(twos(lt), 0.15, 1.3));
  const reach = twos(lt) > 1.55;
  const hx = lerp(260, 470, u), hy = lerp(2150, 1290, u);
  bigHand(g, hx, hy + (reach ? -14 : 0), 1.05, 'open', 'dad', 0.32);
  if (reach) ticks(g, hx + 120, hy - 380, 30, 3, -1.2, -0.2, 1);
});
// 3 · Dad on the sofa, watching
add((g, t, lt) => {
  livingRoom(g, 0, { calendar: [880, 760] }); glow(g, 540, 1050, 640, 0.8);
  sofa(g, 540, 1500, 900, 1.1);
  dadMCU(g, 540, 1080, 1.05, { face: { lx: 0.7, ly: 0.1, mouth: 'flat', blink: blinkAt(t) } });
  ink(g, shape([[560, 1560], [930, 1520], [960, 1720], [600, 1760]]), '#efe9dc', [560, 1520, 960, 1760]);   // newspaper on his lap
  g.strokeStyle = 'rgba(60,50,40,0.5)'; g.lineWidth = 3; for (let i = 0; i < 6; i++) { g.beginPath(); g.moveTo(600, 1590 + i * 24); g.lineTo(900, 1556 + i * 24); g.stroke(); }
});
// 4 · the problem: the match dissolves into static
add((g, t, lt) => {
  wallBg(g, 540, 1080, 700);
  const P = new Path2D(); P.roundRect(80, 640, 920, 860, 90); ink(g, P, '#3b3936', null);
  const k = seg(lt, 0.3, 1.1);
  tvScreen(g, 120, 680, 840, 780, t, { snow: k, pic: 1 - k * 0.85, roll: k > 0 && k < 1 ? lt : 0 });
});
// 5 · comic still: Dad sighs (held completely still)
add((g, t, lt) => {
  livingRoom(g, 0, { calendar: [880, 760] }); glow(g, 540, 1050, 640, 0.8);
  sofa(g, 540, 1500, 900, 1.1);
  dadMCU(g, 540, 1080, 1.05, { face: { eyes: 'closed', mouth: 'o', brow: 'worried' }, headRot: -0.06 });
  ink(g, shape([[560, 1560], [930, 1520], [960, 1720], [600, 1760]]), '#efe9dc', [560, 1520, 960, 1760]);
  g.strokeStyle = 'rgba(60,50,40,0.5)'; g.lineWidth = 3; for (let i = 0; i < 6; i++) { g.beginPath(); g.moveTo(600, 1590 + i * 24); g.lineTo(900, 1556 + i * 24); g.stroke(); }
  g.strokeStyle = 'rgba(140,140,150,0.8)'; g.lineWidth = 5; g.lineCap = 'round'; g.beginPath(); g.moveTo(690, 1030); g.quadraticCurveTo(740, 1010, 760, 1040); g.moveTo(705, 1060); g.quadraticCurveTo(760, 1050, 790, 1080); g.stroke();   // sigh puff
});
// 6 · the Kid peeks in from behind the curtain
add((g, t, lt) => {
  doorway(g, t);
  const u = eo(seg(twos(lt), 0.0, 0.5));
  kid(g, lerp(860, 760, u), 1760, 0.95, { lean: -0.12, face: { lx: -0.5, ly: -0.2, mouth: 'o', brow: 'up', blink: blinkAt(t) }, armL: [[-70, 100], [-90, 0]], handL: 'open', armR: [[60, 160], [40, 290]], handR: 'open', armsBehind: false });
  if (lt > 0.8) { const p = back(seg(lt, 0.8, 1.05)); g.save(); g.translate(660, 900); g.scale(p, p); g.fillStyle = C.ink; g.font = '90px "Patrick Hand"'; g.textAlign = 'center'; g.fillText('?', 0, 0); g.restore(); }
  // the door frame edge stays in front of him
  g.fillStyle = '#d9b47c'; g.fillRect(890, 520, 40, 1300); g.strokeStyle = C.ink; g.lineWidth = 4.6; g.strokeRect(890, 520, 40, 1300);
});
// 7 · POV: the Kid's hand takes over the channel dial, click, click, click
add((g, t, lt) => {
  g.fillStyle = C.wood; g.fillRect(0, 0, W, H); glow(g, 560, 900, 600, 0.5);
  g.save(); g.beginPath(); g.roundRect(-200, 300, 520, 820, 80); g.clip(); tvScreen(g, -200, 300, 520, 820, t, { snow: 1, pic: 0 }); g.restore();
  g.strokeStyle = 'rgba(255,220,180,0.2)'; g.lineWidth = 4; for (let i = 0; i < 8; i++) { g.beginPath(); g.moveTo(380, 300 + i * 200); g.quadraticCurveTo(700, 320 + i * 200, 1100, 290 + i * 200); g.stroke(); }
  const clicks = [2.15, 2.85, 3.55];
  let ang = 0; for (const c of clicks) ang += eo(seg(lt, c, c + 0.12)) * (TAU / 12);
  g.save(); g.translate(700, 860); g.rotate(ang);
  const k = new Path2D(); k.arc(0, 0, 190, 0, TAU); ink(g, k, '#d9d2c4', [-190, -190, 190, 190]);
  const k2 = new Path2D(); k2.arc(0, 0, 130, 0, TAU); g.strokeStyle = 'rgba(80,70,60,0.4)'; g.lineWidth = 4; g.stroke(k2);
  g.fillStyle = C.ink; g.beginPath(); g.roundRect(-24, -176, 48, 120, 18); g.fill();
  g.font = 'bold 34px "Patrick Hand"'; g.textAlign = 'center'; g.textBaseline = 'middle'; for (let i = 0; i < 12; i++) { const a = i * TAU / 12 - Math.PI / 2; g.fillText(String(i + 1), Math.cos(a) * 230, Math.sin(a) * 230); }
  g.restore();
  for (const c of clicks) if (lt > c && lt < c + 0.3) ticks(g, 700, 860, 250, 3, -0.6, 0.4, 1 - seg(lt, c, c + 0.3));
  const open = twos(lt) >= 0.667, onKnob = twos(lt) >= 1.6;
  const u = eo(seg(twos(lt), 1.2, 1.6));
  bigHand(g, lerp(540, 690, u), lerp(1700, 1240, u), 1.0, open && !onKnob ? 'open' : 'fist', 'kid', lerp(0, 0.1, u));
});
// 8 · Dad smiles and points up: "go turn the antenna on the roof"
add((g, t, lt) => {
  livingRoom(g, 0, { calendar: [880, 760] }); glow(g, 540, 1050, 640, 0.8);
  sofa(g, 540, 1500, 900, 1.1);
  const u = eo(seg(twos(lt), 0.4, 0.75));
  dadMCU(g, 520, 1080, 1.05, { face: { lx: -0.6, ly: -0.1, mouth: 'smile', blink: blinkAt(t) }, point: u, headRot: -0.03 });
  if (u > 0.95) { ticks(g, 812, 860, 46, 3, -2.3, -1.0, 1); sparkle(g, 860, 760, 26 * (0.6 + 0.4 * Math.sin(lt * 10))); }
});
// 9 · thumbs up, and off he runs (the song comes in here)
add((g, t, lt) => {
  doorway(g, t);
  const run = ei(seg(twos(lt), 1.45, 2.05));
  const x = lerp(560, 1500, run);
  if (run > 0) { g.strokeStyle = C.ink; g.lineWidth = 5; g.lineCap = 'round'; for (let i = 0; i < 4; i++) { g.globalAlpha = 1 - run * 0.6; g.beginPath(); g.moveTo(x - 260 - i * 30, 1000 + i * 120); g.lineTo(x - 420 - i * 30, 1000 + i * 120); g.stroke(); } g.globalAlpha = 1; }
  kid(g, x, 1760, 0.95, { lean: run > 0 ? 0.2 : 0, face: { lx: 0, ly: 0, eyes: run > 0 ? 'open' : 'open', mouth: 'grin', brow: 'up', blink: blinkAt(t) }, armL: [[-60, 150], [-50, 280]], handL: 'open', armR: [[90, 60], [110, -90], -0.2], handR: 'thumb' });
  if (run === 0 && lt > 0.3) sparkle(g, 700, 1050, 24 * (0.6 + 0.4 * Math.sin(lt * 12)));
  if (run > 0.2) { g.fillStyle = 'rgba(230,200,160,0.8)'; for (let i = 0; i < 3; i++) { g.beginPath(); g.arc(x - 200 - i * 50, 1740 - i * 10, 30 - i * 6, 0, TAU); g.fill(); } }
});
// 10 · on the roof: "aaya papaaa??"
add((g, t, lt) => {
  rooftopSky(g);
  parapet(g, 1560);
  const ang = 0.5 * Math.sin(twos(lt) * 3.2) + 0.2;
  antenna(g, 620, 640, 1580, ang, 1.2);
  kid(g, 500, 1760, 0.92, { tiptoe: true, face: { lx: -0.4, ly: -0.5, mouth: 'shout', brow: 'up', blink: blinkAt(t) }, armL: [[80, -40], [118, -170]], handL: 'fist', armR: [[60, -60], [112, -230]], handR: 'fist', headRot: -0.08 });
  bubble(g, 'aaya papaaa??', 380, 760, seg(lt, 0.35, 0.6), -1);
});
// 11 · over Dad's shoulder: static... then the picture snaps back
add((g, t, lt) => {
  livingRoom(g, 0, {}); glow(g, 560, 900, 560, 0.7, [200, 225, 255]);
  const on = twos(lt) >= 0.95;
  tv(g, 600, 880, 1.2, t, on ? { snow: 0.15 * Math.max(0, 1 - (lt - 0.95) * 4), pic: 1 } : { snow: 1, pic: 0 }, 0);
  if (on) { sparkle(g, 820, 650, 34 * (0.5 + 0.5 * Math.sin(lt * 9))); sparkle(g, 340, 760, 24); }
  // back of Dad's head and shoulders, bottom left
  const sh = shape([[-80, 1920], [-60, 1560], [80, 1440], [380, 1420], [560, 1560], [600, 1920]]); shirtFill(g, sh, [-80, 1420, 600, 1920]);
  const hd = new Path2D(); hd.ellipse(260, 1270, 200, 220, 0, 0, TAU); ink(g, hd, C.hair, [60, 1050, 460, 1490], { hi: 0.15 });
  for (const s of [-1, 1]) { const e = new Path2D(); e.ellipse(260 + s * 200, 1300, 34, 52, 0, 0, TAU); ink(g, e, C.skinD, null); blush(g, 260 + s * 200, 1300, 28, 0.5); }
  g.strokeStyle = '#3a2a22'; g.lineWidth = 7; g.beginPath(); g.moveTo(80, 1270); g.lineTo(60, 1300); g.moveTo(440, 1270); g.lineTo(462, 1300); g.stroke();
});
// 12 · triumph on the roof
add((g, t, lt) => {
  rooftopSky(g);
  parapet(g, 1560);
  antenna(g, 760, 640, 1580, 0, 1.0);
  const hop = Math.sin(Math.PI * seg(twos(lt), 0.1, 0.55)) * 60;
  kid(g, 460, 1760 - hop, 0.92, { face: { eyes: 'happy', mouth: 'grin', brow: 'up' }, armL: [[-80, -60], [-120, -210]], handL: 'fist', armR: [[80, -60], [120, -210]], handR: 'fist' });
  ticks(g, 460, 820 - hop, 220, 5, -2.6, -0.5, 1);
  sparkle(g, 250, 760, 30 * (0.6 + 0.4 * Math.sin(lt * 11))); sparkle(g, 690, 700, 22 * (0.6 + 0.4 * Math.sin(lt * 9 + 1)));
});
// 13 · proud, eyes shut... and Dad calls him down (focus pull)
add((g, t, lt) => {
  const fp = eio(seg(lt, 2.2, 2.75));
  rooftopSky(g, lerp(6, 0, fp));
  // stairwell door at the back right, Dad popping out and waving
  g.save(); g.filter = `blur(${lerp(6, 0, fp)}px)`;
  ink(g, shape([[700, 980], [1000, 980], [1000, 1560], [700, 1560]]), '#d8bea0', [700, 980, 1000, 1560]);
  ink(g, shape([[760, 1080], [930, 1080], [930, 1560], [760, 1560]]), '#5a4030', null);
  const pop = eo(seg(twos(lt), 1.2, 1.6));
  if (pop > 0) {
    g.save(); g.beginPath(); g.rect(760, 1000, 170, 560); g.clip();
    const wave = Math.sin(twos(lt) * 9) * 0.35;
    limb(g, [[900, 1360], [960, 1250], [990 + wave * 40, 1130]], 40, C.skinD);
    dadHead(g, 845, lerp(1500, 1250, pop), 75, { mouth: 'open', lx: -0.6 });
    g.restore();
    if (pop > 0.9) bubble(g, '!', 900, 1150, 1, 0);
  }
  g.restore();
  parapet(g, 1560);
  ly.setTransform(1, 0, 0, 1, 0, 0); ly.clearRect(0, 0, W, H);
  kid(ly, 420, 1960, 1.15, { face: { eyes: 'happy', mouth: 'smile', brow: 'up' }, armL: [[-100, 130], [-40, 230]], handL: 'fist', armR: [[100, 130], [40, 230]], handR: 'fist' });
  g.save(); g.filter = `blur(${fp * 13}px)`; g.drawImage(LY, 0, 0); g.restore();
});
// 14 · POV: fist opens, and Dad drops a kulfi into the palm
add((g, t, lt) => {
  rooftopSky(g, 10); glow(g, 540, 1100, 640, 0.6);
  const open = twos(lt) >= 0.75;
  const drop = eo(seg(twos(lt), 1.3, 2.0)), leave = ei(seg(twos(lt), 2.25, 2.9));
  const kx = 560, ky = lerp(-200, 1180, drop);
  bigHand(g, 540, 1880, 1.12, open ? 'open' : 'fist', 'kid', 0);
  if (open && drop > 0) {
    kulfi(g, kx, ky, 1.35, drop >= 1 ? -0.5 : -0.2, {});
    if (leave < 1) bigHand(g, kx + 40, lerp(ky - 260, -500, leave), 1.0, 'pinch', 'dad', Math.PI);
  }
  if (lt > 2.5) sparkle(g, 660, 1000, 36 * (0.6 + 0.4 * Math.sin(lt * 10))), sparkle(g, 450, 1160, 22 * (0.6 + 0.4 * Math.sin(lt * 8 + 2)));
});
// 15 · puzzled... delighted. "thank youuu"
add((g, t, lt) => {
  rooftopSky(g, 8); glow(g, 540, 1100, 620, 0.7);
  const happy = twos(lt) >= 2.36;
  kid(g, 540, 2300, 1.25, { face: happy ? { lx: 0, ly: 0, mouth: 'grin', brow: 'up', blink: blinkAt(t) } : { lx: 0.3, ly: 0.7, mouth: 'o', brow: 'worried' }, armL: [[-40, 160], [70, 150]], handL: 'fist', armR: [[60, 180], [-20, 120]], handR: 'fist', armsBehind: false });
  kulfi(g, 560, 1540, 1.1, 0.12, {});
  kidHand(g, 560, 1640, 1.25, 'fist', 0);
  sparkle(g, 640, 1440, 26 * (0.5 + 0.5 * Math.sin(lt * 9)));
  bubble(g, 'thank youuu', 820, 680, seg(lt, 3.46, 3.75), 1);
});
// 16 · back home: side by side on the sofa, kulfi and cricket
add((g, t, lt) => {
  livingRoom(g, 0, { calendar: [900, 700] }); glow(g, 540, 1150, 620, 0.75); glow(g, 540, 1300, 500, 0.35, [200, 225, 255]);
  sofa(g, 540, 1460, 900, 1.0);
  dadMCU(g, 360, 1170, 0.62, { face: { lx: 0.2, ly: 0.2, mouth: 'smile', blink: blinkAt(t) }, kulfi: 0 });
  const sw = Math.sin(lt * 7) * 0.25;
  const k = (g2) => kid(g2, 720, 1720, 0.62, { face: { lx: -0.2, ly: 0.2, mouth: 'smile', blink: blinkAt(t + 0.4) }, armL: [[40, 150], [110, 120]], handL: 'fist', armR: [[60, 180], [-10, 140]], handR: 'fist', legs: 34 });
  k(g); kulfi(g, 760, 1340, 0.6, 0.1, {});
  // swinging feet hanging off the sofa
  g.save(); g.translate(720, 1600); for (const s of [-1, 1]) { g.save(); g.rotate(sw * s); limb(g, [[s * 20, 0], [s * 24, 120]], 22, C.skinK); g.restore(); } g.restore();
});
// 17 · Dad offers his kulfi too
add((g, t, lt) => {
  livingRoom(g, 0, { calendar: [880, 760] }); glow(g, 540, 1050, 640, 0.8);
  sofa(g, 540, 1500, 900, 1.1);
  const u = eo(seg(twos(lt), 1.9, 2.5));
  const happy = lt > 2.85;
  dadMCU(g, 600, 1080, 1.05, { face: happy ? { eyes: 'happy', mouth: 'smile' } : { lx: -0.7, ly: 0.2, mouth: 'smile', blink: blinkAt(t) }, kulfi: u, headRot: -0.04 });
  if (u > 0.9) sparkle(g, 330, 880, 30 * (0.6 + 0.4 * Math.sin(lt * 10)));
});
// 18 · wonder close-up: the kulfi glows golden in his imagination, then the first bite
add((g, t, lt) => {
  livingRoom(g, 0, {}); glow(g, 540, 1100, 660, 0.85);
  const gold = eio(seg(lt, 1.55, 2.15)) * (1 - eio(seg(lt, 3.65, 4.25)));
  const bit = twos(lt) >= 4.87;
  const f = bit ? { eyes: 'happy', mouth: 'bite', brow: 'up' } : { lx: 0.25, ly: 0.75, eyes: 'wide', mouth: 'o', brow: 'up', blink: blinkAt(t) };
  // shirt and shoulders
  ink(g, shape([[60, 1920], [120, 1640], [320, 1520], [760, 1520], [960, 1640], [1020, 1920]]), C.red, [60, 1520, 1020, 1920], { sh: 'rgba(90,20,15,0.32)' });
  kidHead(g, 520, 1100, 330, f, -0.04);
  if (bit) { blush(g, 330, 1260, 110, 0.35); blush(g, 710, 1260, 110, 0.35); }
  const kx = 790, ky = 1430;
  if (gold > 0) glow(g, kx, ky - 60, 260 * gold, 0.9 * gold, [255, 214, 90]);
  kulfi(g, kx, ky, 1.2, 0.25, { bitten: bit, gold, drip: bit ? seg(lt, 5.4, 6.4) : 0 });
  kidHand(g, kx + 30, ky + 150, 1.6, 'fist', 0.2);
  if (gold > 0.2) { sparkle(g, kx - 120, ky - 220, 40 * gold); sparkle(g, kx + 110, ky - 160, 30 * gold); sparkle(g, kx - 40, ky - 300, 24 * gold); }
  if (bit) { sparkle(g, 300, 900, 26 * (0.5 + 0.5 * Math.sin(lt * 9))); }
});
// 19 · end card
function endCard(g, t, lt) {
  g.drawImage(PAPER, 0, 0);
  const q = rng(19);
  for (let i = 0; i < 26; i++) { const x = 120 + q() * 840, y = 560 + q() * 900, r = 3 + q() * 6; g.fillStyle = i % 3 ? 'rgba(232,160,70,0.8)' : 'rgba(138,160,72,0.8)'; g.beginPath(); g.ellipse(x, y, r, r * 0.7, q() * 3, 0, TAU); g.fill(); }
  for (const [x, y, r, s] of [[300, 700, -0.5, 1.15], [560, 640, 0.15, 1.05], [800, 760, 0.55, 1.15], [250, 1350, -0.9, 1.1]]) {
    g.save(); g.shadowColor = 'rgba(120,80,40,0.3)'; g.shadowBlur = 24; g.shadowOffsetY = 12; kulfi(g, x, y, s, r, {}); g.restore();
  }
  for (const [x, y, ph] of [[420, 610, 0], [700, 580, 2], [880, 900, 4], [380, 1300, 1]]) sparkle(g, x, y, 20 * (0.5 + 0.5 * Math.sin(lt * 6 + ph)));
  g.save(); g.textAlign = 'center'; g.textBaseline = 'alphabetic'; g.fillStyle = '#7A3E1E'; g.shadowColor = 'rgba(245,150,70,0.85)'; g.shadowBlur = 26;
  g.font = 'bold 84px "Courier Prime"'; g.fillText('forgotten', 540, 1000); g.fillText('little joys of life', 540, 1100);
  g.font = 'bold 46px "Courier Prime"'; g.fillText('( episode 2 )', 540, 1190); g.restore();
}

// ---------- the fixed POV caption (THEME.md section 6) ----------
function caption(g, a) {
  if (a <= 0) return;
  g.save(); g.globalAlpha = a; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillStyle = '#000'; g.fillRect(481, 324, 118, 89);
  g.fillStyle = '#fff'; g.font = '44px "Tinos"'; g.fillText('POV', 540, 370);
  g.font = '40px "Tinos"'; const l1 = 'you were your dads', l2 = 'tv remote';
  const w = Math.max(g.measureText(l1).width, g.measureText(l2).width) + 44;
  g.fillStyle = '#000'; g.fillRect(540 - w / 2, 424, w, 139);
  g.fillStyle = '#fff'; g.fillText(l1, 540, 470); g.fillText(l2, 540, 520);
  g.restore();
}

// ---------- compositing ----------
function shotIndex(t) { for (let i = 0; i < CUTS.length - 1; i++) if (t < CUTS[i + 1]) return i; return CUTS.length - 2; }
function drawShot(g, i, t) {
  g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.filter = 'none'; g.globalCompositeOperation = 'source-over';
  g.clearRect(0, 0, W, H);
  SH[i](g, t, t - CUTS[i]);
}
function storybook(target, src) {   // vignette onto paper, with paper grain on top
  cp.setTransform(1, 0, 0, 1, 0, 0); cp.globalCompositeOperation = 'source-over'; cp.clearRect(0, 0, W, H);
  cp.drawImage(src, 0, 0); cp.globalCompositeOperation = 'destination-in'; cp.drawImage(MASK, 0, 0); cp.globalCompositeOperation = 'source-over';
  target.drawImage(PAPER, 0, 0); target.drawImage(CP, 0, 0);
  target.save(); target.globalCompositeOperation = 'multiply'; target.globalAlpha = 0.35; target.drawImage(PAPER, 0, 0); target.restore();
}
function renderAt(t) {
  const f = Math.min(DUR * FPS - 1, Math.floor(t * FPS + 1e-6)); t = f / FPS;
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
  const i = shotIndex(t);
  if (i === 18) {   // end card, with a 0.5 s fade from the last shot
    const a = seg(t, CUTS[18], CUTS[18] + 0.5);
    if (a < 1) { drawShot(sx, 17, Math.min(t, CUTS[18] - 0.001)); storybook(ctx, SC); caption(ctx, 1 - a); }
    ctx.save(); ctx.globalAlpha = a; endCard(ctx, t, t - CUTS[18]); ctx.restore();
    return cv;
  }
  drawShot(sx, i, t);
  if (i === 9 && t < CUTS[9] + 3 / FPS) {   // 3-frame dissolve into the rooftop
    drawShot(sx2, 8, CUTS[9] - 0.001);
    const a = (t - CUTS[9] + 1 / FPS) / (4 / FPS);
    sx2.globalAlpha = a; sx2.drawImage(SC, 0, 0); sx2.globalAlpha = 1;
    storybook(ctx, SC2);
  } else storybook(ctx, SC);
  caption(ctx, 1);
  return cv;
}
window.SCENE = { W, H, FPS, DUR, CUTS, renderAt, canvas: cv };
window.readyP = (async () => {
  try { await Promise.all([document.fonts.load('44px "Tinos"'), document.fonts.load('36px "Patrick Hand"'), document.fonts.load('bold 84px "Courier Prime"')]); } catch (e) {}
  buildTextures();
})();
})();
