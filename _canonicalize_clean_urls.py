#!/usr/bin/env python3
"""
Make clean (no-.html) URLs the canonical form across the site.

What it does:
  - HTML files: strip a trailing ".html" from the <link rel="canonical"> href
    and the <meta property="og:url"> content. Directory indexes (".../") and
    the site root ("https://samuelochoa.com/") are already clean and untouched.
  - sitemap.xml: same cleaning on every <loc>, and drop the /404.html entry
    (a 404 page should never be in a sitemap).

Netlify serves every "page.html" at the clean "/page" path (verified 200), so
pointing canonicals/sitemap at the clean URLs is safe.

Idempotent: safe to re-run any time, including after a full site rebuild.
Run from anywhere:  python3 _canonicalize_clean_urls.py
"""
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
DOMAIN = "https://samuelochoa.com"


def clean_url(url):
    """Strip .html from a same-domain URL; leave dir-slash and root alone."""
    if not url.startswith(DOMAIN):
        return url
    path = url[len(DOMAIN):]
    if path == "/index.html":
        path = "/"
    elif path.endswith("/index.html"):
        path = path[: -len("index.html")]   # keep the trailing slash
    elif path.endswith(".html"):
        path = path[: -len(".html")]
    return DOMAIN + path


def _fix_tag(match):
    tag = match.group(0)
    if 'rel="canonical"' in tag:
        tag = re.sub(r'href="([^"]+)"',
                     lambda m: 'href="%s"' % clean_url(m.group(1)), tag)
    if 'property="og:url"' in tag:
        tag = re.sub(r'content="([^"]+)"',
                     lambda m: 'content="%s"' % clean_url(m.group(1)), tag)
    return tag


def process_html(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
    except UnicodeDecodeError:
        print("  SKIP (not utf-8):", path)
        return False
    new = re.sub(r"<link\b[^>]*>", _fix_tag, html)
    new = re.sub(r"<meta\b[^>]*>", _fix_tag, new)
    if new != html:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new)
        return True
    return False


def process_sitemap(path):
    with open(path, "r", encoding="utf-8") as f:
        xml = f.read()
    # Drop the 404 entry entirely (single-line <url>...</url> block).
    xml = re.sub(r"\s*<url><loc>%s/404\.html</loc>.*?</url>" % re.escape(DOMAIN),
                 "", xml)
    # Clean every remaining <loc>.
    xml = re.sub(r"<loc>([^<]+)</loc>",
                 lambda m: "<loc>%s</loc>" % clean_url(m.group(1)), xml)
    with open(path, "w", encoding="utf-8") as f:
        f.write(xml)


def main():
    changed = 0
    for dirpath, _dirs, files in os.walk(ROOT):
        if os.sep + ".git" in dirpath:
            continue
        for name in files:
            if name.endswith(".html"):
                if process_html(os.path.join(dirpath, name)):
                    changed += 1
    print("HTML files updated:", changed)

    sitemap = os.path.join(ROOT, "sitemap.xml")
    if os.path.exists(sitemap):
        process_sitemap(sitemap)
        print("sitemap.xml cleaned")


if __name__ == "__main__":
    main()
