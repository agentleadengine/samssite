/* site.js: shared behavior for samuelochoa.com (design v2).
   Mobile sidebar toggle, reveal-on-scroll, copy buttons fallback. */
(function () {
  // Mobile: collapse long lesson indexes behind a toggle.
  document.querySelectorAll('.framework-sidebar, .playbook-sidebar').forEach(function (side) {
    if (side.querySelector('.sidebar-toggle')) return;
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'sidebar-toggle';
    btn.setAttribute('aria-expanded', 'false');
    btn.textContent = side.classList.contains('playbook-sidebar') ? 'All modules' : 'In this section';
    btn.addEventListener('click', function () {
      var open = side.classList.toggle('is-open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    side.insertBefore(btn, side.firstChild);
    side.classList.add('has-toggle');
  });

  // Language toggle proxy (the floating toggle is hidden on small screens)
  document.querySelectorAll('[data-lang-toggle]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      var t = document.getElementById('sam-lang-toggle');
      if (t) t.click();
    });
  });

  // Reveal on scroll (content stays visible without JS or with reduced motion).
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var items = document.querySelectorAll('.reveal');
  if (!reduce && 'IntersectionObserver' in window && items.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px' });
    items.forEach(function (el) { io.observe(el); });
  } else {
    items.forEach(function (el) { el.classList.add('is-in'); });
  }
})();
