(function () {
  'use strict';
  const CALENDLY_URL = 'https://calendly.com/agentleadengine/meet-with-sam';
  const AGENT_CARE_SEND_TO = 'AW-18240559803/R_epCO2X4I0dELu14_lD';
  const introVideoUrl = document.body.dataset.introVideo;
  const thanksUrl = document.body.dataset.thanksUrl;
  const booking = document.getElementById('booking');
  const calendar = document.getElementById('calendly-inline');
  let widgetStarted = false;
  let booked = false;

  const promoDeadline = new Date('2026-11-10T23:59:59-05:00').getTime();
  const query = new URLSearchParams(window.location.search);
  const fromAd = query.has('gclid') || query.has('gbraid') || query.has('wbraid') ||
    (query.get('utm_medium')?.toLowerCase() === 'cpc' && query.get('utm_source')?.toLowerCase() === 'google');
  let promo = false;
  try {
    if (Date.now() <= promoDeadline) {
      promo = fromAd || window.localStorage.getItem('ac_promo') === '1';
      if (fromAd) window.localStorage.setItem('ac_promo', '1');
    } else {
      window.localStorage.removeItem('ac_promo');
    }
  } catch (_) {
    promo = Date.now() <= promoDeadline && fromAd;
  }
  if (promo) {
    document.querySelectorAll('[data-price="standard"]').forEach(function (element) { element.hidden = true; });
    document.querySelectorAll('[data-price="promo"]').forEach(function (element) { element.hidden = false; });
  }

  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = window.gtag || gtag;
  gtag('js', new Date());
  gtag('config', 'AW-18240559803');
  window.addEventListener('load', function () {
    const tag = document.createElement('script');
    tag.async = true;
    tag.src = 'https://www.googletagmanager.com/gtag/js?id=AW-18240559803';
    document.head.appendChild(tag);
    (function (c, l, a, r, i, t, y) {
      c[a] = c[a] || function () { (c[a].q = c[a].q || []).push(arguments); };
      t = l.createElement(r); t.async = true; t.src = 'https://www.clarity.ms/tag/' + i;
      y = l.getElementsByTagName(r)[0]; y.parentNode.insertBefore(t, y);
    })(window, document, 'clarity', 'script', 'x9tyuivf47');
    const intro = document.querySelector('.agent-intro-video');
    fetch(introVideoUrl, { method: 'HEAD' }).then(function (response) {
      if (response.ok) {
        intro.hidden = false;
        document.querySelector('.agent-intro-fallback').hidden = true;
      }
    }).catch(function () { /* The photo and coming-soon card stay visible. */ });
  });

  function showBooking(event) {
    if (event) event.preventDefault();
    gtag('event', 'agent_care_booking_cta_click', { event_category: 'engagement' });
    booking.hidden = false;
    booking.scrollIntoView({ behavior: 'smooth', block: 'start' });
    if (widgetStarted) return;
    widgetStarted = true;
    const css = document.createElement('link');
    css.rel = 'stylesheet';
    css.href = 'https://assets.calendly.com/assets/external/widget.css';
    document.head.appendChild(css);
    const script = document.createElement('script');
    script.src = 'https://assets.calendly.com/assets/external/widget.js';
    script.async = true;
    script.onload = function () {
      if (window.Calendly && window.Calendly.initInlineWidget) {
        window.Calendly.initInlineWidget({ url: CALENDLY_URL, parentElement: calendar });
      }
    };
    script.onerror = function () { calendar.textContent = 'The calendar could not load. Use the Calendly link above to book.'; };
    document.head.appendChild(script);
  }

  document.querySelectorAll('.booking-link').forEach(function (link) {
    link.addEventListener('click', showBooking);
  });
  document.getElementById('booking-close').addEventListener('click', function () {
    booking.hidden = true;
    document.querySelector('.agent-top-cta .booking-link').focus();
  });

  window.addEventListener('message', function (message) {
    if (message.origin !== 'https://calendly.com' && message.origin !== 'https://www.calendly.com') return;
    if (!message.data || message.data.event !== 'calendly.event_scheduled' || booked) return;
    booked = true;
    let redirected = false;
    function finish() {
      if (redirected) return;
      redirected = true;
      window.location.assign(thanksUrl);
    }
    gtag('event', 'conversion', {
      send_to: AGENT_CARE_SEND_TO,
      value: 150.0,
      currency: 'USD',
      event_callback: finish,
      event_timeout: 1200
    });
    window.setTimeout(finish, 1300);
  });
})();
