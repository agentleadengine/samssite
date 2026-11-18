(() => {
  const mark = document.querySelector('[data-mark]');
  const button = mark.querySelector('button');
  const caption = document.querySelector('#mark-caption');
  const counter = document.querySelector('[data-count]');
  const { edition, folio } = document.body.dataset;
  const key = 'wallder-issue-marks-' + edition;
  let found = new Set();

  function savedMarks() {
    try {
      const saved = JSON.parse(localStorage.getItem(key) ?? '[]');
      return Array.isArray(saved) ? saved.filter(value => /^[0-4]$/.test(value)) : [];
    } catch {
      return [];
    }
  }

  function updateCount() {
    for (const text of counter.querySelectorAll('[data-template]')) {
      text.textContent = text.dataset.template.replace('{count}', found.size);
    }
  }

  function show() {
    for (const value of savedMarks()) found.add(String(value));
    found.add(folio);
    try { localStorage.setItem(key, JSON.stringify([...found])); } catch {}
    updateCount();
    caption.hidden = false;
    button.setAttribute('aria-expanded', 'true');
  }

  function hide() {
    caption.hidden = true;
    button.setAttribute('aria-expanded', 'false');
  }

  function sync() {
    found = new Set([...found, ...savedMarks().map(String)]);
    updateCount();
  }

  button.addEventListener('pointerenter', event => {
    if (event.pointerType === 'mouse') show();
  });
  mark.addEventListener('pointerleave', event => {
    if (event.pointerType === 'mouse') hide();
  });
  button.addEventListener('click', event => {
    if (event.pointerType === 'mouse' || caption.hidden) show();
    else hide();
  });
  button.addEventListener('keydown', event => {
    if (event.key === 'Escape') hide();
  });
  window.addEventListener('storage', event => {
    if (event.key === key) {
      found = new Set(savedMarks().map(String));
      updateCount();
    }
  });
  window.addEventListener('pageshow', sync);
  sync();

  if (matchMedia('(prefers-reduced-motion: no-preference)').matches) {
    window.addEventListener('pagereveal', event => {
      if (event.viewTransition) document.body.classList.add('turn-arrived');
    });

    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver(entries => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue;
          entry.target.classList.add('revealing');
          observer.unobserve(entry.target);
        }
      }, { threshold: 0.08 });
      document.querySelectorAll('[data-reveal]').forEach(section => observer.observe(section));
    }
  }

  const coverBar = document.querySelector('.cover-action');
  document.addEventListener('focusin', event => {
    const target = event.target;
    if (target.closest('.cover-action') || !target.matches(':focus-visible')) return;

    requestAnimationFrame(() => {
      if (target !== document.activeElement) return;
      const limit = coverBar && getComputedStyle(coverBar).position === 'fixed'
        ? coverBar.getBoundingClientRect().top
        : window.innerHeight;
      const box = target.getBoundingClientRect();
      const clearance = 10;
      if (box.top < clearance) window.scrollBy(0, box.top - clearance);
      else if (box.bottom > limit - clearance) window.scrollBy(0, box.bottom - limit + clearance);
    });
  });
})();
