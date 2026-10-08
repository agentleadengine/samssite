#!/usr/bin/env python3
"""Rebuild the site-wide top nav: fresh markup + init JS on every HTML page.

Replaces whatever <nav class="topbar">...</nav> block currently exists and the
nav-init <script> block that was previously injected.

Nav layout (2026-10-08 restructure, one consistent menu on every page):
    Home   Agent Care   Queva   Working with me   About   Contact
The library (framework, expertise, playbooks, ...) is reached from the footer.
Also replaces the <footer>...</footer> block with the standard footer.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

NAV_ITEMS = [
    ("Home", "index.html"),
    ("Agent Care", "agent/index.html"),
    ("Queva", "queva/index.html"),
    ("Working with me", "work.html"),
    ("About", "about.html"),
    ("Contact", "contact.html"),
]

FOOTER_ITEMS = [
    ("Testimonials", "testimonials.html"),
    ("Library", "framework/index.html"),
    ("Uses", "uses.html"),
    ("Privacy", "privacy.html"),
    ("Terms", "terms.html"),
    ("Español", "es/index.html"),
]


def rel_prefix(html_path: Path) -> str:
    rel = html_path.relative_to(ROOT)
    depth = len(rel.parts) - 1
    return "../" * depth


def build_nav(R: str) -> str:
    lines = [
        '<nav class="topbar"><div class="topbar-inner">',
        f'<a href="{R}index.html" class="logo"><img class="brand-logo" src="{R}logo.png" alt="Samuel Ochoa"></a>',
        '<button class="hamburger" type="button" aria-label="Toggle menu" aria-expanded="false"><span></span><span></span><span></span></button>',
        '<div class="nav-links">',
    ]
    lines += [f'<a href="{R}{href}" class="nav-link">{label}</a>' for label, href in NAV_ITEMS]
    lines.append('</div>')  # nav-links
    lines.append('</div></nav>')
    return "\n".join(lines)


def build_footer(R: str) -> str:
    links = " &middot; ".join(f'<a href="{R}{href}">{label}</a>' for label, href in FOOTER_ITEMS)
    return ('<footer><div class="container">\n'
            f'<p>&copy; 2026 Samuel Ochoa &middot; {links} &middot; '
            '<a href="https://www.linkedin.com/in/samuelochoa" target="_blank" rel="noopener">LinkedIn</a></p>\n'
            '<p>Agent Care is run by my company, Agent Lead Engine LLC &middot; '
            '<a href="mailto:sam@samuelochoa.com">sam@samuelochoa.com</a></p>\n'
            '</div></footer>')


NAV_SCRIPT = """<script>
(function(){
  const bar = document.querySelector('nav.topbar');
  if (!bar || bar.dataset.navInit) return;
  bar.dataset.navInit = '1';

  const OPEN_DELAY = 120;   // ms - hover intent
  const CLOSE_DELAY = 450;  // ms - forgiving close
  const isMobile = () => window.matchMedia('(max-width: 960px)').matches;

  const hamb = bar.querySelector('.hamburger');
  const links = bar.querySelector('.nav-links');
  const groups = Array.from(bar.querySelectorAll('.nav-group'));

  // --- Mobile hamburger ---------------------------------------------------
  if (hamb && links) {
    hamb.addEventListener('click', function(e) {
      e.stopPropagation();
      const open = bar.classList.toggle('nav-open');
      hamb.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // --- Per-group hover-intent open/close ---------------------------------
  groups.forEach(function(group) {
    let openTimer = null;
    let closeTimer = null;

    const open = () => {
      clearTimeout(closeTimer); closeTimer = null;
      if (openTimer) return;
      openTimer = setTimeout(() => {
        groups.forEach(g => { if (g !== group) g.classList.remove('is-open'); });
        group.classList.add('is-open');
        openTimer = null;
      }, OPEN_DELAY);
    };
    const close = () => {
      clearTimeout(openTimer); openTimer = null;
      clearTimeout(closeTimer);
      closeTimer = setTimeout(() => {
        group.classList.remove('is-open');
        closeTimer = null;
      }, CLOSE_DELAY);
    };
    const cancelClose = () => { clearTimeout(closeTimer); closeTimer = null; };

    // Keyboard focus opens the same desktop menu without requiring hover.
    group.addEventListener('focusin', () => {
      if (isMobile()) return;
      clearTimeout(closeTimer);
      groups.forEach(g => { if (g !== group) g.classList.remove('is-open'); });
      group.classList.add('is-open');
    });
    group.addEventListener('focusout', (e) => {
      if (!isMobile() && !group.contains(e.relatedTarget)) {
        clearTimeout(openTimer); openTimer = null;
        group.classList.remove('is-open');
      }
    });

    // Desktop: hover opens, mouseleave closes after delay
    group.addEventListener('mouseenter', () => { if (!isMobile()) open(); });
    group.addEventListener('mouseleave', () => { if (!isMobile()) close(); });
    // If cursor re-enters while closing, cancel the close
    group.addEventListener('pointerenter', () => { if (!isMobile()) cancelClose(); });

    // Click trigger: mobile toggles accordion; desktop follows the link
    const trigger = group.querySelector('.nav-has-submenu');
    if (trigger) {
      trigger.addEventListener('click', function(e) {
        if (isMobile()) {
          e.preventDefault();
          const wasOpen = group.classList.contains('is-open');
          groups.forEach(g => g.classList.remove('is-open'));
          if (!wasOpen) group.classList.add('is-open');
        }
      });
    }
  });

  // --- Mega menu (legacy): swap right-panel content on category hover -----
  // No-op now that Resources is a simple dropdown, but harmless if any
  // mega markup lingers on a not-yet-rebuilt page.
  const megaCats = bar.querySelectorAll('.nav-mega-cats .nav-cat');
  const megaPanels = bar.querySelectorAll('.nav-mega-content .nav-cat-panel');
  let catTimer = null;
  megaCats.forEach(function(cat) {
    cat.addEventListener('mouseenter', function() {
      clearTimeout(catTimer);
      const id = cat.dataset.cat;
      catTimer = setTimeout(() => {
        megaCats.forEach(c => c.classList.toggle('is-active', c.dataset.cat === id));
        megaPanels.forEach(p => p.classList.toggle('is-active', p.dataset.cat === id));
      }, 80); // snappier than top-level hover intent
    });
  });

  // --- Close menu when a leaf link is clicked ----------------------------
  if (links) {
    links.querySelectorAll('a').forEach(function(a) {
      if (a.classList.contains('nav-has-submenu')) return;
      if (a.classList.contains('nav-cat')) return; // cat label also navigates, but don't auto-close
      a.addEventListener('click', function() {
        bar.classList.remove('nav-open');
        if (hamb) hamb.setAttribute('aria-expanded', 'false');
        groups.forEach(g => g.classList.remove('is-open'));
      });
    });
  }

  // --- Close on outside click ---------------------------------------------
  document.addEventListener('click', function(e) {
    if (!bar.contains(e.target)) {
      bar.classList.remove('nav-open');
      if (hamb) hamb.setAttribute('aria-expanded', 'false');
      groups.forEach(g => g.classList.remove('is-open'));
    }
  });

  // --- Escape key closes everything ---------------------------------------
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      const focusedGroup = groups.find(g => g.contains(document.activeElement));
      if (focusedGroup) focusedGroup.querySelector('.nav-has-submenu').focus();
      bar.classList.remove('nav-open');
      if (hamb) hamb.setAttribute('aria-expanded', 'false');
      groups.forEach(g => g.classList.remove('is-open'));
    }
  });
})();
</script>"""


# Matches the full <nav class="topbar">...</nav> block, greedy across newlines.
NAV_RE = re.compile(r'<nav\s+class="topbar">.*?</nav>', re.DOTALL | re.IGNORECASE)
FOOTER_RE = re.compile(r'<footer\b.*?</footer>', re.DOTALL | re.IGNORECASE)

# Matches the existing nav-init <script>...</script> block.
# The script we previously injected contains the unique phrase "dataset.navInit".
SCRIPT_RE = re.compile(r'<script>\s*\(function\(\)\{[^<]*?dataset\.navInit[\s\S]*?</script>', re.IGNORECASE)

replaced_nav = 0
replaced_script = 0
scanned = 0

for html in sorted(ROOT.rglob("*.html")):
    rel = html.relative_to(ROOT)
    scanned += 1
    text = html.read_text(encoding="utf-8")
    orig = text
    if not NAV_RE.search(text):
        continue

    R = rel_prefix(html)
    new_nav = build_nav(R)

    if NAV_RE.search(text):
        text = NAV_RE.sub(lambda _m: new_nav, text, count=1)
        if text != orig:
            replaced_nav += 1

    text = FOOTER_RE.sub(lambda _m: build_footer(R), text, count=1)

    # Replace any existing nav-init script.
    if SCRIPT_RE.search(text):
        text = SCRIPT_RE.sub(lambda _m: NAV_SCRIPT, text, count=1)
        replaced_script += 1
    else:
        # Inject nav script before </body> if no init script exists yet
        if "</body>" in text and "dataset.navInit" not in text:
            text = text.replace("</body>", NAV_SCRIPT + "\n</body>", 1)
            replaced_script += 1

    if text != orig:
        html.write_text(text, encoding="utf-8")

print(f"Scanned: {scanned} | nav replaced: {replaced_nav} | script replaced: {replaced_script}")
