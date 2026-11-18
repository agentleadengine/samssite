(() => {
  const root = document.documentElement;
  const storageKey = 'wallder-scope-' + document.body.dataset.edition;
  const townKey = 'wallder-home-town';
  const checks = [...document.querySelectorAll('[data-scope-id]')];
  const counts = [...document.querySelectorAll('[data-scope-count]')];
  const summaries = [...document.querySelectorAll('[data-summary-id]')];
  const empty = document.querySelector('[data-scope-empty]');
  const list = document.querySelector('[data-scope-summary]');
  const townControl = document.querySelector('[data-town-store]');
  const formTown = document.querySelector('[data-town-input]');
  const motion = window.matchMedia('(prefers-reduced-motion: no-preference)');

  function stored(key) {
    try { return localStorage.getItem(key); } catch { return null; }
  }

  function save(key, value) {
    try { localStorage.setItem(key, value); } catch {}
  }

  function readScope(value) {
    try {
      const scope = JSON.parse(value);
      return new Set(Array.isArray(scope) ? scope.filter(item => typeof item === 'string') : []);
    } catch { return new Set(); }
  }

  let scope = readScope(stored(storageKey));

  function update(animate = false) {
    for (const check of checks) check.checked = scope.has(check.dataset.scopeId);
    for (const count of counts) {
      for (const text of count.querySelectorAll('[data-i18n]')) {
        const word = scope.size === 1 ? 'One' : 'Many';
        text.textContent = count.dataset[text.lang + word].replace('{count}', scope.size);
      }
      if (animate && motion.matches) {
        count.classList.remove('pulse');
        void count.offsetWidth;
        count.classList.add('pulse');
      }
    }
    for (const item of summaries) item.hidden = !scope.has(item.dataset.summaryId);
    if (empty) empty.hidden = scope.size > 0;
    if (list) list.hidden = scope.size === 0;
  }

  for (const check of checks) {
    check.addEventListener('change', () => {
      if (check.checked) scope.add(check.dataset.scopeId);
      else scope.delete(check.dataset.scopeId);
      save(storageKey, JSON.stringify([...scope]));
      update(true);
    });
  }
  window.addEventListener('storage', event => {
    if (event.key === storageKey) {
      scope = readScope(event.newValue);
      update();
    }
    if (event.key === townKey && townControl) townControl.value = event.newValue ?? '';
  });
  window.addEventListener('pageshow', event => {
    if (event.persisted) {
      const value = stored(storageKey);
      if (value !== null) scope = readScope(value);
      update();
    }
  });
  update();

  if (townControl) {
    townControl.value = stored(townKey) ?? '';
    const setPlaceholder = () => {
      townControl.placeholder = townControl.dataset[root.dataset.lang + 'Placeholder'];
    };
    setPlaceholder();
    document.addEventListener('wallder:language', setPlaceholder);
    townControl.addEventListener('change', () => save(townKey, townControl.value.trim()));
  }
  if (formTown && !formTown.value && document.body.dataset.edition === 'home') {
    formTown.value = stored(townKey) ?? '';
  }

  if (motion.matches) {
    for (const cell of document.querySelectorAll('[data-type-value]')) cell.classList.add('typing');
    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver(entries => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue;
          observer.unobserve(entry.target);
          entry.target.classList.add('pressed');
        }
      }, { threshold: .32 });
      for (const stamp of document.querySelectorAll('[data-stamp]')) observer.observe(stamp);
    }
  }

  const tabs = document.querySelector('.tabs');
  const mobile = window.matchMedia('(max-width: 720px)');
  document.addEventListener('focusin', event => {
    const control = event.target;
    if (!mobile.matches || control.closest('.tabs, dialog') ||
        !control.matches(':focus-visible')) return;
    requestAnimationFrame(() => {
      if (control !== document.activeElement) return;
      const target = control.matches('[type="checkbox"]') ? control.closest('label') : control;
      const box = target.getBoundingClientRect();
      const visibleBottom = tabs.getBoundingClientRect().top - 8;
      const offset = box.top < 8 || box.height > visibleBottom - 8 ? box.top - 8 :
        box.bottom > visibleBottom ? box.bottom - visibleBottom : 0;
      if (offset) window.scrollBy({ top: offset, behavior: 'instant' });
    });
  });

  const dialog = document.querySelector('[data-lightbox]');
  if (dialog?.showModal) {
    const imageBox = dialog.querySelector('[data-lightbox-image]');
    const caption = dialog.querySelector('p');
    let opener;
    for (const link of document.querySelectorAll('[data-image-link]')) {
      link.addEventListener('click', event => {
        if (event.metaKey || event.ctrlKey || event.altKey || event.shiftKey) return;
        event.preventDefault();
        opener = link;
        const lang = root.dataset.lang;
        const img = new Image();
        img.alt = link.querySelector(':scope > [data-i18n][lang="' + lang + '"] img').alt;
        img.src = link.href;
        imageBox.replaceChildren(img);
        caption.textContent = [...link.closest('figure').querySelectorAll('figcaption [lang="' + lang + '"]')]
          .map(node => node.textContent).join('. ');
        dialog.showModal();
        dialog.querySelector('button').focus();
      });
    }
    dialog.querySelector('button').addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', event => {
      if (event.target === dialog) {
        const box = dialog.getBoundingClientRect();
        if (event.clientX < box.left || event.clientX > box.right ||
            event.clientY < box.top || event.clientY > box.bottom) dialog.close();
      }
    });
    dialog.addEventListener('close', () => opener?.focus());
  }
})();
