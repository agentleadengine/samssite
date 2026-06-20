#!/usr/bin/env python3
"""Inject the Microsoft Clarity analytics snippet into every page (idempotent).

Adds the Clarity tag (project x9tyuivf47) right before </head> on every HTML
page that does not already have it. Safe to re-run after adding new pages.
"""
from pathlib import Path

ROOT = Path("/Users/ale/Desktop/samssite")
PROJECT_ID = "x9tyuivf47"

SNIPPET = """<script type="text/javascript">
(function(c,l,a,r,i,t,y){
    c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
    t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
    y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
})(window, document, "clarity", "script", "%s");
</script>
""" % PROJECT_ID

added = skipped = scanned = 0
for html in sorted(ROOT.rglob("*.html")):
    scanned += 1
    text = html.read_text(encoding="utf-8")
    if "clarity.ms/tag" in text or "</head>" not in text:
        skipped += 1
        continue
    new = text.replace("</head>", SNIPPET + "</head>", 1)
    if new != text:
        html.write_text(new, encoding="utf-8")
        added += 1

print(f"Scanned: {scanned} | clarity added: {added} | skipped: {skipped}")
