(() => {
  const root = document.documentElement;
  const title = document.querySelector('title');
  const description = document.querySelector('meta[name="description"]');
  const switches = [...document.querySelectorAll('[data-language]')];

  function refresh(lang) {
    root.lang = root.dataset.lang = lang;
    title.textContent = title.dataset[lang];
    description.content = description.dataset[lang];

    for (const link of document.querySelectorAll('a[href]')) {
      const raw = link.getAttribute('href');
      if (!raw || raw.startsWith('#') || link.hasAttribute('data-image-link')) continue;
      const url = new URL(raw, location.href);
      if (/^(https?:|file:)$/.test(url.protocol) && url.origin === location.origin) {
        const [path, hash = ''] = raw.split('#');
        const [pathname, query = ''] = path.split('?');
        const params = new URLSearchParams(query);
        params.set('lang', lang);
        link.setAttribute('href', pathname + '?' + params + (hash ? '#' + hash : ''));
      }
    }
    for (const control of switches) {
      control.setAttribute('aria-pressed', String(control.dataset.language === lang));
    }
    document.dispatchEvent(new CustomEvent('wallder:language', { detail: lang }));
  }

  switches.forEach(control => control.addEventListener('click', () => {
    const lang = control.dataset.language;
    try { localStorage.setItem('wallder-language', lang); } catch {}
    const url = new URL(location.href);
    url.searchParams.set('lang', lang);
    try { history.replaceState(history.state, '', url); } catch {}
    refresh(lang);
  }));

  refresh(root.dataset.lang);
})();
