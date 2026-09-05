#!/usr/bin/env python3
"""Fail-closed checks for the staged core offer journey. Run from any cwd."""
from pathlib import Path
import unittest
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]

class OfferJourneyTests(unittest.TestCase):
    def test_home_primary_action_is_free_check_not_paid_purchase(self):
        soup = BeautifulSoup((ROOT / 'index.html').read_text(), 'html.parser')
        primary = soup.select_one('.lp-hero .lp-btn-primary')
        self.assertIsNotNone(primary)
        self.assertEqual(primary['href'], 'audit.html#intake')
        self.assertIn('free 15-minute', primary.get_text().lower())

    def test_core_offer_does_not_call_hypothetical_revenue_measured(self):
        for name in ('index.html', 'audit.html', 'sample-audit.html'):
            with self.subTest(page=name):
                text = BeautifulSoup((ROOT / name).read_text(), 'html.parser').get_text(' ', strip=True).lower()
                for unsupported in ('measured leak worth more than the fee', 'dollar figure on every', 'annual recoverable leak', 'lifetime commission', 'first 3 businesses through'):
                    self.assertNotIn(unsupported, text)
        sample = BeautifulSoup((ROOT / 'sample-audit.html').read_text(), 'html.parser')
        self.assertIn('No observed client results', sample.get_text(' ', strip=True))
        self.assertIn('Not known', sample.get_text(' ', strip=True))

    def test_agency_route_and_retired_offers(self):
        agency = ROOT / 'insurance-agencies.html'
        self.assertTrue(agency.exists(), 'Dedicated agency journey is missing')
        text = BeautifulSoup(agency.read_text(), 'html.parser').get_text(' ', strip=True)
        self.assertIn('quoted-but-not-bound', text)
        for name in ('offer.html','websites.html','paginas-web.html'):
            soup = BeautifulSoup((ROOT/name).read_text(),'html.parser')
            self.assertIsNone(soup.find('form'), name)
            self.assertIsNotNone(soup.select_one('a[href="audit.html#intake"]'), name)
        contact = BeautifulSoup((ROOT/'contact.html').read_text(),'html.parser')
        self.assertIsNone(contact.select_one('a[href="offer.html"]'))

    def test_machine_readable_published_offer_and_core_price(self):
        import json
        c = json.loads((ROOT / 'offer-contract.json').read_text())
        self.assertEqual(c['status'], 'approved_for_publication')
        self.assertFalse(c['revenue_guarantee'])
        for name in ('index.html', 'audit.html', 'sample-audit.html'):
            text = BeautifulSoup((ROOT / name).read_text(), 'html.parser').get_text(' ', strip=True)
            self.assertIn(f"${c['audit_usd']:,}", text, name)
        audit = BeautifulSoup((ROOT / 'audit.html').read_text(), 'html.parser').get_text(' ', strip=True)
        self.assertIn(c['offer_name'], audit)
        self.assertIn('calendar month', audit)

    def test_home_has_one_main_landmark(self):
        s = BeautifulSoup((ROOT / 'index.html').read_text(), 'html.parser')
        self.assertEqual(len(s.find_all('main')), 1)
        self.assertIsNotNone(s.select_one('main h1'))

    def test_sitemap_and_archived_route_indexing(self):
        import xml.etree.ElementTree as ET
        urls = [x.text for x in ET.parse(ROOT / 'sitemap.xml').findall('.//{*}loc')]
        self.assertGreater(len(urls), 1000, 'Sitemap verification must not pass an empty inventory')
        self.assertEqual(len(urls), len(set(urls)))
        self.assertIn('https://samuelochoa.com/insurance-agencies', urls)
        for name in ('offer.html', 'websites.html', 'paginas-web.html', 'es/paginas-web-para-negocios.html'):
            s = BeautifulSoup((ROOT / name).read_text(), 'html.parser')
            self.assertIn('noindex', s.select_one('meta[name="robots"]')['content'])
            route = name.removesuffix('.html')
            self.assertNotIn('https://samuelochoa.com/' + route, urls)
            self.assertNotIn('https://samuelochoa.com/' + name, urls)

    def test_existing_intake_field_contract_is_preserved(self):
        import subprocess
        baseline = subprocess.run(['git', 'show', '4eafa785f0991c83e841b16bce4f1144fd0a538f:audit.html'], cwd=ROOT, check=True, capture_output=True, text=True).stdout
        before = BeautifulSoup(baseline, 'html.parser').select_one('form[name="audit-intake"]')
        after = BeautifulSoup((ROOT / 'audit.html').read_text(), 'html.parser').select_one('form[name="audit-intake"]')
        old_names = {x['name'] for x in before.select('[name]')}
        new_names = {x['name'] for x in after.select('[name]')}
        self.assertTrue(old_names <= new_names, old_names - new_names)
        self.assertEqual(after.get('method', '').lower(), 'post')
        self.assertEqual(after.get('data-netlify'), before.get('data-netlify'))

if __name__ == '__main__':
    unittest.main(verbosity=2)
