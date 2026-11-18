(() => {
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const ruler = document.querySelector('[data-ruler]');
  const links = [...ruler.querySelectorAll('[data-depth-link]')];
  const readouts = [...document.querySelectorAll('[data-readout]')];
  const sections = links.map(link => document.getElementById(link.hash.slice(1)));
  const isStucco = document.body.matches('.cover-page.edition-home');
  const numbers = ['0″', '1/8″', '1/4″', '3/8″', '1/2″', '5/8″', '3/4″', '7/8″'];
  let current = 0;
  let frame = 0;
  let anchorSelection;
  let anchorTarget;

  function markActive(index) {
    if (current === index) return;
    links[current].removeAttribute('aria-current');
    readouts[current].hidden = true;
    links[index].setAttribute('aria-current', 'location');
    readouts[index].hidden = false;
    ruler.style.setProperty('--active-row', index);
    current = index;
  }

  function updateDepth() {
    if (anchorSelection !== undefined && Math.abs(scrollY - anchorTarget) < 3) {
      markActive(anchorSelection);
    } else {
      const revealAt = innerHeight * .37;
      const next = sections.findLastIndex(section => section.getBoundingClientRect().top <= revealAt);
      markActive(Math.max(0, next));
    }
    if (!isStucco) return;
    const stops = [0, 1, 4, 7, 7, 7];
    let step = stops[current];
    if (!reducedMotion.matches && current < 3) {
      const from = sections[current].getBoundingClientRect().top - innerHeight * .37;
      const to = sections[current + 1].getBoundingClientRect().top - innerHeight * .37;
      const fraction = Math.min(1, Math.max(0, -from / (to - from)));
      step = Math.floor(step + fraction * (stops[current + 1] - step));
    }
    const number = readouts[current].querySelector('.readout-number');
    if (number.textContent !== numbers[step]) number.textContent = numbers[step];
  }

  const cuts = [...document.querySelectorAll('.cut')];
  const windows = [...document.querySelectorAll('.window-opening')];
  const visibleMotion = new Set();
  const nativePeel = CSS.supports('animation-timeline: view()');
  if (nativePeel) cuts.forEach(cut => cut.classList.add('css-peel'));
  const motionTargets = nativePeel ? windows : [...windows, ...cuts];
  const waterDiagram = document.querySelector('.water-diagram');

  function updateMotion() {
    if (reducedMotion.matches) return;
    for (const target of visibleMotion) {
      const box = target.getBoundingClientRect();
      if (target.classList.contains('cut')) {
        const position = Math.min(1, Math.max(0, (innerHeight - box.top) / innerHeight));
        target.style.setProperty('--cut-left', (85 - 63 * position).toFixed(1) + '%');
        target.style.setProperty('--cut-right', Math.max(0, 27 - 38 * position).toFixed(1) + '%');
      } else {
        const offset = (innerHeight / 2 - box.top - box.height / 2) * .018;
        target.style.setProperty('--window-drift', Math.min(8, Math.max(-8, offset)).toFixed(1) + 'px');
      }
    }
  }

  function update() {
    frame = 0;
    updateDepth();
    updateMotion();
  }

  function schedule() {
    if (!frame) frame = requestAnimationFrame(update);
  }

  function trackAnchor() {
    anchorSelection = links.findIndex(link => link.hash === location.hash);
    if (anchorSelection < 0) {
      anchorSelection = undefined;
      return;
    }
    const section = sections[anchorSelection];
    const margin = parseFloat(getComputedStyle(section).scrollMarginTop) || 0;
    const maxScroll = document.documentElement.scrollHeight - innerHeight;
    anchorTarget = Math.max(0, Math.min(maxScroll, scrollY + section.getBoundingClientRect().top - margin));
    schedule();
  }

  for (const [index, link] of links.entries()) {
    link.addEventListener('click', () => {
      markActive(index);
      if (link.hash === location.hash) trackAnchor();
    });
  }
  addEventListener('scroll', schedule, { passive: true });
  addEventListener('resize', schedule);
  addEventListener('hashchange', trackAnchor);
  document.addEventListener('wallder:language', schedule);
  reducedMotion.addEventListener('change', schedule);

  if ('IntersectionObserver' in window) {
    const motionObserver = new IntersectionObserver(entries => {
      for (const entry of entries) {
        if (entry.isIntersecting) visibleMotion.add(entry.target);
        else visibleMotion.delete(entry.target);
      }
      schedule();
    });
    motionTargets.forEach(target => motionObserver.observe(target));
    if (waterDiagram) {
      const waterObserver = new IntersectionObserver(([entry]) => {
        waterDiagram.classList.toggle('in-view', entry.isIntersecting);
      }, { threshold: .43 });
      waterObserver.observe(waterDiagram);
    }
  }
  trackAnchor();
  schedule();

  const scope = [...document.querySelectorAll('[data-scope-id]')];
  if (scope.length === 0) return;
  const storageKey = 'wallder-v2-scope-' + document.body.dataset.edition;
  let selected = new Set();
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey) ?? '[]');
    if (Array.isArray(saved)) selected = new Set(saved);
  } catch {}
  const picker = document.querySelector('.scope-picker');
  if (picker && scope.some(control => selected.has(control.value))) picker.open = true;
  for (const control of scope) {
    control.checked = selected.has(control.value);
    control.addEventListener('change', () => {
      if (control.checked) selected.add(control.value);
      else selected.delete(control.value);
      try { localStorage.setItem(storageKey, JSON.stringify([...selected])); } catch {}
    });
  }
})();
