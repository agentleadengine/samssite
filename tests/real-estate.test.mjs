import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { followups, leaseFacts, csvSamples, summarizeCsv, initDemo } from '../assets/real-estate-demo.js';

test('QUEVA for Real Estate samples calculate exact cents, require review, reset and never connect accounts', async () => {
  assert.deepEqual(summarizeCsv(csvSamples.complete), {
    current: { in: 220030, out: 140000, net: 80030 },
    prior: { in: 210000, out: 120001, net: 89999 }, change: -9969
  });
  assert.deepEqual(summarizeCsv(csvSamples.missing), {
    current: { in: 220030, out: 140000, net: 80030 }, prior: null, change: null
  });
  for (const csv of [csvSamples.complete + '\nC1,2026-10-05,in,0.01', csvSamples.complete.replace('2200.20', '2200.2'), csvSamples.complete.replace(',in,', ',unknown,')]) assert.throws(() => summarizeCsv(csv));
  const script = await readFile(new URL('../assets/real-estate-demo.js', import.meta.url), 'utf8');
  assert.doesNotMatch(script, /fetch\(|XMLHttpRequest|localStorage|sessionStorage|sendBeacon|https?:/);
  for (const type of ['followup', 'lease', 'money']) {
    // Minimal controls exercise the actual click handlers; browser acceptance is separate.
    const elements = new Map();
    const root = { dataset: { sdDemo: type }, querySelector(selector) {
      if (!elements.has(selector)) elements.set(selector, { value: type === 'money' ? 'complete' : '0', textContent: '', disabled: false, listeners: {}, addEventListener(event, fn) { this.listeners[event] = fn; }, set selectedIndex(index) { this.value = type === 'money' ? 'complete' : String(index); } });
      return elements.get(selector);
    } };
    const button = (action) => root.querySelector(`[data-sd-action="${action}"]`);
    const click = (action) => button(action).listeners.click();
    const output = () => root.querySelector('[data-sd-output]').textContent;
    const status = () => root.querySelector('[data-sd-status]').textContent;
    initDemo(root);
    click('approve'); assert.match(status(), /^Ready/);
    click('review'); assert.match(status(), /^Ready/);
    const choices = type === 'followup' ? ['0', '1', '2'] : type === 'money' ? ['complete', 'missing'] : ['0'];
    for (const value of choices) {
      const select = root.querySelector('[data-sd-choice]'); select.value = value; select.listeners.change();
      assert.equal(button('approve').disabled, true);
      click('prepare'); assert.equal(button('review').disabled, false);
      if (type === 'followup') {
        assert.ok(output().includes(followups[Number(value)].draft));
        assert.ok(output().includes(followups[Number(value)].task));
        assert.ok(output().includes(followups[Number(value)].note));
      } else if (type === 'lease') {
        assert.ok(output().includes(leaseFacts)); assert.match(output(), /Signature: left blank/);
      } else {
        assert.match(output(), /Money in: \$2,200\.30/); assert.match(output(), /Net cash: \$800\.30/);
        assert.match(output(), value === 'complete' ? /decreased by \$99\.69/ : /Prior week: unknown/);
        assert.equal(output().includes('$899.99'), value === 'complete');
      }
      click('approve'); assert.match(status(), /^Sample prepared/);
      click('review'); assert.equal(button('approve').disabled, false); assert.match(status(), /^Review:/);
      click('approve'); assert.match(status(), /^Approved sample\. Simulation only/);
      assert.equal(button('approve').disabled, true);
      select.listeners.change(); assert.match(status(), /^Ready/); assert.equal(button('approve').disabled, true);
      click('prepare'); click('review'); click('approve'); click('reset');
      assert.match(status(), /^Ready/); assert.equal(button('prepare').disabled, false);
      assert.equal(output(), 'Your sample preview will appear here.');
    }
  }
  for (const page of ['index.html', 'real-estate.html']) {
    const html = await readFile(new URL('../' + page, import.meta.url), 'utf8');
    assert.match(html, /type="module" src="\/assets\/real-estate-demo.js"/);
    assert.match(html, /Interactive sample \/ fictional data/);
    assert.match(html, /data-sd-output aria-live="polite"/);
    assert.match(html, /href="\/contact(?:\?lang=es)?"/);
  }
});


test('focused landing keeps its demo CTA, metadata, commercial terms and accessible sample controls', async () => {
  const html = await readFile(new URL('../real-estate.html', import.meta.url), 'utf8');
  const home = await readFile(new URL('../index.html', import.meta.url), 'utf8');
  const canonical = html.match(/rel="canonical" href="([^"]+)"/)[1];
  assert.match(canonical, /^https:\/\/(agentleadengine|samuelochoa)\.com\/real-estate$/);
  assert.ok(html.includes(`property="og:url" content="${canonical}"`));
  for (const pattern of [/<title>([^<]+)<\/title>/, /name="description" content="([^"]+)"/, /property="og:title" content="([^"]+)"/, /property="og:description" content="([^"]+)"/]) {
    assert.notEqual(html.match(pattern)?.[1], home.match(pattern)?.[1]);
  }
  assert.equal([...html.matchAll(/<h1\b/g)].length, 1);
  assert.equal([...html.matchAll(/<main\b/g)].length, 1);
  assert.doesNotMatch(html, /<link[^>]+hreflang=|response commitment|not a free.month|\u2014/i);
  const header = html.match(/<header\b[\s\S]*?<\/header>/)[0];
  assert.match(header, /class="brand" href="\/"/);
  assert.match(header, /<img src="\/logo.png" alt="" width="32" height="32"><span>Samuel Ochoa<\/span>/);
  assert.ok(html.includes('<h1 id="hero-title">I set up and run QUEVA for real estate agents.</h1>'));
  assert.match(html, /supported tasks agreed during setup/);
  assert.match(html, /confirms? what QUEVA can do in your account/);
  assert.doesNotMatch(html, /without adding to your assistant|Keep follow-ups moving|Delegate with a clear view|Bring one task you want help with/);
  assert.equal([...header.matchAll(/<a\b/g)].length, 2);
  const ctas = [...html.matchAll(/<a\b[^>]*href="([^"]+)"[^>]*>Request a demo<\/a>/g)];
  assert.equal(ctas.length, 3);
  assert.ok(ctas.every((match) => match[1] === '/contact'));
  for (const phrase of ['Illustrative example', 'fictional data', 'proposed CRM task and note', 'simulated approvals', 'nothing is sent or saved', 'account access', 'permissions', 'Unlimited support requests when something we set up breaks', 'Every day, 9 AM–9 PM Eastern', 'Response within two support hours', '$125/hour', '15-minute increments ($31.25)', 'monthly price and allowance are agreed before starting', 'no five-hour caps', 'no usage limits for their first 30 days', 'Monthly limits apply afterward']) assert.ok(html.includes(phrase), phrase);
  const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map((match) => match[1]);
  assert.equal(new Set(ids).size, ids.length);
  for (const [, id] of html.matchAll(/href="#([^"]+)"/g)) assert.ok(ids.includes(id), id);
  const demos = [...html.matchAll(/<article class="sd-demo" data-sd-demo="(\w+)"[\s\S]*?<\/article>/g)];
  assert.deepEqual(demos.map((match) => match[1]), ['followup', 'lease', 'money']);
  for (const [markup] of demos) {
    assert.match(markup, /Interactive sample \/ fictional data/);
    assert.match(markup, /data-sd-output aria-live="polite"/);
    assert.match(markup, /data-sd-status role="status"/);
    assert.match(markup, /<noscript>/);
    for (const action of ['prepare', 'review', 'approve', 'reset']) {
      const button = markup.match(new RegExp(`<button type="button" data-sd-action="${action}"([^>]*)>`));
      assert.ok(button, action);
      assert.equal(button[1].includes('disabled'), ['review', 'approve'].includes(action));
    }
  }
  assert.match(html, /<details><summary>Paperwork from facts you supply[\s\S]*?id="lease"[\s\S]*?<\/details>/);
  assert.match(html, /<details><summary>Weekly cash summary[\s\S]*?id="money"[\s\S]*?value="missing"[\s\S]*?<\/details>/);
  const css = await readFile(new URL('../assets/queva-landing.css', import.meta.url), 'utf8');
  assert.match(css, /:focus-visible/);
  assert.match(css, /prefers-reduced-motion/);
  assert.doesNotMatch(css, /gradient|@import|@keyframes/);
});
