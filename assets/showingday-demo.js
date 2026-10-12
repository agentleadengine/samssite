// Fixed fictional examples. No account connections, storage or network calls.
export const followups = [
  {
    context: 'Open house: Maya Chen visited 18 Willow Lane on Sunday. She liked the garden and asked about a second visit on Thursday.',
    draft: 'Hi Maya, thanks for visiting 18 Willow Lane on Sunday. You mentioned the garden and a possible second visit on Thursday. What time would suit you? I can check availability.',
    task: 'Proposed CRM task: Check Thursday showing availability for Maya Chen.',
    note: 'Proposed CRM note: Open-house visitor; interested in the garden; requested a possible Thursday visit.'
  },
  {
    context: 'CRM note: Jordan Ellis asked for two-bedroom homes under $450,000 near a train station. No properties have been selected yet.',
    draft: 'Hi Jordan, I have your two-bedroom search under $450,000 near a train station noted. Which stations would work best for you? That will help me narrow the search.',
    task: 'Proposed CRM task: Confirm preferred train stations with Jordan Ellis.',
    note: 'Proposed CRM note: Two bedrooms; budget under $450,000; station preferences still needed.'
  },
  {
    context: 'CRM note: Alex Rivera is considering selling a condo this spring and asked what to prepare before a first conversation. No valuation has been provided.',
    draft: 'Hi Alex, you mentioned possibly selling your condo this spring. For our first conversation, it would help to know your timing and any recent updates to the home. When would you like to talk?',
    task: 'Proposed CRM task: Arrange a first conversation with Alex Rivera.',
    note: 'Proposed CRM note: Considering a spring sale; timing and home updates to confirm; no valuation provided.'
  }
];

export const leaseFacts = 'Tenant: Taylor Morgan\nProperty: 24 Sample Street, Unit 2\nMonthly rent: $1,800.00\nStart date: November 1, 2026';
const currentRows = 'C1,2026-10-05,in,2200.20\nC2,2026-10-05,in,0.10\nC3,2026-10-05,out,1200.00\nC4,2026-10-05,out,200.00';
export const csvSamples = {
  complete: `row,week,direction,amount_usd\n${currentRows}\nP1,2026-09-28,in,2100.00\nP2,2026-09-28,out,1200.01`,
  missing: `row,week,direction,amount_usd\n${currentRows}`
};

export function summarizeCsv(csv) {
  const [header, ...rows] = csv.trim().split('\n');
  if (header !== 'row,week,direction,amount_usd') throw new Error('Unexpected sample columns');
  const weeks = new Map(), ids = new Set();
  // These authored CSV samples have four unquoted columns; this is not an upload parser.
  for (const row of rows) {
    const [id, week, direction, amount, extra] = row.split(',');
    if (!id || ids.has(id) || !['2026-10-05', '2026-09-28'].includes(week) || !['in', 'out'].includes(direction) || !/^\d{1,7}\.\d{2}$/.test(amount) || extra !== undefined) throw new Error('Invalid sample row');
    ids.add(id);
    const [dollars, cents] = amount.split('.');
    const total = weeks.get(week) || { in: 0, out: 0, net: 0 };
    total[direction] += Number(dollars) * 100 + Number(cents);
    total.net = total.in - total.out;
    weeks.set(week, total);
  }
  const current = weeks.get('2026-10-05');
  if (!current) throw new Error('Current week is missing');
  const prior = weeks.get('2026-09-28') || null;
  return { current, prior, change: prior ? current.net - prior.net : null };
}

const dollars = (cents) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(cents / 100);

export function initDemo(root) {
  const type = root.dataset.sdDemo;
  const choice = root.querySelector('[data-sd-choice]');
  const source = root.querySelector('[data-sd-source]');
  const output = root.querySelector('[data-sd-output]');
  const status = root.querySelector('[data-sd-status]');
  const buttons = Object.fromEntries(['prepare', 'review', 'approve', 'reset'].map((action) => [action, root.querySelector(`[data-sd-action="${action}"]`)]));
  let stage = 'ready';
  const updateButtons = () => {
    buttons.review.disabled = stage !== 'prepared';
    buttons.approve.disabled = stage !== 'reviewed';
    buttons.prepare.disabled = stage !== 'ready';
  };
  function reset() {
    stage = 'ready';
    source.textContent = type === 'followup' ? followups[Number(choice.value)].context : type === 'lease' ? leaseFacts : csvSamples[choice.value];
    output.textContent = 'Your sample preview will appear here.';
    status.textContent = 'Ready. Prepare the sample, then review it.';
    updateButtons();
  }
  buttons.prepare.addEventListener('click', () => {
    if (stage !== 'ready') return;
    if (type === 'followup') {
      const item = followups[Number(choice.value)];
      output.textContent = `Draft for your review\n\n${item.draft}\n\n${item.task}\n${item.note}`;
    } else if (type === 'lease') {
      output.textContent = `Owner-template preview\n\n${leaseFacts}\n\nSignature: left blank\nSample template; signing/delivery not included in this preview.`;
    } else {
      const { current, prior, change } = summarizeCsv(csvSamples[choice.value]);
      output.textContent = `October 5–11, 2026\nMoney in: ${dollars(current.in)} (C1 + C2)\nMoney out: ${dollars(current.out)} (C3 + C4)\nNet cash: ${dollars(current.net)}\n\n${prior ? `September 28–October 4 net: ${dollars(prior.net)} (P1 − P2)\nNet cash ${change < 0 ? 'decreased' : 'increased'} by ${dollars(Math.abs(change))}.` : 'Prior week: unknown. No prior-week rows were supplied, so no comparison is available.'}\n\nCash movement, not revenue or profit. Sample coverage is declared complete for each included week.`;
    }
    stage = 'prepared';
    status.textContent = 'Sample prepared. Review the preview and its source facts before approving.';
    updateButtons();
  });
  buttons.review.addEventListener('click', () => {
    if (stage !== 'prepared') return;
    stage = 'reviewed';
    status.textContent = type === 'lease' ? 'Review: tenant, property, rent and start date are shown above. Signature stays blank. Approve this sample preview when checked.' : type === 'followup' ? 'Review: check the draft, proposed CRM task and note against the source context. Approve the sample action when checked.' : 'Review: check the row references, totals and prior-week coverage above. Approve the sample summary when checked.';
    updateButtons();
  });
  buttons.approve.addEventListener('click', () => {
    if (stage !== 'reviewed') return;
    stage = 'approved';
    status.textContent = 'Approved sample. Simulation only: nothing sent, signed, saved to a CRM or entered in any books. Reset to try again.';
    updateButtons();
  });
  buttons.reset.addEventListener('click', () => {
    if (choice) choice.selectedIndex = 0;
    reset();
  });
  choice?.addEventListener('change', reset);
  reset();
}

if (typeof document !== 'undefined') document.querySelectorAll('[data-sd-demo]').forEach(initDemo);
