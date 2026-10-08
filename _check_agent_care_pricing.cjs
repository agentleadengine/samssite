// Checks the core pages: one price line, no retired wording, no horizontal scroll.
// Run with any node_modules that has playwright, e.g.
//   NODE_PATH=~/content-os-web/node_modules SITE_URL=https://<draft>.netlify.app node _check_agent_care_pricing.cjs
// SITE_URL can be a local static server too (then pass .html paths with PAGES_HTML=1).
const assert = require('node:assert/strict');
const { chromium } = require('playwright');

const base = process.env.SITE_URL || 'http://127.0.0.1:8877';
const html = process.env.PAGES_HTML === '1';
const PRICE = 'Setup $400 one time. Then Care $99, Managed $199 or Full Service $349 a month. Provider costs are included. 30-day money back.';
const pages = ['/', '/agent/', '/queva/', html ? '/work.html' : '/work', html ? '/about.html' : '/about',
  html ? '/contact.html' : '/contact', html ? '/now.html' : '/now', '/es/', html ? '/testimonials.html' : '/testimonials'];
const withPrice = new Set(['/', '/agent/', '/queva/', '/work', '/work.html', '/contact', '/contact.html']);
const banned = [/free setup/i, /720 support minutes/i, /provider funding/i, /plus about \$/i, /DigitalOcean/, /\u2014/, /Group classes/i];

(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  try {
    for (const width of [390, 1280]) {
      const page = await browser.newPage({ viewport: { width, height: 850 } });
      for (const path of pages) {
        const res = await page.goto(base + path, { waitUntil: 'domcontentloaded' });
        assert.equal(res.status(), 200, `${path}: status ${res.status()}`);
        await page.$$eval('details', ds => ds.forEach(d => { d.open = true; }));
        const copy = await page.locator('body').innerText();
        if (withPrice.has(path)) assert.ok(copy.includes(PRICE), `${path}: price line missing`);
        for (const re of banned) assert.doesNotMatch(copy, re, `${path}: retired wording ${re}`);
        const overflow = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
        assert.ok(overflow <= 1, `${path} at ${width}px overflows by ${overflow}px`);
        console.log(`PASS ${width}px ${path}`);
      }
      await page.close();
    }
  } finally {
    await browser.close();
  }
})().catch(err => { console.error(err.message); process.exit(1); });
