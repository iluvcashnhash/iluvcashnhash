// Renders each orbit ring (scripts/build/rings.json) to a bitmap once, so the
// animated SVG rotates a few images instead of re-drawing ~1000 glyphs per frame.
// Usage: node scripts/raster_rings.mjs [scale] [format]   (needs Google Chrome)
import { spawn } from 'node:child_process';
import { readFileSync, writeFileSync } from 'node:fs';

const SCALE = Number(process.argv[2] || 2.5);
const FORMAT = process.argv[3] || 'image/webp';
const CHROME = process.env.CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const dir = new URL('./build/', import.meta.url);
const rings = JSON.parse(readFileSync(new URL('rings.json', dir)));

const port = 9334;
const chrome = spawn(CHROME, [`--remote-debugging-port=${port}`, '--headless=new',
  '--user-data-dir=/tmp/raster-rings-chrome', '--no-first-run', 'about:blank'], { stdio: 'ignore' });
try {
  let targets;
  for (let i = 0; i < 40 && !targets; i++) {
    await new Promise(r => setTimeout(r, 500));
    try { targets = await (await fetch(`http://127.0.0.1:${port}/json`)).json(); } catch {}
  }
  const ws = new WebSocket(targets.find(t => t.type === 'page').webSocketDebuggerUrl);
  await new Promise(r => (ws.onopen = r));
  let id = 0; const pend = {};
  ws.onmessage = e => { const m = JSON.parse(e.data); pend[m.id]?.(m); delete pend[m.id]; };
  const send = (method, params = {}) => new Promise(r => { pend[++id] = r; ws.send(JSON.stringify({ id, method, params })); });

  const fn = async (svg, scale, format) => {
    const img = new Image();
    img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
    await img.decode();
    const c = document.createElement('canvas');
    c.width = Math.round(img.width * scale); c.height = Math.round(img.height * scale);
    c.getContext('2d').drawImage(img, 0, 0, c.width, c.height);
    return c.toDataURL(format, 0.9);
  };
  const out = {};
  for (const [key, svg] of Object.entries(rings)) {
    const res = await send('Runtime.evaluate', {
      expression: `(${fn})(${JSON.stringify(svg)}, ${SCALE}, ${JSON.stringify(FORMAT)})`,
      awaitPromise: true, returnByValue: true,
    });
    out[key] = res.result.result.value;
    console.log(key, Math.round(out[key].length / 1024) + ' KB');
  }
  writeFileSync(new URL('rings.raster.json', dir), JSON.stringify(out));
} finally {
  chrome.kill();
}
