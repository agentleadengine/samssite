#!/usr/bin/env python3
"""Full-site audit: broken links, missing assets, duplicates, structural issues."""
import re
from pathlib import Path
from collections import defaultdict
from urllib.parse import urldefrag

ROOT = Path(__file__).resolve().parent

HREF_RE = re.compile(r'href\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
SRC_RE = re.compile(r'\bsrc\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
TITLE_RE = re.compile(r'<title>([^<]*)</title>', re.IGNORECASE)
META_DESC_RE = re.compile(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']*)["\']', re.IGNORECASE)

EXTERNAL = ("http://", "https://", "mailto:", "tel:", "javascript:", "data:", "#")

def is_external(link: str) -> bool:
    low = link.strip().lower()
    return low.startswith(EXTERNAL) or low == ""

# Netlify redirect sources count as valid targets (retired pages 301 to new ones).
REDIRECTS = set()
for line in (ROOT / "_redirects").read_text().splitlines():
    if line.strip() and not line.startswith("#"):
        REDIRECTS.add(line.split()[0].rstrip("*"))


class Target(type(Path())):
    pass


def resolve(page: Path, link: str) -> Path:
    link, _ = urldefrag(link)  # drop #fragment
    link = link.split("?", 1)[0]  # drop query
    if not link:
        return page
    if link.startswith("/"):
        if any(link == s or (s.endswith("/") and link.startswith(s)) for s in REDIRECTS):
            return page  # handled by _redirects
        target = (ROOT / link.lstrip("/")).resolve()
    else:
        target = (page.parent / link).resolve()
    # Netlify pretty URLs: /about -> about.html, /queva/ -> queva/index.html
    if not target.exists():
        for alt in (target.with_name(target.name + ".html"), target / "index.html"):
            if alt.exists():
                return alt
    elif target.is_dir() and (target / "index.html").exists():
        return target / "index.html"
    return target

# Collect pages
pages = sorted(ROOT.rglob("*.html"))

# Issue buckets
broken_links = defaultdict(list)   # page -> [(link, target)]
broken_assets = defaultdict(list)
missing_nav = []
missing_footer = []
missing_styles = []
missing_title = []
missing_meta_desc = []
duplicate_script = []
banned_content = defaultdict(list)
emdash_pages = []
duplicate_nav = []
empty_pages = []

# 2026-10-08: the old rule "no Agent Lead Engine mentions" is retired (10-03
# decision: this site may name and link to agentleadengine.com). The list
# below is the restructure's retired-offer and jargon list. It is enforced on
# the core pages; the 1,100-page library is reported, not enforced.
BANNED = ["Yardi", "my team", "$497", "$249", "free setup", "plus about", "720 support minutes",
          "provider funding", "leak check", "snapshot", "GHL", "cold call", "daily AI brief",
          "DigitalOcean", "captainslog", "Assistant Home", "Group classes", "serial entrepreneur"]
CORE = {"index.html", "agent/index.html", "queva/index.html", "work.html", "about.html", "contact.html",
        "now.html", "links.html", "es/index.html", "terms.html", "privacy.html", "testimonials.html",
        "uses.html", "404.html", "agent/thanks/index.html"}
core_fail = []

total_pages = 0
total_links_checked = 0
total_assets_checked = 0

for p in pages:
    total_pages += 1
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        empty_pages.append(p)
        continue

    if len(text) < 100:
        empty_pages.append(p)
        continue

    # Structural checks
    if '<nav class="topbar">' not in text:
        missing_nav.append(p)
    elif text.count('<nav class="topbar">') > 1:
        duplicate_nav.append(p)

    if '<footer' not in text.lower():
        missing_footer.append(p)

    if 'styles.css' not in text:
        missing_styles.append(p)

    if not TITLE_RE.search(text):
        missing_title.append(p)
    if not META_DESC_RE.search(text):
        missing_meta_desc.append(p)

    if text.count('bar.dataset.navInit') > 2:
        # normal = 2 (check + set). more = duplicated script
        duplicate_script.append(p)

    # Banned content (visible text only, so the Clarity/gtag scripts do not count)
    import re as _re
    visible = _re.sub(r'(?s)<(script|style)\b.*?</\1>', '', text)
    tl = visible.lower()
    rel = p.relative_to(ROOT).as_posix()
    for phrase in BANNED:
        hit = phrase in visible if phrase.isupper() else phrase.lower() in tl
        if hit:
            banned_content[phrase].append(p)
            if rel in CORE:
                core_fail.append(f"{rel}: banned phrase {phrase!r}")

    # Em-dashes (user hates them)
    if '\u2014' in text or '\u2013' in text:
        emdash_pages.append(p)
        if rel in CORE:
            core_fail.append(f"{rel}: em or en dash")

    # Link checks
    for m in HREF_RE.finditer(text):
        link = m.group(1)
        if is_external(link):
            continue
        total_links_checked += 1
        target = resolve(p, link)
        if not target.exists():
            if p.relative_to(ROOT).as_posix() in CORE:
                core_fail.append(f"{p.relative_to(ROOT).as_posix()}: broken link {link}")
            broken_links[str(p.relative_to(ROOT))].append((link, str(target.relative_to(ROOT) if str(target).startswith(str(ROOT)) else target)))

    # Asset checks
    for m in SRC_RE.finditer(text):
        link = m.group(1)
        if is_external(link):
            continue
        total_assets_checked += 1
        target = resolve(p, link)
        if not target.exists():
            broken_assets[str(p.relative_to(ROOT))].append(link)

# ============ REPORT ============
print("=" * 70)
print(f"FULL SITE AUDIT - {total_pages} HTML pages")
print("=" * 70)
print(f"Links checked:  {total_links_checked:,}")
print(f"Assets checked: {total_assets_checked:,}")

print("\n--- STRUCTURAL ISSUES ---")
print(f"Pages missing nav:        {len(missing_nav)}")
print(f"Pages with duplicate nav: {len(duplicate_nav)}")
print(f"Pages missing footer:     {len(missing_footer)}")
print(f"Pages missing styles.css: {len(missing_styles)}")
print(f"Pages missing <title>:    {len(missing_title)}")
print(f"Pages missing meta desc:  {len(missing_meta_desc)}")
print(f"Pages with duplicate init script: {len(duplicate_script)}")
print(f"Empty/tiny pages:         {len(empty_pages)}")

print("\n--- CONTENT HYGIENE ---")
print(f"Pages containing em-dash (- or -): {len(emdash_pages)}")
for phrase in BANNED:
    hits = banned_content[phrase]
    print(f"Pages containing banned phrase {phrase!r}: {len(hits)}")

print("\n--- BROKEN LINKS (internal only) ---")
total_broken = sum(len(v) for v in broken_links.values())
print(f"Pages with broken links: {len(broken_links)}")
print(f"Total broken link instances: {total_broken}")

if broken_links:
    # Group by target type
    link_targets = defaultdict(int)
    for page, links in broken_links.items():
        for link, target in links:
            link_targets[link] += 1
    print("\nTop 30 unique broken link targets:")
    for link, count in sorted(link_targets.items(), key=lambda x: -x[1])[:30]:
        print(f"  ({count:4d}x)  {link}")

print("\n--- BROKEN ASSETS (img/src) ---")
total_assets_broken = sum(len(v) for v in broken_assets.values())
print(f"Pages with broken assets: {len(broken_assets)}")
print(f"Total broken asset instances: {total_assets_broken}")
if broken_assets:
    asset_counts = defaultdict(int)
    for page, assets in broken_assets.items():
        for a in assets:
            asset_counts[a] += 1
    print("\nTop 20 unique broken asset paths:")
    for a, count in sorted(asset_counts.items(), key=lambda x: -x[1])[:20]:
        print(f"  ({count:4d}x)  {a}")

# Sample pages with structural problems
def show_samples(label, lst, n=6):
    if not lst:
        return
    print(f"\n{label} - samples:")
    for p in lst[:n]:
        print(f"  {p.relative_to(ROOT)}")

show_samples("Pages missing nav", missing_nav)
show_samples("Pages with duplicate nav", duplicate_nav)
show_samples("Pages missing footer", missing_footer)
show_samples("Pages missing styles.css", missing_styles)
show_samples("Pages missing title", missing_title)
show_samples("Pages missing meta description", missing_meta_desc)
show_samples("Pages with duplicate init script", duplicate_script)
show_samples("Empty pages", empty_pages)

if emdash_pages:
    print(f"\nEm-dash samples (first 6):")
    for p in emdash_pages[:6]:
        print(f"  {p.relative_to(ROOT)}")

for phrase in BANNED:
    hits = banned_content[phrase]
    if hits:
        print(f"\nBanned phrase {phrase!r} found on (first 6):")
        for p in hits[:6]:
            print(f"  {p.relative_to(ROOT)}")

# Sitemap entries must exist (directly or via a pretty URL) and not be redirected away.
import re as _re
sitemap_missing = []
for loc in _re.findall(r"<loc>https://samuelochoa.com(.*?)</loc>", (ROOT / "sitemap.xml").read_text()):
    path = loc or "/"
    if path in REDIRECTS or not resolve(ROOT / "index.html", path).exists():
        sitemap_missing.append(path)
print(f"\nSitemap URLs missing or redirected: {len(sitemap_missing)} {sitemap_missing[:10]}")
core_fail += [f"sitemap: {s}" for s in sitemap_missing]

print("\n--- CORE PAGE GATE ---")
for f in core_fail:
    print("FAIL", f)
print("CORE GATE:", "PASS" if not core_fail else f"FAIL ({len(core_fail)})")
print("AUDIT COMPLETE")
raise SystemExit(1 if core_fail else 0)
