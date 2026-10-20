#!/usr/bin/env python3
"""Managed AI offer regression check. Run: python3 tests/test_offer.py"""
from pathlib import Path
from html import unescape
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
BASE = 'c9495c1d'

def read(name):
    return (ROOT / name).read_text()

def text(markup):
    return ' '.join(unescape(re.sub('<[^>]+>', ' ', markup)).split())

def check():
    contract = json.loads(read('offer-contract.json'))
    assert contract['offer_name'] == 'Managed AI'
    assert contract['product'] == 'QUEVA for Real Estate'
    assert contract['parent_company'] == contract['system_creator'] == 'Agent Lead Engine'
    assert contract['system'] == 'QUEVA OS'
    assert contract['operator'] == 'Samuel Ochoa'
    previous = json.loads(subprocess.check_output(
        ['git', 'show', '9d739afb:offer-contract.json'], cwd=ROOT, text=True))
    for key in ('included_support', 'custom_setup', 'usage'):
        assert contract[key] == previous[key], key
    assert contract['status'] == 'current_offer'
    assert contract['contact_path'] == '/contact'
    assert contract['audience'] == 'Real estate agents and small teams'
    assert contract['primary_cta'] == 'Request a demo'
    for name in ('index.html', 'ai-consulting.html', 'about.html', 'links.html',
                 'ai.html', 'ghl.html', 'thanks-ai.html', 'thanks-ghl.html'):
        page = read(name)
        assert 'real estate' in text(page).lower(), name
        ctas = re.findall(r'<a\b[^>]*href="([^"]+)"[^>]*>Request a demo(?: →)?</a>', page)
        assert ctas and set(ctas) == {'/contact'}, name
    for name in ('index.html', 'ai-consulting.html'):
        page = read(name)
        assert 'real estate' in text(re.search(r'<h1\b.*?</h1>', page, re.S)[0])
        assert text(re.search(r'<h1\b.*?</h1>', page, re.S)[0]) == 'Your real estate AI assistant.'
        assert 'Set up, managed, and supported for you.' in text(page)
        assert 'QUEVA for Real Estate' in text(page)
        assert all(phrase in text(page) for phrase in ('follow-ups', 'paperwork', 'routine admin'))
    for name in ('index.html', 'ai-consulting.html', 'contact.html', 'about.html', 'links.html', 'es/index.html'):
        page = read(name)
        assert not re.search(r'showingday|showday|\bromy\b|\banya\b', page, re.I), name
        body = page.split('<body', 1)[1]
        description = re.search(r'<meta name="description" content="([^"]+)"', page)[1]
        for phrase in ('QUEVA for Real Estate', 'QUEVA OS', 'Agent Lead Engine'):
            assert phrase in text(body) and phrase in description, (name, phrase)
    assert 'href="/#demo-examples"' in read('ai-consulting.html')
    assert read('index.html').index('id="demo-examples"') < read('index.html').index('id="proof"')
    home = BeautifulSoup(read('index.html'), 'html.parser')
    demos = home.select('#demo-examples article[data-sd-demo]')
    assert [demo['data-sd-demo'] for demo in demos] == ['followup', 'lease', 'money']
    assert home.select_one('script[type="module"][src="/assets/real-estate-demo.js"]')
    assert home.select_one('link[rel="stylesheet"][href="/assets/real-estate-demo.css"]')
    for demo in demos:
        assert 'Interactive sample / fictional data' in demo.get_text()
        assert not demo.select('form, input, textarea, iframe'), demo['data-sd-demo']
        assert demo.select_one('[data-sd-output][aria-live="polite"]')
        assert demo.select_one('[data-sd-status][role="status"]')
        assert demo.select_one('noscript')
        for action in ('prepare', 'review', 'approve', 'reset'):
            button = demo.select_one(f'button[data-sd-action="{action}"]')
            assert button and button['type'] == 'button'
            assert button.has_attr('disabled') == (action in ('review', 'approve'))
        for select in demo.select('select'):
            assert select.find_parent('label')
    assert 'This sample is not connected to either CRM.' in demos[0].get_text()
    assert 'signing/delivery not included' in demos[1].get_text()
    assert 'Beta preview under final validation' in demos[2].get_text()
    assert [o['value'] for o in demos[2].select('option')] == ['complete', 'missing']
    assert 'Call, email or message me on LinkedIn' in read('contact.html')
    assert 'subject=Real%20estate%20AI%20demo%20request' in read('contact.html')
    assert 'agentes inmobiliarios y equipos pequeños' in read('es/index.html')
    assert 'href="/contact">Solicitar una demo</a>' in read('es/index.html')
    support = contract['included_support']
    assert support['days'] == ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
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
    assert 'beta_is_free_trial' not in usage and usage['price_and_allowance_agreed_before_start']
    core = ('index.html', 'ai-consulting.html', 'terms.html')
    for name in core:
        page = text(read(name))
        assert 'queva os' in page.lower(), name
        for phrase in ('9 AM to 9 PM Eastern Time', 'within two support hours',
                       '$125/hour', '15-minute', '$31.25',
                       'no rolling five-hour', 'first 30 days', 'Monthly limits apply afterward',
                       'We agree your price before you start.', 'before starting', 'Unlimited support requests'):
            assert phrase in page, (name, phrase)
    assert 'not a guaranteed fix time' in text(read('terms.html'))
    for name in (*core, 'contact.html'):
        page = text(read(name))
        assert 'every day, 9 AM to 9 PM Eastern Time' in page, name
        assert 'not a free trial or a free month' not in page, name
        if name != 'terms.html':
            assert 'not a guaranteed fix time' not in page, name
    for name in ('index.html', 'ai-consulting.html'):
        intro = re.search(r'<p class="(?:lp-hsub|intro)">(.*?)</p>', read(name), re.S)[1]
        assert not text(intro).startswith('We run your AI for you.')
        assert 'Sam uses' not in intro
    for name in (*core, 'about.html', 'contact.html', 'links.html', 'es/index.html'):
        page = read(name)
        # CRM names are allowed only in the explicitly disconnected fictional sample.
        offer_copy = re.sub(r'<article class="sd-demo".*?</article>', '', page, flags=re.S)
        assert 'Follow Up Boss' not in offer_copy, name
        assert len(re.findall(r'<main\b', page)) == page.count('</main>') == 1, name
        assert len(re.findall(r'<h1\b', page)) == 1, name
        assert 'rel="canonical"' in page and 'name="description"' in page, name
        for stale in ('at Origin', 'three weeks', '$99', '$199', '$349', '$400', 'calendar.app.google', 'calendly.com'):
            assert stale not in page, (name, stale)
        for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S):
            json.loads(raw)
    spanish = text(read('es/index.html'))
    for phrase in ('todos los días, de 9 AM a 9 PM', 'hora del Este', 'dos horas de soporte', '$125', '$31.25',
                   '15 minutos', 'primeros 30 días', 'Después se aplican los límites mensuales'):
        assert phrase in spanish, phrase
    assert 'prueba ni un mes gratis' not in spanish
    assert 'Acordamos tu precio antes de empezar.' in spanish
    # Sam 2026-10-20: no testimonials on the site. The page is gone and old links go home.
    assert not (ROOT / 'testimonials.html').exists()
    for name in ('index.html', 'es/index.html', 'about.html', 'ai-consulting.html', 'thanks.html'):
        page = read(name)
        assert 'id="testimonials"' not in page and 'href="/testimonials"' not in page and 'testimonials.html' not in page, name
        assert 'class="lp-quote"' not in page, name
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
    print('PASS: QUEVA for Real Estate identity, three accessible sample embeds, unchanged commercial terms, daily support, metadata, Spanish summary, no testimonials, routes, sitemap, all-HTML stale-offer scan')

if __name__ == '__main__':
    check()
