/*
 * Spanish auto-translate for samuelochoa.com
 *
 * Behavior:
 *   - On first visit, if the browser language starts with "es", the page
 *     auto-translates to Spanish via the Google Translate widget.
 *   - A small floating button (bottom-right) lets visitors toggle ES <-> EN.
 *   - Their choice persists via the googtrans cookie and localStorage.
 *
 * The widget is hidden visually; we only show our own toggle button.
 */
(function () {
  'use strict';

  var COOKIE_NAME = 'googtrans';
  var PREF_KEY = 'sam-lang-pref';        // 'es' | 'en' | null (no choice yet)
  var PROMPTED_KEY = 'sam-lang-prompted'; // '1' once we've auto-detected

  // ---- cookie helpers --------------------------------------------------
  function readCookie(name) {
    var m = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]+)'));
    return m ? decodeURIComponent(m[1]) : null;
  }

  function writeCookie(name, value, days) {
    var maxAge = days * 24 * 60 * 60;
    var host = window.location.hostname;
    // Write on the current host and (when applicable) on the apex domain so
    // the widget picks it up consistently across www/non-www.
    document.cookie = name + '=' + value + '; path=/; max-age=' + maxAge;
    if (host && host.indexOf('.') !== -1 && host !== 'localhost') {
      var apex = host.replace(/^www\./, '');
      document.cookie = name + '=' + value + '; path=/; domain=.' + apex + '; max-age=' + maxAge;
    }
  }

  function clearCookie(name) {
    var host = window.location.hostname;
    document.cookie = name + '=; path=/; max-age=0';
    if (host && host.indexOf('.') !== -1 && host !== 'localhost') {
      var apex = host.replace(/^www\./, '');
      document.cookie = name + '=; path=/; domain=.' + apex + '; max-age=0';
    }
  }

  // ---- current language detection -------------------------------------
  function currentLang() {
    var c = readCookie(COOKIE_NAME);          // e.g. "/en/es"
    if (c) {
      var parts = c.split('/');
      if (parts.length >= 3 && parts[2]) return parts[2];
    }
    return 'en';
  }

  function setLang(target) {
    if (target === 'en') {
      clearCookie(COOKIE_NAME);
      try { localStorage.setItem(PREF_KEY, 'en'); } catch (e) {}
    } else {
      writeCookie(COOKIE_NAME, '/en/' + target, 365);
      try { localStorage.setItem(PREF_KEY, target); } catch (e) {}
    }
    // Reload so the widget re-applies the translation cleanly.
    window.location.reload();
  }

  // ---- Google Translate bootstrap -------------------------------------
  // The widget calls this global on load.
  window.googleTranslateElementInit = function () {
    /* global google */
    new google.translate.TranslateElement({
      pageLanguage: 'en',
      includedLanguages: 'es',
      autoDisplay: false,
      layout: google.translate.TranslateElement.InlineLayout.SIMPLE
    }, 'google_translate_element');
  };

  function loadWidgetScript() {
    if (document.getElementById('gt-widget-script')) return;
    var s = document.createElement('script');
    s.id = 'gt-widget-script';
    s.src = 'https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
    s.async = true;
    document.head.appendChild(s);
  }

  // ---- UI: hidden host + visible toggle button ------------------------
  function injectStyles() {
    if (document.getElementById('sam-lang-style')) return;
    var css = '' +
      // Hide Google's chrome — we drive it ourselves.
      '#google_translate_element { position: fixed; left: -9999px; top: -9999px; visibility: hidden; }' +
      // Hide ONLY the visible top banner iframe. Google also injects
      // hidden IPC iframes with class "skiptranslate" — those must stay
      // displayed (off-screen but live) or the translation pipeline never
      // delivers results to the page. Target the obfuscated banner class
      // (currently VIpgJd-ZVi9od-ORHb-OEVmcd, with a fallback to the
      // legacy goog-te-banner-frame name) and never `iframe.skiptranslate`
      // on its own.
      '.goog-te-banner-frame, .goog-te-banner-frame.skiptranslate,' +
      ' iframe.VIpgJd-ZVi9od-ORHb-OEVmcd, .goog-te-gadget-icon { display: none !important; }' +
      // Google pushes the body down to make room for its banner; cancel it.
      'body { top: 0 !important; position: static !important; }' +
      'html { margin-top: 0 !important; }' +
      // Our toggle button.
      '#sam-lang-toggle {' +
        'position: fixed; bottom: 18px; right: 18px; z-index: 9998;' +
        'background: #111; color: #fff; border: 1px solid rgba(255,255,255,0.08);' +
        'border-radius: 999px; padding: 9px 14px;' +
        'font: 500 13px/1 \'Inter\', system-ui, -apple-system, sans-serif;' +
        'cursor: pointer; box-shadow: 0 4px 16px rgba(0,0,0,0.18);' +
        'transition: transform .15s ease, opacity .15s ease;' +
        'display: inline-flex; align-items: center; gap: 6px;' +
      '}' +
      '#sam-lang-toggle:hover { transform: translateY(-1px); }' +
      '#sam-lang-toggle:focus-visible { outline: 2px solid #7a4dff; outline-offset: 2px; }' +
      '@media (max-width: 600px) {' +
        '#sam-lang-toggle { bottom: 12px; right: 12px; padding: 8px 12px; font-size: 12px; }' +
      '}';
    var style = document.createElement('style');
    style.id = 'sam-lang-style';
    style.appendChild(document.createTextNode(css));
    document.head.appendChild(style);
  }

  function injectHost() {
    if (document.getElementById('google_translate_element')) return;
    var host = document.createElement('div');
    host.id = 'google_translate_element';
    document.body.appendChild(host);
  }

  function injectToggle() {
    if (document.getElementById('sam-lang-toggle')) return;
    var btn = document.createElement('button');
    btn.id = 'sam-lang-toggle';
    btn.type = 'button';
    var lang = currentLang();
    btn.textContent = lang === 'es' ? 'English' : 'Español';
    btn.setAttribute('aria-label', lang === 'es'
      ? 'Switch site to English'
      : 'Traducir el sitio al español');
    btn.addEventListener('click', function () {
      setLang(currentLang() === 'es' ? 'en' : 'es');
    });
    document.body.appendChild(btn);
  }

  // ---- first-visit auto-detection -------------------------------------
  function maybeAutoTranslate() {
    var alreadyPrompted = false;
    try { alreadyPrompted = localStorage.getItem(PROMPTED_KEY) === '1'; } catch (e) {}
    if (alreadyPrompted) return false;
    try { localStorage.setItem(PROMPTED_KEY, '1'); } catch (e) {}

    if (currentLang() !== 'en') return false; // user already on a translation

    var lang = (navigator.language || navigator.userLanguage || '').toLowerCase();
    var alsoCheck = (navigator.languages || []).map(function (l) { return l.toLowerCase(); });
    var isSpanish = lang.indexOf('es') === 0 || alsoCheck.some(function (l) { return l.indexOf('es') === 0; });

    if (isSpanish) {
      setLang('es'); // triggers reload
      return true;
    }
    return false;
  }

  // ---- post-translation glossary fixes --------------------------------
  //
  // Google Translate makes bad calls on tech shorthand: "LLMs" becomes
  // "másteres en derecho", "BINDER" becomes "AGLUTINANTE", etc. We can't
  // pre-wrap terms in <span translate="no"> because that breaks Google's
  // DOM-merge step entirely. Instead we let the page translate, then
  // sweep through and put the originals back where Google overreached.
  //
  // Pairs are [Spanish-output, English-original]. Case-insensitive match,
  // whole-word, applied as a global replace inside each text node Google
  // emits. Only runs while a translation is active.
  var GLOSSARY_FIXES = [
    ['máster en derecho', 'LLM'],
    ['másteres en derecho', 'LLMs'],
    ['máster\\s*en\\s*derecho', 'LLM'],
    ['Máster en Derecho', 'LLM'],
    ['Aglutinante', 'Binder'],
    ['aglutinante', 'Binder'],
    ['AGLUTINANTE', 'BINDER'],
    ['inteligencia artificial', 'AI'],
    ['Inteligencia Artificial', 'AI'],
    ['Inteligencia artificial', 'AI']
  ];

  function applyGlossaryFixes(root) {
    var walker = document.createTreeWalker(root || document.body, NodeFilter.SHOW_TEXT, null);
    var node;
    while ((node = walker.nextNode())) {
      var parent = node.parentNode;
      if (!parent) continue;
      var tag = parent.nodeName;
      if (tag === 'SCRIPT' || tag === 'STYLE' || tag === 'CODE' || tag === 'PRE') continue;
      var v = node.nodeValue;
      var changed = false;
      for (var i = 0; i < GLOSSARY_FIXES.length; i++) {
        var pair = GLOSSARY_FIXES[i];
        // Word-boundary, case-insensitive
        var re = new RegExp('\\b' + pair[0] + '\\b', 'gi');
        if (re.test(v)) {
          v = v.replace(re, pair[1]);
          changed = true;
        }
      }
      if (changed) node.nodeValue = v;
    }
  }

  function watchForTranslation() {
    function isTranslated() {
      var c = document.documentElement.classList;
      return c.contains('translated-ltr') || c.contains('translated-rtl');
    }

    // Run an initial pass in case translation already landed.
    if (isTranslated()) applyGlossaryFixes();

    // Only watch the <html> class flip — that fires once per language
    // change. We intentionally do NOT observe body subtree mutations,
    // because Google Translate uses its own observers and a two-way
    // ping-pong loop ("LLM" -> "máster en derecho" -> "LLM" -> ...) is
    // easy to set off. The class flip fires once per translation, and
    // by the time we run, Google has produced its translated DOM.
    var htmlObs = new MutationObserver(function () {
      if (isTranslated()) {
        // Wait a little more for Google's lazy passes to settle, then sweep.
        setTimeout(applyGlossaryFixes, 1500);
      }
    });
    htmlObs.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
  }

  // ---- boot ------------------------------------------------------------
  function boot() {
    injectStyles();
    injectHost();
    if (maybeAutoTranslate()) return; // reloading; nothing else to do
    loadWidgetScript();
    injectToggle();
    watchForTranslation();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
