#!/usr/bin/env python3
"""Managed AI offer regression check. Run: python3 tests/test_offer.py"""
from pathlib import Path
from html import unescape
import json
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = 'c9495c1d'

def read(name):
    return (ROOT / name).read_text()

def text(markup):
    return ' '.join(unescape(re.sub('<[^>]+>', ' ', markup)).split())

def check():
    contract = json.loads(read('offer-contract.json'))
    assert contract['offer_name'] == 'Managed AI'
    assert contract['contact_path'] == '/contact'
    support = contract['included_support']
    assert (support['window_start'], support['window_end'], support['timezone']) == ('09:00', '21:00', 'America/New_York')
    assert support['response_within_support_hours'] == 2 and not support['resolution_time_guarantee']
    assert support['requests'] == 'unlimited'
    assert contract['custom_setup']['hourly_usd'] == 125
    assert contract['custom_setup']['billing_increment_minutes'] == 15
    assert contract['custom_setup']['billing_increment_usd'] == 31.25
    usage = contract['usage']
    assert usage['monthly_price_usd'] is None and usage['monthly_allowance'] is None
    assert usage['beta_unlimited_days'] == 30 and usage['monthly_limits_after_beta']
    assert usage['limit_period'] == 'monthly' and not usage['rolling_five_hour_limits']
    assert not usage['beta_is_free_trial'] and usage['price_and_allowance_agreed_before_start']
    core = ('index.html', 'ai-consulting.html', 'terms.html')
    for name in core:
        page = text(read(name))
        for phrase in ('Queva OS', '9 AM to 9 PM Eastern Time', 'within two support hours',
                       'not a guaranteed fix time', '$125/hour', '15-minute', '$31.25',
                       'no rolling five-hour', 'first 30 days', 'Monthly limits apply afterward',
                       'not a free trial or a free month', 'before starting', 'Unlimited support requests'):
            assert phrase in page, (name, phrase)
    for name in (*core, 'about.html', 'contact.html', 'links.html', 'es/index.html'):
        page = read(name)
        assert len(re.findall(r'<main\b', page)) == page.count('</main>') == 1, name
        assert len(re.findall(r'<h1\b', page)) == 1, name
        assert 'rel="canonical"' in page and 'name="description"' in page, name
        for stale in ('Follow Up Boss', 'at Origin', 'three weeks', '$99', '$199', '$349', '$400', 'calendar.app.google', 'calendly.com'):
            assert stale not in page, (name, stale)
        for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S):
            json.loads(raw)
    spanish = text(read('es/index.html'))
    for phrase in ('9 AM a 9 PM', 'hora del Este', 'dos horas de soporte', '$125', '$31.25',
                   '15 minutos', 'primeros 30 días', 'Después se aplican los límites mensuales'):
        assert phrase in spanish, phrase
    # Compare the actual quote and video markup to the approved base, not rewritten fixtures.
    for name, prefix in [('index.html', 'lp'), ('testimonials.html', 'tst')]:
        before = subprocess.check_output(['git', 'show', f'{BASE}:{name}'], cwd=ROOT, text=True)
        after = read(name)
        for pattern, count in [(rf'<p class="{prefix}-quote".*?</p>', None),
                               (rf'<p class="{prefix}-[t]*name".*?</p>', 5),
                               (r'<video\b.*?</video>', 3)]:
            old = re.findall(pattern, before, re.S)
            assert old and old == re.findall(pattern, after, re.S), (name, pattern)
            if count: assert len(old) == count, (name, count)
        assert 'not results from' in after, name
    routes = [line.split() for line in read('_redirects').splitlines() if line and not line.startswith('#')]
    targets = {line[0]: line[1] for line in routes}
    for route in ('/book', '/book/', '/book.html'):
        assert targets[route] == '/contact', route
    for route in ('agent', 'assistant', 'queva'):
        for suffix in ('', '/*', '.html'):
            assert targets['/' + route + suffix] == '/', (route, suffix)
    assert 'tel:+15167801385' in read('contact.html')
    assert 'https://www.linkedin.com/in/samuelochoa' in read('contact.html')
    urls = [x.text for x in ET.parse(ROOT / 'sitemap.xml').findall('.//{*}loc')]
    assert len(urls) > 1000 and len(urls) == len(set(urls))
    for route in ('/', '/ai-consulting', '/contact', '/es/'):
        assert 'https://samuelochoa.com' + route in urls
    for source in targets:
        assert 'https://samuelochoa.com' + source not in urls, source
    for name in ('agent/index.html', 'assistant/index.html', 'work.html', 'offer.html',
                 'audit.html', 'websites.html', 'es/consultoria-ia.html'):
        page = read(name)
        assert 'noindex,follow' in page and 'http-equiv="refresh"' in page, name
        assert '<form' not in page, name
    # Scan every HTML file, including metadata, for the uniquely retired service promises.
    for path in ROOT.rglob('*.html'):
        page = path.read_text()
        for stale in ('calendar.app.google/mxZWNPV4nBFezjGt8', 'Agent Care', 'Care $99',
                      'founding_audit_usd', 'Start a free 15-minute leak check',
                      'I now help small offices use ChatGPT or Claude'):
            assert stale not in page, (path, stale)
    print('PASS: offer terms, metadata, Spanish summary, five testimonials and three videos per page, routes, sitemap, all-HTML stale-offer scan')

if __name__ == '__main__':
    check()
