// Run from ~/agent-care-app with this site served at http://127.0.0.1:8877.
const assert = require('node:assert/strict');
const { chromium } = require('playwright');

const base = process.env.SITE_URL || 'http://127.0.0.1:8877';
const pages = ['/', '/contact.html', '/about.html', '/es/', '/agent/', '/assistant/'];
const landingPages = ['/agent/', '/assistant/'];
const promoLine = 'Free setup when you book from this page, through November 10, 2026.';

async function visibleCopy(page) {
  const costFaq = page.locator('details').filter({ has: page.locator('summary', { hasText: 'What does it cost all-in?' }) });
  if (await costFaq.count()) await costFaq.evaluate(element => { element.open = true; });
  return page.locator('body').innerText();
}

async function checkStandard(page, path) {
  await page.goto(base + path, { waitUntil: 'domcontentloaded' });
  const copy = await visibleCopy(page);
  assert.match(copy, /\$400/, `${path}: standard price missing`);
  for (const price of ['$149', '$249', '$399']) assert.ok(copy.includes(price), `${path}: ${price} missing`);
  assert.doesNotMatch(copy, /DigitalOcean|\$24\b|\$10 to \$20|\$133\b|\$148\b|\$233\b|\$248\b|\$383\b|\$398\b|\$99\b|\$199\b|\$349\b/i, `${path}: old pricing or account copy remains`);
  assert.doesNotMatch(copy, /Free setup/i, `${path}: promo shown to a standard visitor`);
  return copy;
}

async function main() {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  try {
    const stubExternal = async context => context.route('**/*', route => {
      const url = route.request().url();
      if (url.startsWith(base)) return route.continue();
      if (url.includes('assets.calendly.com/assets/external/widget.js')) {
        return route.fulfill({ contentType: 'text/javascript', body: 'window.Calendly={initInlineWidget:({parentElement})=>{parentElement.dataset.widgetReady="yes"}};' });
      }
      return route.fulfill({ status: 200, body: '' });
    });

    for (const width of [390, 1280]) {
      const context = await browser.newContext({ viewport: { width, height: 850 }, reducedMotion: 'reduce' });
      await stubExternal(context);
      const page = await context.newPage();
      for (const path of pages) {
        await checkStandard(page, path);
        const overflow = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
        assert.ok(overflow <= 1, `${path} at ${width}px overflows by ${overflow}px`);
        await page.screenshot({ path: `/private/tmp/agent-care-${path === '/' ? 'home' : path.replaceAll('/', '_')}-${width}.png`, fullPage: true });
        console.log(`PASS ${width}px ${path}: standard copy and no horizontal overflow`);
      }
      await context.close();
    }

    for (const width of [390, 1280]) for (const path of landingPages) {
      const context = await browser.newContext({ viewport: { width, height: 850 }, reducedMotion: 'reduce' });
      await stubExternal(context);
      const page = await context.newPage();
      await page.goto(base + path + '?utm_source=google&utm_medium=cpc&utm_campaign=x', { waitUntil: 'domcontentloaded' });
      let copy = await visibleCopy(page);
      assert.ok(copy.includes(promoLine), `${path}: promo missing`);
      assert.doesNotMatch(copy, /\$400/, `${path}: standard price shown in promo mode`);
      for (const price of ['$149', '$249', '$399']) assert.ok(copy.includes(price), `${path}: ${price} missing`);
      assert.equal(await page.evaluate(() => localStorage.getItem('ac_promo')), '1');
      await page.goto(base + path, { waitUntil: 'domcontentloaded' });
      copy = await visibleCopy(page);
      assert.ok(copy.includes(promoLine), `${path}: returning promo missing`);
      assert.doesNotMatch(copy, /\$400/, `${path}: returning standard price shown`);

      await page.locator('.agent-hero .booking-link').click();
      assert.equal(await page.locator('#booking').isVisible(), true);
      await page.waitForFunction(() => document.querySelector('#calendly-inline').dataset.widgetReady === 'yes');
      assert.ok(await page.evaluate(() => dataLayer.some(args => args[0] === 'event' && args[1] === 'agent_care_booking_cta_click')));
      await page.evaluate(() => dispatchEvent(new MessageEvent('message', { origin: 'https://calendly.com', data: { event: 'calendly.event_scheduled' } })));
      assert.ok(await page.evaluate(() => dataLayer.some(args => args[0] === 'event' && args[1] === 'conversion' && args[2].send_to === 'AW-18240559803/R_epCO2X4I0dELu14_lD')));
      await page.waitForURL(base + path + 'thanks/');
      console.log(`PASS ${width}px ${path}: ad promo, persistence, booking, conversion, thanks redirect`);
      await context.close();
    }

    for (const marker of ['gclid=x', 'gbraid=x', 'wbraid=x']) {
      const context = await browser.newContext();
      await stubExternal(context);
      const page = await context.newPage();
      await page.goto(base + '/agent/?' + marker);
      assert.ok((await visibleCopy(page)).includes(promoLine), `${marker}: promo missing`);
      await page.goto(base + '/assistant/');
      assert.ok((await visibleCopy(page)).includes(promoLine), `${marker}: promo did not persist across pages`);
      await context.close();
    }
    console.log('PASS gclid, gbraid, wbraid: promo persists across landing pages');

    const organic = await browser.newContext();
    await stubExternal(organic);
    await checkStandard(await organic.newPage(), '/agent/?utm_source=google&utm_medium=organic');
    await organic.close();
    console.log('PASS Google organic visit: standard price');

    const noJs = await browser.newContext({ javaScriptEnabled: false });
    const noJsPage = await noJs.newPage();
    for (const path of landingPages) await checkStandard(noJsPage, path);
    console.log('PASS no JavaScript: standard price on both landing pages');
    await noJs.close();

    const expired = await browser.newContext();
    await expired.addInitScript(() => { Date.now = () => new Date('2026-11-11T00:00:00-05:00').getTime(); });
    await stubExternal(expired);
    const expiredPage = await expired.newPage();
    await expiredPage.goto(base + '/agent/');
    await expiredPage.evaluate(() => localStorage.setItem('ac_promo', '1'));
    await checkStandard(expiredPage, '/agent/?gclid=test');
    assert.equal(await expiredPage.evaluate(() => localStorage.getItem('ac_promo')), null);
    console.log('PASS after deadline: ad tag and saved promo show standard price');
    await expired.close();
  } finally {
    await browser.close();
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
