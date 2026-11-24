(() => {
  const root = document.documentElement;
  const languageLinks = [...document.querySelectorAll('[data-lang-choice]')];
  const localizedOptions = document.querySelectorAll('[data-option-en]');
  const localizedLabels = document.querySelectorAll('[data-label-en]');
  const localizedImages = [...document.querySelectorAll('[data-alt-en]')].map(image => ({
    image, es: image.alt, en: image.dataset.altEn
  }));
  const supported = value => value === 'es' || value === 'en';
  const videoSets = [...document.querySelectorAll('[data-video]')];
  const videoButtons = [...document.querySelectorAll('[data-video-choice]')];
  const videoControls = document.querySelector('.video-controls');
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');

  function selectVideo(language) {
    videoSets.forEach(set => {
      const visible = set.dataset.video === language;
      if (!visible) set.querySelector('video').pause();
      set.hidden = !visible;
    });
    videoButtons.forEach(button => {
      button.setAttribute('aria-pressed', String(button.dataset.videoChoice === language));
    });
  }

  function selectLanguage(language, persist = false) {
    const suffix = language === 'es' ? 'Es' : 'En';
    root.dataset.lang = language;
    root.lang = language;
    document.title = root.dataset['title' + suffix];
    languageLinks.forEach(link => {
      if (link.dataset.langChoice === language) link.setAttribute('aria-current', 'true');
      else link.removeAttribute('aria-current');
    });
    localizedOptions.forEach(option => { option.textContent = option.dataset['option' + suffix]; });
    localizedLabels.forEach(element => { element.setAttribute('aria-label', element.dataset['label' + suffix]); });
    localizedImages.forEach(({image, es, en}) => { image.alt = language === 'es' ? es : en; });
    selectVideo(language);
    if (persist) {
      try { localStorage.setItem('wallder-language', language); } catch {}
      const url = new URL(window.location.href);
      url.searchParams.set('lang', language);
      history.replaceState(null, '', url);
    }
  }

  const queryLanguage = new URLSearchParams(location.search).get('lang');
  let savedLanguage;
  try { savedLanguage = localStorage.getItem('wallder-language'); } catch {}
  selectLanguage(supported(queryLanguage) ? queryLanguage : supported(savedLanguage) ? savedLanguage : 'es');
  languageLinks.forEach(link => link.addEventListener('click', event => {
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    selectLanguage(link.dataset.langChoice, true);
  }));

  videoButtons.forEach(button => button.addEventListener('click', () => selectVideo(button.dataset.videoChoice)));
  if (videoControls) videoControls.hidden = false;
  videoSets.forEach(set => {
    const video = set.querySelector('video');
    const play = set.querySelector('.play');
    play.hidden = false;
    play.addEventListener('click', () => {
      video.play().then(() => video.focus()).catch(() => { play.hidden = true; video.focus(); });
    });
    video.addEventListener('play', () => { play.hidden = true; });
    video.addEventListener('ended', () => { play.hidden = false; });
  });

  document.querySelectorAll('.estimate-form').forEach(form => form.addEventListener('submit', event => {
    event.preventDefault();
    form.querySelector('.demo').hidden = false;
  }));

  const menu = document.querySelector('.mobile-menu');
  menu.querySelectorAll('a[href^="#"]').forEach(link => link.addEventListener('click', () => { menu.open = false; }));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && menu.open) {
      menu.open = false;
      menu.querySelector('summary').focus();
    }
  });
  const floating = document.querySelector('.floating-estimate');
  function updateScroll() {
    const y = window.scrollY;
    if (y > 95) root.classList.add('compact');
    if (y < 40) root.classList.remove('compact');
    if (floating) {
      const contactTop = estimate.getBoundingClientRect().top;
      floating.hidden = y < 630 || contactTop < innerHeight - 70;
    }
  }
  const estimate = document.querySelector('#estimado');
  window.addEventListener('scroll', updateScroll, {passive:true});
  updateScroll();

  document.querySelectorAll('[data-carousel]').forEach(carousel => {
    const track = carousel.querySelector('.project-track');
    const buttons = [...carousel.querySelectorAll('[data-slide]')];
    const cards = [...track.children];
    const update = () => {
      buttons[0].disabled = track.scrollLeft < 2;
      buttons[1].disabled = track.scrollLeft + track.clientWidth >= track.scrollWidth - 2;
    };
    function advance(direction) {
      const offsets = cards.map(card => card.offsetLeft - cards[0].offsetLeft);
      const target = direction > 0
        ? offsets.find(offset => offset > track.scrollLeft + 4)
        : offsets.findLast(offset => offset < track.scrollLeft - 4);
      track.scrollTo({left: target ?? 0, behavior: motion.matches ? 'auto' : 'smooth'});
    }
    buttons.forEach(button => button.addEventListener('click', () => advance(Number(button.dataset.slide))));
    track.addEventListener('keydown', event => {
      if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
      event.preventDefault();
      advance(event.key === 'ArrowRight' ? 1 : -1);
    });
    track.addEventListener('scroll', update, {passive:true});
    window.addEventListener('resize', update);
    carousel.querySelector('.carousel-buttons').hidden = false;
    update();
  });

  if (!motion.matches && 'IntersectionObserver' in window) {
    const reveals = new IntersectionObserver(entries => entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.classList.replace('reveal-wait', 'revealed');
      reveals.unobserve(entry.target);
    }), {threshold: .12});
    document.querySelectorAll('[data-reveal], .marks').forEach((element, index) => {
      if (element.getBoundingClientRect().top > innerHeight) {
        element.classList.add('reveal-wait');
        element.style.setProperty('--reveal-delay', (index % 3) * 85 + 'ms');
      } else {
        element.classList.add('revealed');
      }
      reveals.observe(element);
    });
    const count = new IntersectionObserver(entries => entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const element = entry.target;
      const final = element.dataset.count;
      const precision = final.includes('.') ? 1 : 0;
      const start = precision ? 0 : Number(final) - 24;
      const begin = performance.now();
      const frame = time => {
        const progress = Math.min((time - begin) / 760, 1);
        element.textContent = (start + (Number(final) - start) * (1 - (1 - progress) ** 3)).toFixed(precision);
        if (progress < 1 && !motion.matches) requestAnimationFrame(frame);
        else element.textContent = final;
      };
      requestAnimationFrame(frame);
      count.unobserve(element);
    }), {threshold: .5});
    document.querySelectorAll('[data-count]').forEach(element => count.observe(element));
  }
})();
