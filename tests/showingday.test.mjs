import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { followups, leaseFacts, csvSamples, summarizeCsv, initDemo } from '../assets/showingday-demo.js';

test('Showingday samples calculate exact cents, require review, reset and never connect accounts', async () => {
  assert.deepEqual(summarizeCsv(csvSamples.complete), {
    current: { in: 220030, out: 140000, net: 80030 },
    prior: { in: 210000, out: 120001, net: 89999 }, change: -9969
  });
  assert.deepEqual(summarizeCsv(csvSamples.missing), {
    current: { in: 220030, out: 140000, net: 80030 }, prior: null, change: null
  });
  for (const csv of [csvSamples.complete + '\nC1,2026-10-05,in,0.01', csvSamples.complete.replace('2200.20', '2200.2'), csvSamples.complete.replace(',in,', ',unknown,')]) assert.throws(() => summarizeCsv(csv));
  const script = await readFile(new URL('../assets/showingday-demo.js', import.meta.url), 'utf8');
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
  for (const page of ['index.html']) {
    const html = await readFile(new URL('../' + page, import.meta.url), 'utf8');
    assert.match(html, /type="module" src="\/assets\/showingday-demo.js"/);
    assert.match(html, /Interactive sample \/ fictional data/);
    assert.match(html, /data-sd-output aria-live="polite"/);
    assert.match(html, /href="\/contact(?:\?lang=es)?"/);
  }
});
