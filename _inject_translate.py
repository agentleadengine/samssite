#!/usr/bin/env python3
"""
Inject the Spanish auto-translate widget into every HTML file in samssite.

Idempotent: re-running won't duplicate the <script> tag.

The script tag is inserted right after the existing `js/sketch.js` reference
so it inherits the same `defer` / loading pattern and the same relative-path
convention. The relative prefix is computed per file based on its depth from
the site root.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Match the existing sketch.js include at any relative depth so we can land
# our tag on the next line.
SKETCH_RE = re.compile(r'(<script[^>]*src="((?:\.\./)*)js/sketch\.js"[^>]*></script>)')

# Mark we've already injected — used for idempotency.
TRANSLATE_MARKER = 'js/translate.js'


def rel_prefix(html_path: Path) -> str:
    """Return the '../' chain needed to reach the site root from html_path."""
    depth = len(html_path.relative_to(ROOT).parts) - 1  # subtract the file itself
    return '../' * depth


def inject(html_path: Path) -> str:
    """Return 'added' | 'skipped' | 'no-anchor'."""
    text = html_path.read_text(encoding='utf-8')

    if TRANSLATE_MARKER in text:
        return 'skipped'

    match = SKETCH_RE.search(text)
    if not match:
        return 'no-anchor'

    prefix = rel_prefix(html_path)
    new_tag = f'<script defer src="{prefix}js/translate.js"></script>'
    # Place the new tag on its own line right after the sketch.js include.
    insertion = f'{match.group(1)}\n{new_tag}'
    new_text = text.replace(match.group(1), insertion, 1)

    html_path.write_text(new_text, encoding='utf-8')
    return 'added'


def main() -> int:
    added = skipped = missing = 0
    missing_paths: list[Path] = []

    for html in ROOT.rglob('*.html'):
        # Skip anything inside hidden dirs (.git, .well-known, .claude).
        if any(part.startswith('.') for part in html.relative_to(ROOT).parts):
            continue
        result = inject(html)
        if result == 'added':
            added += 1
        elif result == 'skipped':
            skipped += 1
        else:
            missing += 1
            missing_paths.append(html)

    print(f'Injected:  {added}')
    print(f'Skipped:   {skipped} (already had translate.js)')
    print(f'No-anchor: {missing} (no sketch.js tag found)')
    if missing_paths:
        print('\nFirst few files without a sketch.js anchor:')
        for p in missing_paths[:10]:
            print(f'  {p.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
