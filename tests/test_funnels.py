"""Static contracts for the YouTube capture pages and booking route."""
from pathlib import Path
from urllib.parse import urlsplit, unquote
import re
from html import unescape
import unittest
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
CAPTURE = {'ghl': ('ghl', 'ghl-list'), 'snapshots': ('ghl', 'snapshots'),
           'ai': ('ai', 'ai-list'), 'newsletter': ('ai', 'newsletter')}
NEW = (*CAPTURE, 'links', 'thanks-ghl', 'thanks-ai')


def read(slug):
    return BeautifulSoup((ROOT / (slug + '.html')).read_text(), 'html.parser')


class FunnelTests(unittest.TestCase):
    def test_capture_contract(self):
        for slug, (channel, interest) in CAPTURE.items():
            with self.subTest(page=slug):
                soup = read(slug)
                forms = soup.find_all('form')
                self.assertEqual(len(forms), 1)
                form = forms[0]
                self.assertFalse(form.has_attr('hidden'))
                self.assertEqual(form.get('name'), channel + '-list')
                self.assertEqual(form.get('method', '').lower(), 'post')
                self.assertEqual(form.get('action'), '/thanks-' + channel)
                self.assertEqual(form.get('data-netlify'), 'true')
                self.assertEqual(form.get('netlify-honeypot'), 'bot-field')
                self.assertIsNotNone(form.select_one('[name="bot-field"]'))
                fields = {x['name']: x for x in form.select('input[type="hidden"][name]')}
                for key in ('form-name', 'utm_source', 'utm_medium', 'utm_campaign',
                            'utm_content', 'page', 'channel', 'interest'):
                    self.assertIn(key, fields)
                self.assertEqual(fields['form-name']['value'], channel + '-list')
                self.assertEqual(fields['channel']['value'], channel)
                self.assertEqual(fields['interest']['value'], interest)
                self.assertEqual(fields['page']['value'], '/' + slug)
                self.assertEqual([x.get('name') for x in form.select('[required]')], ['email'])
                email = form.select_one('input[type="email"]')
                self.assertIsNotNone(form.find('label', attrs={'for': email['id']}))
                self.assertIn('unsubscribe link', form.get_text())
                self.assertIsNotNone(form.select_one('button[type="submit"]'))

    def test_links_hub_has_no_form_or_nav(self):
        soup = read('links')
        self.assertIsNone(soup.find('form'))
        self.assertIsNone(soup.find('nav'))
        self.assertIsNone(soup.find('footer'))
        self.assertEqual([x['href'] for x in soup.select('.lp-linkstack a')],
                         ['/ghl', '/newsletter', '/book', '/audit', '/about'])
        self.assertIsNotNone(soup.select_one('img[src="/sam-real.jpg"]'))

    def test_copy_and_metadata(self):
        for slug in (*NEW, 'thanks-web', 'gracias'):
            with self.subTest(page=slug):
                soup = read(slug)
                body = soup.body.get_text(' ', strip=True)
                self.assertNotIn('\u2014', str(soup))
                self.assertNotIn('\u2013', body)
                self.assertNotIn('$', body)
                self.assertNotIn('trusted by', body.lower())
                self.assertIsNone(soup.select_one('a[href^="tel:"]'))
                self.assertEqual(len(soup.find_all('main')), 1)
                self.assertEqual(len(soup.find_all('h1')), 1)
                self.assertEqual(soup.select_one('link[rel="canonical"]')['href'],
                                 'https://samuelochoa.com/' + slug)
                self.assertIn('x9tyuivf47', str(soup))
                self.assertNotIn('googletagmanager', str(soup))
        for slug in ('ghl', 'snapshots'):
            self.assertEqual(len(read(slug).select('.lp-resource .lp-status')), 6)
            self.assertEqual({x.get_text() for x in read(slug).select('.lp-status')}, {'Planned'})
        self.assertEqual(len(read('ai').select('.lp-playbooks .lp-status')), 5)

    def test_sample_is_fictional_and_in_word_budget(self):
        sample = read('newsletter').select_one('.lp-sample')
        text = sample.get_text(' ', strip=True)
        self.assertIn('Sample issue', text)
        self.assertIn('fictional', text)
        self.assertGreaterEqual(len(text.split()), 350)
        self.assertLessEqual(len(text.split()), 450)
        self.assertEqual(len(sample.find_all('h4')), 5)

    def test_thank_you_and_sitemap(self):
        urls = [x.text for x in ET.parse(ROOT / 'sitemap.xml').findall('.//{*}loc')]
        for slug in ('ghl', 'ai', 'newsletter', 'snapshots', 'links'):
            self.assertEqual(urls.count('https://samuelochoa.com/' + slug), 1)
        for slug in ('thanks-ghl', 'thanks-ai', 'thanks-web', 'gracias'):
            soup = read(slug)
            self.assertIn('noindex', soup.select_one('meta[name="robots"]')['content'])
            self.assertNotIn('https://samuelochoa.com/' + slug, urls)
        for slug in ('thanks-ghl', 'thanks-ai'):
            text = read(slug).get_text(' ', strip=True)
            self.assertIn('I send the first email when it is ready', text)
            self.assertNotIn('check your inbox', text.lower())

    def test_booking_single_target(self):
        self.assertIn('/book https://calendly.com/agentleadengine/meet-with-sam 301!',
                      (ROOT / '_redirects').read_text().splitlines())
        for slug in ('audit', 'contact', *NEW):
            soup = read(slug)
            self.assertNotIn('api.leadconnectorhq.com/widget/booking', str(soup))
            for a in soup.select('a[href]'):
                if re.match(r'book\b', a.get_text(' ', strip=True), re.I):
                    self.assertEqual(a['href'], '/book')

    def test_no_page_has_em_dash_in_body_copy(self):
        for path in ROOT.rglob('*.html'):
            html = path.read_text()
            if '\u2014' not in unescape(html):
                continue
            soup = BeautifulSoup(html, 'html.parser')
            if soup.body:
                self.assertNotIn('\u2014', soup.body.get_text(' ', strip=True), str(path))

    def test_all_booking_ctas_use_shared_route(self):
        for path in ROOT.rglob('*.html'):
            html = path.read_text()
            self.assertNotIn('api.leadconnectorhq.com/widget/booking', html, str(path))
            for markup in re.findall(r'<a\b[^>]*>.*?</a>', html, re.S | re.I):
                if 'book' not in markup.lower():
                    continue
                a = BeautifulSoup(markup, 'html.parser').find('a')
                if a and re.match(r'book\b', a.get_text(' ', strip=True), re.I):
                    self.assertEqual(a.get('href'), '/book', str(path))

    def test_internal_links_and_assets_resolve(self):
        for slug in (*NEW, 'thanks-web', 'gracias'):
            soup = read(slug)
            for el in soup.select('[href], [src]'):
                raw = el.get('href', el.get('src'))
                url = urlsplit(raw)
                if url.scheme or url.netloc:
                    continue
                with self.subTest(page=slug, link=raw):
                    if not url.path:
                        self.assertIsNotNone(soup.find(id=unquote(url.fragment)))
                        continue
                    if url.path == '/book':
                        self.assertIn('/book ', (ROOT / '_redirects').read_text())
                        continue
                    path = ROOT / unquote(url.path.lstrip('/'))
                    candidates = [path, path.with_suffix('.html'), path / 'index.html']
                    self.assertTrue(any(p.is_file() for p in candidates), raw)

    def test_resource_strips(self):
        for name in ('index.html', 'framework/index.html', 'expertise/index.html',
                     'playbooks/index.html', 'writing.html'):
            soup = BeautifulSoup((ROOT/name).read_text(), 'html.parser')
            strip = soup.select('.resource-strip')
            self.assertEqual(len(strip), 1, name)
            self.assertEqual([a['href'] for a in strip[0].select('a')], ['/ghl', '/ai'])


if __name__ == '__main__':
    unittest.main()
