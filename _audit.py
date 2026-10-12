#!/usr/bin/env python3
"""Full-site audit: broken links, missing assets, duplicates, structural issues."""
import re
from pathlib import Path
from collections import defaultdict
from urllib.parse import urldefrag

ROOT = Path("/Users/ble/Desktop/sams site")

HREF_RE = re.compile(r'href\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
SRC_RE = re.compile(r'\bsrc\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
TITLE_RE = re.compile(r'<title>([^<]*)</title>', re.IGNORECASE)
META_DESC_RE = re.compile(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']*)["\']', re.IGNORECASE)

EXTERNAL = ("http://", "https://", "mailto:", "tel:", "javascript:", "data:", "#")

def is_external(link: str) -> bool:
    low = link.strip().lower()
    return low.startswith(EXTERNAL) or low == ""

def resolve(page: Path, link: str) -> Path:
    link, _ = urldefrag(link)  # drop #fragment
    link = link.split("?", 1)[0]  # drop query
    if not link:
        return page
    base = page.parent
    target = (base / link).resolve()
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

BANNED = ["agent lead engine", "Yardi", "I run ", "my team", "currently running"]

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

    # Banned content
    tl = text.lower()
    for phrase in BANNED:
        if phrase.lower() in tl:
            banned_content[phrase].append(p)

    # Em-dashes (user hates them)
    if '-' in text or '-' in text:
        emdash_pages.append(p)

    # Link checks
    for m in HREF_RE.finditer(text):
        link = m.group(1)
        if is_external(link):
            continue
        total_links_checked += 1
        target = resolve(p, link)
        if not target.exists():
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

print("\n=" * 35)
print("AUDIT COMPLETE")
