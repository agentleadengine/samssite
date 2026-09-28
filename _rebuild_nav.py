#!/usr/bin/env python3
"""Stamp the site shell (design v2, 2026-09-28) onto every non-demo page.

Idempotent. For each HTML page outside demos/:
  - replaces <nav class="topbar">...</nav> with the learning-first nav
  - replaces the nav-init <script> with NAV_SCRIPT
  - replaces the plain site <footer> with the colophon footer
  - swaps the Google Fonts link for the v2 faces (Gloock, Source Serif 4, JetBrains Mono)
  - pins styles.css to CSS_VERSION and adds js/site.js
  - strips legacy inline purple styling and v1 per-template <style> blocks
Run this after ANY _build_*.py generator: generators still emit the v1 shell.

Nav:  Start here · Owners · Builders · Library v · Daily brief · About · [Get help]
Run:  python3 _rebuild_nav.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CSS_VERSION = "20260929"
SITE_CHECKED = "28 Sep 2026"
HELP_URL = "https://agentleadengine.com/"
LINKEDIN = "https://www.linkedin.com/in/samuelochoa"

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Gloock&family=Source+Serif+4:ital,opsz,wght@0,8..60,400..700;1,8..60,400..600'
         '&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">')

SKIP_DIRS = {"demos", ".impeccable", "node_modules", "tests"}


def count(pattern: str) -> int:
    return sum(1 for p in ROOT.glob(pattern) if p.name != "index.html")


LIBRARY = [
    ("The Framework", "framework/index.html", count("framework/**/*.html")),
    ("Expertise libraries", "expertise/index.html", count("expertise/**/*.html")),
    ("Industry playbooks", "playbooks/index.html", count("playbooks/**/*.html")),
    ("Tool comparisons", "compare/index.html", count("compare/*.html")),
    ("Glossary", "glossary/index.html", count("glossary/*.html")),
    ("Essays", "writing.html", count("writing/*.html")),
    ("GHL snapshots", "snapshots.html", 0),
]


def rel_prefix(html_path: Path) -> str:
    return "../" * (len(html_path.relative_to(ROOT).parts) - 1)


def build_nav(R: str) -> str:
    lib = "\n".join(
        f'<a href="{R}{href}">{label}' + (f' <small>{n}</small>' if n else "") + "</a>"
        for label, href, n in LIBRARY
    )
    return "\n".join([
        '<nav class="topbar" aria-label="Main"><div class="topbar-inner">',
        f'<a href="{R}index.html" class="logo"><img class="brand-logo" src="{R}images/so-mark.png" alt="" width="33" height="42">'
        '<span class="brand-word">Samuel Ochoa<small>AI at work, checked</small></span></a>',
        '<button class="hamburger" type="button" aria-label="Toggle menu" aria-expanded="false"><span></span><span></span><span></span></button>',
        '<div class="nav-links">',
        f'<a href="{R}learn/index.html" class="nav-link">Start here</a>',
        f'<a href="{R}learn/owners/index.html" class="nav-link">Owners</a>',
        f'<a href="{R}framework/index.html" class="nav-link">Builders</a>',
        '<div class="nav-group">',
        f'<a href="{R}learn/library.html" class="nav-link nav-has-submenu">Library</a>',
        '<div class="nav-submenu">',
        lib,
        '</div></div>',
        f'<a href="{R}about.html" class="nav-link">About</a>',
        f'<a href="{HELP_URL}" class="nav-link nav-quiet">Get help</a>',
        '<a href="#" class="nav-link nav-lang" data-lang-toggle>Español</a>',
        f'<a href="{R}newsletter.html" class="nav-link nav-cta">Daily brief</a>',
        '</div>',
        '</div></nav>',
    ])


def build_footer(R: str) -> str:
    return f"""<footer class="site-footer"><div class="container">
<div class="foot-grid">
<div class="foot-brand"><img src="{R}images/so-mark.png" alt="" width="44" height="56"><div><strong>Samuel Ochoa</strong><p>A free library for learning AI at work. Plain English, dated, and checked by someone who sets these tools up for real small businesses.</p></div></div>
<div><h4>Learn</h4><ul><li><a href="{R}learn/index.html">Start here</a></li><li><a href="{R}learn/owners/index.html">Owner track</a></li><li><a href="{R}framework/index.html">Builder track</a></li><li><a href="{R}newsletter.html">Daily AI brief</a></li></ul></div>
<div><h4>Library</h4><ul><li><a href="{R}framework/index.html">Framework</a></li><li><a href="{R}expertise/index.html">Expertise</a></li><li><a href="{R}playbooks/index.html">Playbooks</a></li><li><a href="{R}compare/index.html">Comparisons</a></li><li><a href="{R}glossary/index.html">Glossary</a></li><li><a href="{R}writing.html">Essays</a></li></ul></div>
<div><h4>Sam</h4><ul><li><a href="{R}about.html">About</a></li><li><a href="{R}testimonials.html">Testimonials</a></li><li><a href="{R}contact.html">Contact</a></li><li><a href="{HELP_URL}">Get help setting it up</a></li><li><a href="{LINKEDIN}" rel="noopener">LinkedIn</a></li></ul></div>
</div>
<div class="foot-colophon"><span>&copy; 2026 Samuel Ochoa &middot; <a href="{R}privacy.html">Privacy</a> &middot; <a href="{R}terms.html">Terms</a></span><span class="status">Library last checked {SITE_CHECKED}</span></div>
</div></footer>"""


NAV_SCRIPT = """<script>
(function(){
  const bar = document.querySelector('nav.topbar');
  if (!bar || bar.dataset.navInit) return;
  bar.dataset.navInit = '1';
  const OPEN_DELAY = 120, CLOSE_DELAY = 400;
  const isMobile = () => window.matchMedia('(max-width: 1000px)').matches;
  const hamb = bar.querySelector('.hamburger');
  const links = bar.querySelector('.nav-links');
  const groups = Array.from(bar.querySelectorAll('.nav-group'));
  const here = location.pathname.replace(/index\\.html$/, '').replace(/\\.html$/, '');
  let best = null, bestLen = 0;
  bar.querySelectorAll('.nav-links > a:not([data-lang-toggle]), .nav-group > a').forEach(function(a){
    const p = new URL(a.href, location.href).pathname.replace(/index\\.html$/, '').replace(/\\.html$/, '');
    if (p !== '/' && here.indexOf(p) === 0 && p.length > bestLen) { best = a; bestLen = p.length; }
  });
  if (best) best.setAttribute('aria-current', 'page');
  if (hamb && links) hamb.addEventListener('click', function(e){
    e.stopPropagation();
    const open = bar.classList.toggle('nav-open');
    hamb.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  groups.forEach(function(group){
    let openT = null, closeT = null;
    const open = () => { clearTimeout(closeT); if (openT) return; openT = setTimeout(() => { groups.forEach(g => g !== group && g.classList.remove('is-open')); group.classList.add('is-open'); openT = null; }, OPEN_DELAY); };
    const close = () => { clearTimeout(openT); openT = null; clearTimeout(closeT); closeT = setTimeout(() => group.classList.remove('is-open'), CLOSE_DELAY); };
    group.addEventListener('mouseenter', () => { if (!isMobile()) open(); });
    group.addEventListener('mouseleave', () => { if (!isMobile()) close(); });
    group.addEventListener('focusin', () => { if (!isMobile()) { clearTimeout(closeT); group.classList.add('is-open'); } });
    group.addEventListener('focusout', (e) => { if (!isMobile() && !group.contains(e.relatedTarget)) group.classList.remove('is-open'); });
    const trigger = group.querySelector('.nav-has-submenu');
    if (trigger) trigger.addEventListener('click', function(e){
      if (isMobile()) { e.preventDefault(); const was = group.classList.contains('is-open'); groups.forEach(g => g.classList.remove('is-open')); if (!was) group.classList.add('is-open'); }
    });
  });
  document.addEventListener('click', function(e){
    if (!bar.contains(e.target)) { bar.classList.remove('nav-open'); if (hamb) hamb.setAttribute('aria-expanded', 'false'); groups.forEach(g => g.classList.remove('is-open')); }
  });
  document.addEventListener('keydown', function(e){
    if (e.key === 'Escape') { bar.classList.remove('nav-open'); if (hamb) hamb.setAttribute('aria-expanded', 'false'); groups.forEach(g => g.classList.remove('is-open')); }
  });
})();
</script>"""

NAV_RE = re.compile(r'<nav\s+class="topbar"[^>]*>.*?</nav>', re.S | re.I)
SCRIPT_RE = re.compile(r'<script>\s*\(function\(\)\{[^<]*?dataset\.navInit[\s\S]*?</script>', re.I)
FOOTER_RE = re.compile(r'<footer(?:\s+class="site-footer")?>.*?</footer>', re.S)
FONTS_RE = re.compile(r'(?:<link rel="preconnect" href="https://fonts\.(?:googleapis|gstatic)\.com"(?: crossorigin)?>\s*)*<link[^>]+href="https://fonts\.googleapis\.com/css2[^"]*"[^>]*>')
CSS_RE = re.compile(r'(href="(?:\.\./)*styles\.css)(?:\?v=\d+)?"')
H1_INLINE_RE = re.compile(r'(<h1 class="title") style="[^"]*"')
BACK_RE = re.compile(r'<a href="index\.html" style="color:#4a00e0; text-decoration: none; font-size: 14px;">')
LEGACY_STYLE_RE = re.compile(r'\n?<style[^>]*>\s*(/\* Playbook-specific styles \*/|\.gloss-layout \{|\.cmp-layout \{|\.essay \{).*?</style>', re.S)
TOPIC_RE = re.compile(r'(<span class="(?:gloss|cmp)-topic") style="margin-top: \d+px;"')


PURPLE = {"#4a00e0": "#7b0f14", "#5a1fe0": "#7b0f14", "#6d28d9": "#7b0f14", "#4514b2": "#7b0f14",
          "#7c3aed": "#a1171c", "#8b5cf6": "#a1171c", "#a78bfa": "#c8343a",
          "#f3f0ff": "#faf6ec", "#f7f4fc": "#faf6ec", "#f5f3ff": "#faf6ec", "#ede9fe": "#f0e6d8", "#faf5ff": "#faf6ec"}
PURPLE_RE = re.compile("|".join(PURPLE), re.I)
STYLE_ATTR_RE = re.compile(r'style="[^"]*"')
STYLE_BLOCK_RE = re.compile(r'<style[^>]*>.*?</style>', re.S)


def recolor(text: str) -> str:
    """Re-ink legacy purple inside inline style attributes and <style> blocks only."""
    fix = lambda m: PURPLE_RE.sub(lambda c: PURPLE[c.group(0).lower()], m.group(0))
    text = STYLE_ATTR_RE.sub(fix, text)
    text = STYLE_BLOCK_RE.sub(fix, text)
    text = text.replace(' style="color:#7b0f14; font-weight:600;"', "")
    # glyph arrows -> CSS SVG arrows
    text = text.replace('<div class="label">← Previous</div>', '<div class="label">Previous</div>')
    text = text.replace('<div class="label">Next →</div>', '<div class="label">Next</div>')
    text = text.replace('<div class="label">← Track</div>', '<div class="label">Track</div>')
    text = re.sub(r'(<a href="[^"]*" class="back-link">)← ', r'\1', text)
    text = re.sub(r'<meta name="theme-color" content="#[0-9a-fA-F]{6}">', '<meta name="theme-color" content="#f3ecdd">', text)
    return text


def stamp(html: Path) -> bool:
    text = html.read_text(encoding="utf-8")
    orig = text
    R = rel_prefix(html)
    if NAV_RE.search(text):
        text = NAV_RE.sub(lambda _m: build_nav(R), text, count=1)
        if SCRIPT_RE.search(text):
            text = SCRIPT_RE.sub(lambda _m: NAV_SCRIPT, text, count=1)
        elif "</body>" in text:
            text = text.replace("</body>", NAV_SCRIPT + "\n</body>", 1)
        if FOOTER_RE.search(text):
            text = FOOTER_RE.sub(lambda _m: build_footer(R), text, count=1)
    if "styles.css" in text:
        text = FONTS_RE.sub(lambda _m: FONTS, text, count=1) if FONTS_RE.search(text) else text.replace("</head>", FONTS + "\n</head>", 1)
        text = CSS_RE.sub(lambda m: f'{m.group(1)}?v={CSS_VERSION}"', text)
        if "js/site.js" not in text:
            text = text.replace("</body>", f'<script defer src="{R}js/site.js"></script>\n</body>', 1)
    text = H1_INLINE_RE.sub(r"\1", text)
    text = BACK_RE.sub('<a href="index.html" class="back-link">', text)
    text = TOPIC_RE.sub(r"\1", text)
    text = LEGACY_STYLE_RE.sub("", text)  # generators still emit v1 template styles
    text = recolor(text)
    if text != orig:
        html.write_text(text, encoding="utf-8")
        return True
    return False


if __name__ == "__main__":
    changed = scanned = 0
    for html in sorted(ROOT.rglob("*.html")):
        parts = html.relative_to(ROOT).parts
        if parts[0] in SKIP_DIRS or any(x.startswith('_') for x in parts):
            continue
        scanned += 1
        changed += stamp(html)
    print(f"scanned {scanned} pages, changed {changed}")
