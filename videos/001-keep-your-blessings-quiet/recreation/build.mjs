import fs from 'fs';
const here = new URL('.', import.meta.url).pathname;
const font = fs.readFileSync(process.env.FONT || here + 'src/fonts/montserrat-latin-800-normal.woff2').toString('base64');
let html = fs.readFileSync(here + 'src/template.html', 'utf8');
html = html.replace('__FONT__', font).replace('__SCENE__', () => fs.readFileSync(here + 'src/scene.js', 'utf8'));
fs.writeFileSync(here + 'woman-walk.html', html);
console.log('built', (html.length / 1024).toFixed(0), 'KB');
