const root = document.documentElement;
const title = document.querySelector('title');
const description = document.querySelector('meta[name="description"]');
const menu = document.querySelector('.mobile-menu');
const player = document.querySelector('.video-stage');
const video = player.querySelector('video');
const poster = player.querySelector('.video-poster');
const play = player.querySelector('.play');
const videoStatus = player.querySelector('.video-status');
const availableMedia = player.dataset.mediaLanguages.split(' ');
const form = document.querySelector('.estimate-form');
const motion = matchMedia('(prefers-reduced-motion: reduce)');

function validLang(value) {
  return value === 'es' || value === 'en';
}

function setVideoLanguage(lang) {
  video.pause();
  video.hidden = true;
  poster.hidden = false;
  document.querySelectorAll('[data-video-lang]').forEach((button) => {
    button.setAttribute('aria-pressed', String(button.dataset.videoLang === lang));
  });
  player.dataset.activeLang = lang;
  const available = availableMedia.includes(lang);
  const base = '../media/wallder-site-' + lang;
  const image = poster.querySelector('img');
  if (!image.dataset.fallback) {
    image.dataset.fallback = image.getAttribute('src');
    image.dataset.fallbackSet = image.getAttribute('srcset') || '';
  }
  if (available) {
    image.removeAttribute('srcset');
    image.src = base + '-poster.jpg';
    video.poster = image.src;
    video.src = base + '.mp4';
    const track = document.createElement('track');
    track.kind = 'captions';
    track.src = base + '.vtt';
    track.srclang = lang;
    track.label = lang === 'es' ? 'Español' : 'English';
    track.default = true;
    video.replaceChildren(track);
  } else {
    image.setAttribute('srcset', image.dataset.fallbackSet);
    image.src = image.dataset.fallback;
    video.removeAttribute('src');
    video.replaceChildren();
    video.load();
  }
  play.disabled = !available;
  videoStatus.hidden = available;
}

function setLanguage(lang) {
  const suffix = lang === 'es' ? 'Es' : 'En';
  root.lang = root.dataset.lang = lang;
  title.textContent = title.dataset[lang];
  description.content = description.dataset[lang];
  document.querySelectorAll('[data-label-es]').forEach((item) => {
    item.setAttribute('aria-label', item.dataset['label' + suffix]);
  });
  document.querySelectorAll('[data-alt-es]').forEach((item) => {
    item.alt = item.dataset['alt' + suffix];
  });
  document.querySelectorAll('[data-text-es]').forEach((item) => {
    item.textContent = item.dataset['text' + suffix];
  });
  document.querySelectorAll('[data-pick-lang]').forEach((button) => {
    button.setAttribute('aria-pressed', String(button.dataset.pickLang === lang));
  });
  for (const field of form.elements) field.setCustomValidity('');
  setVideoLanguage(lang);
}

let saved;
try { saved = localStorage.getItem('wallder-language'); } catch {}
const query = new URLSearchParams(location.search).get('lang');
setLanguage([query, saved].find(validLang) || 'es');
root.classList.add('enhanced');

document.querySelectorAll('[data-pick-lang]').forEach((button) => {
  button.addEventListener('click', () => {
    const lang = button.dataset.pickLang;
    if (root.dataset.lang === lang) return;
    try { localStorage.setItem('wallder-language', lang); } catch {}
    const url = new URL(location.href);
    url.searchParams.set('lang', lang);
    history.replaceState(history.state, '', url);
    setLanguage(lang);
  });
});

document.querySelectorAll('[data-video-lang]').forEach((button) => {
  button.addEventListener('click', () => {
    if (player.dataset.activeLang !== button.dataset.videoLang) {
      setVideoLanguage(button.dataset.videoLang);
    }
  });
});

play.addEventListener('click', () => {
  poster.hidden = true;
  video.hidden = false;
  video.focus();
  video.play().catch(() => {});
});

menu.querySelectorAll('a').forEach((item) => {
  item.addEventListener('click', () => { menu.open = false; });
});
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && menu.open) {
    menu.open = false;
    menu.querySelector('summary').focus();
  }
});

form.addEventListener('invalid', (event) => {
  const field = event.target;
  const spanish = root.lang === 'es';
  if (field.validity.valueMissing) {
    const prompt = field.matches('select')
      ? (spanish ? 'Elige un servicio.' : 'Choose a service.')
      : (spanish ? 'Completa este campo.' : 'Fill in this field.');
    field.setCustomValidity(prompt);
  }
  if (field.validity.typeMismatch) {
    field.setCustomValidity(spanish ? 'Escribe un correo electrónico válido.' : 'Enter a valid email address.');
  }
}, true);
form.addEventListener('input', (event) => event.target.setCustomValidity(''));
form.addEventListener('submit', (event) => {
  event.preventDefault();
  const status = form.querySelector('.form-status');
  status.hidden = false;
  status.focus();
});
form.querySelector('button[type="submit"]').disabled = false;

const filters = document.querySelector('.filters');
if (filters) {
  const type = filters.querySelector('[name="type"]');
  const system = filters.querySelector('[name="system"]');
  const cards = [...document.querySelectorAll('#project-grid [data-type]')];
  const total = filters.querySelector('[data-total]');
  const empty = document.querySelector('.no-results');
  function applyFilters() {
    let count = 0;
    cards.forEach((card) => {
      const matchesType = !type.value || type.value === card.dataset.type;
      const matchesSystem = !system.value || card.dataset.system.split(' ').includes(system.value);
      card.hidden = !(matchesType && matchesSystem);
      if (!card.hidden) count++;
    });
    total.textContent = count;
    empty.hidden = count !== 0;
  }
  filters.addEventListener('change', applyFilters);
  filters.querySelector('.reset').addEventListener('click', () => {
    type.value = system.value = '';
    applyFilters();
  });
  filters.hidden = false;
  applyFilters();
}

function countUp(item) {
  const end = Number(item.dataset.count);
  const precision = Number.isInteger(end) ? 0 : 1;
  const suffix = item.dataset.suffix || '';
  const start = performance.now();
  function step(now) {
    const progress = Math.min((now - start) / 750, 1);
    item.textContent = (end * (1 - (1 - progress) ** 3)).toFixed(precision) + suffix;
    if (progress < 1 && !motion.matches) requestAnimationFrame(step);
    else item.textContent = end.toFixed(precision) + suffix;
  }
  requestAnimationFrame(step);
}

if (!motion.matches && 'IntersectionObserver' in window) {
  const reveal = new IntersectionObserver((entries) => {
    entries.forEach(({target, isIntersecting}) => {
      if (!isIntersecting) return;
      target.classList.remove('pending');
      reveal.unobserve(target);
    });
  }, {rootMargin:'0px 0px -24px 0px'});
  document.querySelectorAll('[data-reveal]').forEach((item) => {
    if (item.getBoundingClientRect().top > innerHeight) item.classList.add('pending');
    reveal.observe(item);
  });
  const counters = new IntersectionObserver((entries) => {
    entries.forEach(({target, isIntersecting}) => {
      if (!isIntersecting) return;
      if (!motion.matches) countUp(target);
      counters.unobserve(target);
    });
  }, {threshold:.75});
  document.querySelectorAll('[data-count]').forEach((item) => counters.observe(item));
}
const siteHeader = document.querySelector('.site-header');
function compactHeader() {
  siteHeader.classList.toggle('compact', window.scrollY > 40);
}
window.addEventListener('scroll', compactHeader, {passive:true});
compactHeader();
