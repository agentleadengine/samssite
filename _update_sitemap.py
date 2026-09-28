#!/usr/bin/env python3
"""Add missing pages to sitemap.xml and bump <lastmod> for pages changed vs origin/main.

    python3 _update_sitemap.py [YYYY-MM-DD]
"""
import re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TODAY = sys.argv[1] if len(sys.argv) > 1 else "2026-09-28"
SKIP = {"demos", "tests", "completed", ".impeccable", ".agent"}
NOINDEX = {"404.html", "thanks.html", "thanks-ai.html", "thanks-ghl.html", "thanks-web.html", "gracias.html", "links.html"}


def url_for(p: Path) -> str:
    rel = p.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return "https://samuelochoa.com/"
    if rel.endswith("/index.html"):
        return "https://samuelochoa.com/" + rel[: -len("index.html")]
    return "https://samuelochoa.com/" + rel[: -len(".html")]


sm = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
changed = set(subprocess.run(["git", "diff", "--name-only", "origin/main"], cwd=ROOT, capture_output=True, text=True).stdout.split())
changed |= set(subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT, capture_output=True, text=True).stdout.split())
added = bumped = 0
for p in sorted(ROOT.rglob("*.html")):
    parts = p.relative_to(ROOT).parts
    if parts[0] in SKIP or any(x.startswith("_") for x in parts) or p.name in NOINDEX:
        continue
    if 'name="robots" content="noindex' in p.read_text(encoding="utf-8", errors="ignore"):
        continue
    u = url_for(p)
    rel = p.relative_to(ROOT).as_posix()
    if f"<loc>{u}</loc>" not in sm:
        prio = "0.9" if rel.startswith("learn/") else "0.7"
        sm = sm.replace("</urlset>", f"  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod><changefreq>monthly</changefreq><priority>{prio}</priority></url>\n</urlset>")
        added += 1
    elif rel in changed:
        sm, n = re.subn(rf"(<loc>{re.escape(u)}</loc><lastmod>)[^<]*", rf"\g<1>{TODAY}", sm)
        bumped += n
(ROOT / "sitemap.xml").write_text(sm, encoding="utf-8")
print(f"sitemap: added {added}, lastmod bumped {bumped}")
