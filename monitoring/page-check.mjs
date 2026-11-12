// Page check: load every page in a headless browser and fail if the site's own code breaks.
//
//   node monitoring/page-check.mjs [root]      (needs `playwright` installed; run in CI by lint.yml)
//
// Catches what a syntax check can't: a script that throws while the page loads (the sector
// Signals pages showed no picks for four months, #68), a local file that 404s, a page that
// scrolls sideways on a phone, the light/dark button pushed off-screen, a feed left empty.
//
// Outside sites are blocked on purpose, so a slow CDN can never fail a PR. The two libraries
// the pages load from outside (TradingView, d3) are then simply "not defined": expected, and
// ignored. Any other error fails.
import { chromium } from 'playwright';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(process.argv[2] || '.');
const EXTERNAL_GLOBALS = ['TradingView', 'd3'];
const FUNCTION_URLS = new Set(['/health']);   // Cloudflare Pages Functions: no file for a plain server to return
// shared.js tries prices.json first and falls back to the page's own table when it's missing (All, exports)
const OPTIONAL = [/\/prices\.json$/];
const SKIP_DIRS = new Set(['.git', 'node_modules', 'mockups', '.wrangler', 'functions']);
const SKIP_FILES = new Set(['mockup.html', 'market.html']); // market.html is a redirect

const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.css': 'text/css',
  '.csv': 'text/csv', '.svg': 'image/svg+xml', '.png': 'image/png', '.ico': 'image/x-icon' };

// Things a page must have drawn by the time it has loaded (page-specific, kept deliberately small).
const MUST_RENDER = [
  [/^All\/signals\.html$/, '#signals-root', 'the signal picks'],
  [/\/signals\.html$/, '#signals-feed', 'the signal picks'],
  [/^track-record\.html$/, '.verdict-card', 'the verdict cards'],
];

function pages(dir = ROOT, out = []) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (e.isDirectory()) { if (!SKIP_DIRS.has(e.name)) pages(path.join(dir, e.name), out); }
    else if (e.name.endsWith('.html') && !SKIP_FILES.has(e.name)) out.push(path.relative(ROOT, path.join(dir, e.name)));
  }
  return out.sort();
}

function serve() {
  return new Promise(resolve => {
    const server = http.createServer((req, res) => {
      let p = decodeURIComponent(req.url.split('?')[0]);
      if (p.endsWith('/')) p += 'index.html';
      const file = path.join(ROOT, p);
      if (!file.startsWith(ROOT) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); return res.end('not found'); }
      res.writeHead(200, { 'content-type': TYPES[path.extname(file)] || 'application/octet-stream', 'cache-control': 'no-store' });
      fs.createReadStream(file).pipe(res);
    }).listen(0, '127.0.0.1', () => resolve({ server, base: `http://127.0.0.1:${server.address().port}/` }));
  });
}

const { server, base } = await serve();
const browser = await chromium.launch();
const list = pages();
const failures = [];
const fail = (page, msg) => failures.push(`${page}: ${msg}`);

for (const [label, width] of [['desktop', 1440], ['phone', 390]]) {
  const ctx = await browser.newContext({ viewport: { width, height: 900 } });
  await ctx.route(url => !url.href.startsWith(base), r => r.abort());   // outside sites: blocked
  for (const p of list) {
    const page = await ctx.newPage();
    const tag = `${p} (${label})`;
    page.on('pageerror', e => {
      const ext = EXTERNAL_GLOBALS.some(g => e.message.startsWith(`${g} is not defined`));
      if (!ext) fail(tag, `script error: ${e.message}`);
    });
    page.on('response', r => { if (r.url().startsWith(base) && r.status() >= 400 && !FUNCTION_URLS.has(new URL(r.url()).pathname) && !OPTIONAL.some(re => re.test(new URL(r.url()).pathname))) fail(tag, `${r.status()} for ${r.url().slice(base.length - 1)}`); });
    await page.goto(base + p, { waitUntil: 'load' });
    await page.waitForTimeout(500);
    const r = await page.evaluate(() => {
      const toggle = [...document.querySelectorAll('.theme-toggle')].find(e => e.offsetParent !== null);
      return { sw: document.documentElement.scrollWidth, w: window.innerWidth, toggleRight: toggle ? Math.round(toggle.getBoundingClientRect().right) : null };
    });
    if (width <= 600) {
      if (r.sw > r.w) fail(tag, `scrolls sideways (${r.sw - r.w}px too wide)`);
      if (r.toggleRight !== null && r.toggleRight > r.w) fail(tag, `light/dark button is off-screen (right edge ${r.toggleRight}px, screen ${r.w}px)`);
    }
    if (label === 'desktop') {
      for (const [re, sel, what] of MUST_RENDER) {
        if (!re.test(p)) continue;
        const n = await page.evaluate(s => { const e = document.querySelector(s); return e ? e.innerText.trim().length + e.querySelectorAll('*').length : -1; }, sel);
        if (n <= 0) fail(tag, `${what} did not render (${sel} is empty or missing)`);
        break;   // first matching rule only
      }
    }
    await page.close();
  }
  await ctx.close();
}

await browser.close();
server.close();
console.log(`Page check: ${list.length} pages × 2 sizes, ${failures.length} problem(s)`);
for (const f of failures) console.log('  FAIL ' + f);
process.exit(failures.length ? 1 : 0);
