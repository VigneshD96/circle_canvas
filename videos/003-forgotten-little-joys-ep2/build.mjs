import fs from 'fs';
const here = new URL('.', import.meta.url).pathname, f = n => fs.readFileSync(here + 'src/fonts/' + n).toString('base64');
let html = fs.readFileSync(here + 'src/template.html', 'utf8');
const audio = fs.existsSync(here + 'audio/score.m4a') ? 'data:audio/mp4;base64,' + fs.readFileSync(here + 'audio/score.m4a').toString('base64') : '';
html = html.replace('__TINOS__', f('tinos-latin-400-normal.woff2')).replace('__PATRICK__', f('patrick-hand-latin-400-normal.woff2')).replace('__COURIER__', f('courier-prime-latin-700-normal.woff2'))
  .replace('__AUDIO__', audio).replace('__SCENE__', () => fs.readFileSync(here + 'src/scene.js', 'utf8'));
fs.writeFileSync(here + 'episode2.html', html); console.log('built', (html.length / 1024).toFixed(0), 'KB');
