const form = document.querySelector('.estimate-form');
const status = form.querySelector('.form-status');

form.addEventListener('submit', (event) => {
  event.preventDefault();
  status.hidden = false;
  status.focus();
});
form.querySelector('button[type="submit"]').disabled = false;

const menu = document.querySelector('.mobile-menu');
menu.querySelectorAll('a').forEach((link) => {
  link.addEventListener('click', () => { menu.open = false; });
});
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && menu.open) {
    menu.open = false;
    menu.querySelector('summary').focus();
  }
});

{
  const root = document.documentElement;
  const player = document.querySelector('.meet-stage');
  const video = player.querySelector('video');
  const poster = player.querySelector('.meet-poster');
  const image = poster.querySelector('img');
  const stillPhoto = image.getAttribute('src');
  const play = poster.querySelector('.meet-play');
  const videoStatus = poster.querySelector('.meet-status');
  const playbackLanguages = document.querySelectorAll('[data-video-lang]');
  const pageLanguages = document.querySelectorAll('[data-page-lang]');
  const estimateForm = document.querySelector('main form');

  function setVideoLanguage(language) {
    const base = '../media/wallder-site-' + language;
    const available = player.dataset.mediaLanguages.split(/\s+/).includes(language);
    video.pause();
    video.hidden = true;
    poster.hidden = false;
    image.src = available ? base + '-poster.jpg' : stillPhoto;
    video.replaceChildren();
    if (available) {
      video.src = base + '.mp4';
      video.poster = image.getAttribute('src');
      const captions = document.createElement('track');
      captions.kind = 'captions';
      captions.src = base + '.vtt';
      captions.srclang = language;
      captions.label = language === 'es' ? 'Español' : 'English';
      captions.default = true;
      video.append(captions);
    } else if (video.hasAttribute('src')) {
      video.removeAttribute('src');
      video.removeAttribute('poster');
      video.load();
    }
    for (const button of playbackLanguages) {
      button.setAttribute('aria-pressed', String(button.dataset.videoLang === language));
    }
    play.disabled = !available;
    videoStatus.hidden = available;
    if (available) play.removeAttribute('aria-describedby');
    else play.setAttribute('aria-describedby', 'meet-status');
  }

  function updateComparisonLabel() {
    const range = document.querySelector('.comparison input[type="range"]');
    if (!range) return;
    const label = root.lang === 'en' ? '% of the installation photo' : '% de foto en obra';
    range.setAttribute('aria-valuetext', range.value + label);
  }

  function setLanguage(language) {
    root.lang = root.dataset.lang = language;
    document.title = document.querySelector('title').dataset[language];
    const description = document.querySelector('meta[name="description"]');
    description.content = description.dataset[language];
    for (const option of document.querySelectorAll('option[data-es]')) {
      option.textContent = option.dataset[language];
    }
    for (const attribute of ['alt', 'aria-label', 'placeholder', 'title']) {
      for (const element of document.querySelectorAll('[data-' + attribute + '-es]')) {
        element.setAttribute(attribute, element.getAttribute('data-' + attribute + '-' + language));
      }
    }
    for (const button of pageLanguages) {
      button.setAttribute('aria-pressed', String(button.dataset.pageLang === language));
    }
    for (const field of estimateForm.elements) field.setCustomValidity?.('');
    updateComparisonLabel();
    setVideoLanguage(language);
  }

  const key = 'wallder-language';
  setLanguage(root.dataset.lang);

  for (const button of pageLanguages) {
    button.addEventListener('click', () => {
      const language = button.dataset.pageLang;
      try { localStorage.setItem(key, language); } catch {}
      const url = new URL(location.href);
      url.searchParams.set('lang', language);
      history.replaceState(history.state, '', url);
      if (root.lang !== language) setLanguage(language);
    });
    button.closest('.language-switch').hidden = false;
  }
  for (const button of playbackLanguages) {
    button.addEventListener('click', () => {
      if (button.getAttribute('aria-pressed') !== 'true') setVideoLanguage(button.dataset.videoLang);
    });
    button.closest('.language-switch').hidden = false;
  }
  play.addEventListener('click', () => {
    if (play.disabled) return;
    poster.hidden = true;
    video.hidden = false;
    video.focus();
    video.play().catch(() => {
      video.hidden = true;
      poster.hidden = false;
      play.focus();
    });
  });

  estimateForm.addEventListener('invalid', event => {
    const field = event.target;
    if (field.validity.valueMissing) {
      const spanish = root.lang === 'es';
      field.setCustomValidity(field.matches('select')
        ? (spanish ? 'Elige un servicio.' : 'Choose a service.')
        : (spanish ? 'Completa este campo.' : 'Fill in this field.'));
    }
  }, true);
  estimateForm.addEventListener('input', event => event.target.setCustomValidity?.(''));
}

{
  const root = document.documentElement;
  const preference = matchMedia('(prefers-reduced-motion: reduce)');
  const header = document.querySelector('header');
  const reveals = [...document.querySelectorAll('[data-reveal]')];
  const numbers = [...document.querySelectorAll('[data-counter]')];
  let revealObserver;
  let numberObserver;

  function updateHeader() {
    header.classList.toggle('compact-nav', !preference.matches && scrollY > 75);
  }

  function count(number) {
    const end = Number(number.dataset.counter);
    const startValue = end === 2002 ? 1992 : 0;
    const decimals = Number.isInteger(end) ? 0 : 1;
    const start = performance.now();
    const text = number.textContent;
    const width = number.getBoundingClientRect().width;
    number.style.display = 'inline-block';
    number.style.minWidth = width + 'px';
    function tick(now) {
      const progress = Math.max(0, Math.min((now - start) / 760, 1));
      if (preference.matches || progress === 1) {
        number.textContent = text;
        number.style.removeProperty('min-width');
        number.style.removeProperty('display');
        return;
      }
      number.textContent = (startValue + (end - startValue) * (1 - (1 - progress) ** 3)).toFixed(decimals);
      requestAnimationFrame(tick);
    }
    number.dataset.counted = '';
    requestAnimationFrame(tick);
  }

  function enableMotion() {
    revealObserver?.disconnect();
    numberObserver?.disconnect();
    for (const item of reveals) item.classList.remove('awaiting-reveal');
    root.classList.toggle('motion-ready', !preference.matches);
    updateHeader();
    if (preference.matches || !('IntersectionObserver' in window)) return;

    revealObserver = new IntersectionObserver(entries => {
      for (const {target, isIntersecting} of entries) {
        if (!isIntersecting) continue;
        target.classList.remove('awaiting-reveal');
        target.dataset.revealed = '';
        revealObserver.unobserve(target);
      }
    }, {rootMargin: '0px 0px 25% 0px'});
    for (const item of reveals) {
      if ('revealed' in item.dataset) continue;
      if (item.getBoundingClientRect().top >= innerHeight) item.classList.add('awaiting-reveal');
      revealObserver.observe(item);
    }
    numberObserver = new IntersectionObserver(entries => {
      for (const {target, isIntersecting} of entries) {
        if (!isIntersecting) continue;
        count(target);
        numberObserver.unobserve(target);
      }
    }, {threshold: .5});
    for (const number of numbers) {
      if (!('counted' in number.dataset)) numberObserver.observe(number);
    }
  }

  window.addEventListener('scroll', updateHeader, {passive: true});
  preference.addEventListener('change', enableMotion);
  enableMotion();
}
