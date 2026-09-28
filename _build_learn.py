#!/usr/bin/env python3
"""Build the owner track: learn/owners/*.html from body fragments.

Each lesson's article body lives in learn/_content/<slug>.html (lede, sections,
claims, lesson task, and a <div class="further-reading"> sources block).
This script wraps it in the shared lesson shell: sidebar custody line,
breadcrumbs, record strip, prev/next. Then run python3 _rebuild_nav.py
to stamp the site nav and footer.

    python3 _build_learn.py && python3 _rebuild_nav.py
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "learn" / "_content"
OUT = ROOT / "learn" / "owners"
CHECKED = "28 Sep 2026"
CHECKED_ISO = "2026-09-28"

# (slug, title, one-line summary)
LESSONS = [
    ("what-ai-can-do", "What AI can and cannot do for a small business", "The honest starting point: where AI saves real time, where it fails, and the one habit that keeps you safe."),
    ("pick-an-assistant", "Pick one assistant for the office", "ChatGPT, Claude, Gemini, or Copilot. How to choose one for the whole team, based on the tools you already use."),
    ("what-it-costs", "What AI costs a small business in 2026", "Real plan prices, what the business tiers add, and a simple budget for a five-person office."),
    ("first-five-tasks", "Five tasks to hand AI this week", "Five low-risk, high-return jobs to start with, with a prompt for each."),
    ("how-to-ask", "How to ask so you get usable work", "The four things every good request includes, and how to fix a bad first answer."),
    ("check-before-you-trust", "What to check before you trust the output", "A two-minute checklist for names, numbers, promises, and anything you would not want quoted back to you."),
    ("customer-data", "Keep customer data safe", "What each plan does with what you type, which setting to change today, and what never to paste."),
    ("the-rules", "The rules that apply to you", "Plain facts about the FTC, state AI laws, and disclosures. Not legal advice, but what to ask your lawyer about."),
    ("roll-it-out", "Roll it out to your team", "How to get a small team using one tool well: one owner, one shared prompt list, one weekly check."),
    ("when-to-automate", "When a task is ready to run on its own", "The signs a task can move from chat to automation or an agent, and the guardrails to put in first."),
    ("ai-in-your-office-suite", "Use AI inside Google Workspace or Microsoft 365", "Turn on and use the AI already in the email, documents, and meetings your team opens every day, step by step."),
    ("marketing-without-sounding-like-ai", "Marketing posts that do not sound like AI", "A human-first way to use AI for posts, emails, and offers, starting from real customer words and facts you can prove."),
    ("ai-for-missed-calls", "AI for phones and missed calls", "Turn voicemails into a short callback list, and keep urgent, sensitive, and uncertain calls with a person."),
    ("meeting-notes", "Meeting notes and call summaries you can trust", "Use AI notes for meetings and calls, with consent, a quick accuracy check, and clear owners for every next step."),
    ("spot-ai-scams", "Spot AI scams and fake invoices", "The verification habits that stop voice clones, deepfake messages, and fake invoices aimed at small businesses."),
    ("reviews-and-replies", "Reviews and reputation replies", "Draft calm, specific replies to public reviews with AI, and know which reviews a person must handle."),
]


def words(text: str) -> int:
    return len(re.sub(r"<[^>]+>", " ", text).split())


def sidebar(active: str) -> str:
    items = [f'<li><a href="index.html"{" class=\"active\"" if active == "index" else ""}>Overview</a></li>']
    for i, (slug, title, _) in enumerate(LESSONS, 1):
        cls = ' class="active"' if slug == active else ""
        items.append(f'<li><a href="{slug}.html"{cls}>{i:02d} · {html.escape(title)}</a></li>')
    return ('<aside class="framework-sidebar" aria-label="Owner track lessons"><h4>The owner track</h4><ul>'
            + "".join(items) + '</ul><h4>Also</h4><ul><li><a href="../index.html">Start here</a></li>'
            '<li><a href="../../framework/index.html">The builder track</a></li><li><a href="../changes.html">Change log</a></li>'
            '<li><a href="../../newsletter.html">Daily AI brief</a></li></ul></aside>')


def head(title: str, desc: str, path: str, depth: int) -> str:
    R = "../" * depth
    t = html.escape(title)
    d = html.escape(desc)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{t} | Samuel Ochoa</title>
<meta name="description" content="{d}">
<meta name="author" content="Samuel Ochoa">
<link rel="canonical" href="https://samuelochoa.com/{path}">
<meta property="og:type" content="article">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="https://samuelochoa.com/{path}">
<meta property="og:image" content="https://samuelochoa.com/sam-real.jpg">
<meta property="og:site_name" content="Samuel Ochoa">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#f3ecdd">
<link rel="icon" type="image/png" href="{R}logo.png">
<link href="https://fonts.googleapis.com/css2?family=Gloock&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{R}styles.css?v=20260928">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"Article","headline":{json.dumps(title)},"description":{json.dumps(desc)},"dateModified":"{CHECKED_ISO}","author":{{"@type":"Person","name":"Samuel Ochoa","url":"https://samuelochoa.com/about"}}}}</script>
<script defer src="{R}js/translate.js"></script>
<script type="text/javascript">
(function(c,l,a,r,i,t,y){{
    c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};
    t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
    y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
}})(window, document, "clarity", "script", "x9tyuivf47");
</script>
</head>
<body><a class="skip-link" href="#main">Skip to content</a><nav class="topbar"></nav>"""


def lesson_page(i: int) -> str:
    slug, title, summary = LESSONS[i]
    body = (SRC / f"{slug}.html").read_text(encoding="utf-8").strip()
    minutes = max(2, round(words(body) / 230))
    prev_ = LESSONS[i - 1] if i > 0 else None
    next_ = LESSONS[i + 1] if i + 1 < len(LESSONS) else None
    pn = '<div class="prev-next">'
    pn += (f'<a href="{prev_[0]}.html" class="prev"><div class="label">Previous</div><div class="title">{html.escape(prev_[1])}</div></a>'
           if prev_ else '<a href="index.html" class="prev"><div class="label">Track</div><div class="title">Owner track overview</div></a>')
    pn += (f'<a href="{next_[0]}.html" class="next"><div class="label">Next</div><div class="title">{html.escape(next_[1])}</div></a>'
           if next_ else '<a href="../../framework/index.html" class="next"><div class="label">Next</div><div class="title">Ready to build? The builder track</div></a>')
    pn += "</div>"
    record = (f'<dl class="record is-owner"><div class="rec-item"><dt>Track</dt><dd>Owners · lesson {i + 1:02d} of {len(LESSONS)}</dd></div>'
              f'<div class="rec-item"><dt>Reading time</dt><dd>{minutes} min</dd></div>'
              f'<div class="rec-item"><dt>Last checked</dt><dd><time datetime="{CHECKED_ISO}">{CHECKED}</time></dd></div>'
              f'<div class="rec-item"><dt>Marks</dt><dd><span class="status">Checked</span> <span class="status is-take">My take</span></dd></div><span class="rec-stamp" aria-hidden="true"></span></dl>')
    return (head(title, summary, f"learn/owners/{slug}", 2)
            + f'<div class="framework-layout">{sidebar(slug)}<main class="framework-content" id="main">'
            + '<div class="breadcrumbs"><a href="../../index.html">Home</a><span class="sep">›</span>'
            + '<a href="../index.html">Learn</a><span class="sep">›</span><a href="index.html">Owner track</a>'
            + f'<span class="sep">›</span><span>Lesson {i + 1:02d}</span></div>'
            + f'<h1 class="title">{html.escape(title)}</h1>{record}\n{body}\n{pn}</main></div>'
            + '<footer></footer><script defer src="../../js/site.js"></script></body></html>\n')


def index_page() -> str:
    rows = []
    for i, (slug, title, summary) in enumerate(LESSONS, 1):
        src = SRC / f"{slug}.html"
        mins = f"{max(2, round(words(src.read_text(encoding='utf-8')) / 230))} min" if src.exists() else ""
        rows.append(f'<li><a href="{slug}.html"><span class="hub-title">{i:02d} · {html.escape(title)}</span>'
                    f'<span class="hub-desc">{html.escape(summary)}</span><span class="hub-arrow"><small>{mins}</small></span></a></li>')
    body = f"""<h1 class="title">The owner track</h1>
<dl class="record is-owner"><div class="rec-item"><dt>For</dt><dd>Owners and office staff</dd></div><div class="rec-item"><dt>Lessons</dt><dd>{len(LESSONS)}, about two hours in total</dd></div><div class="rec-item"><dt>Code</dt><dd>None</dd></div><div class="rec-item"><dt>Last checked</dt><dd><time datetime="{CHECKED_ISO}">{CHECKED}</time></dd></div></dl>
<p class="lede">Sixteen short lessons for people who run a small business or keep one running. By the end you will have one AI assistant set up for your office, five jobs it does every week, a way to check its work, and a clear picture of what it costs and what it does with your data.</p>
<p>Read them in order the first time. Each one ends with a small task you can do the same day. Every fact is marked: <span class="status">Checked</span> means I confirmed it in the official source on the date shown, and <span class="status is-take">My take</span> means it is my judgment from setting these tools up for real offices.</p>
<ul class="hub-list">{"".join(rows)}</ul>
<div class="callout note"><span class="callout-title">Want to go further?</span><p>When you are ready to connect AI to your own tools or build something that runs on its own, the <a href="../../framework/index.html">builder track</a> picks up where this one ends.</p></div>"""
    return (head("The owner track: AI for small-business owners", "Plain-English lessons for small-business owners and office staff: pick an assistant, know the costs, protect customer data, and check the work.", "learn/owners/", 2)
            + f'<div class="framework-layout">{sidebar("index")}<main class="framework-content" id="main">'
            + '<div class="breadcrumbs"><a href="../../index.html">Home</a><span class="sep">›</span><a href="../index.html">Learn</a><span class="sep">›</span><span>Owner track</span></div>'
            + body + '</main></div><footer></footer><script defer src="../../js/site.js"></script></body></html>\n')


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    built = 0
    for i, (slug, _, _) in enumerate(LESSONS):
        if (SRC / f"{slug}.html").exists():
            (OUT / f"{slug}.html").write_text(lesson_page(i), encoding="utf-8")
            built += 1
        else:
            print(f"  missing content: learn/_content/{slug}.html")
    (OUT / "index.html").write_text(index_page(), encoding="utf-8")
    print(f"built {built} lessons + index")


# ---------------------------------------------------------------------------
# Hub pages: learn/index.html (Start here), learn/library.html, learn/changes.html
# ---------------------------------------------------------------------------
def count(pattern: str) -> int:
    return sum(1 for p in ROOT.glob(pattern) if p.name != "index.html")


def hub_shell(title, desc, path, crumb, body):
    return (head(title, desc, path, 1)
            + '<main id="main">' + body + '</main><footer></footer><script defer src="../js/site.js"></script></body></html>\n')


def start_page() -> str:
    owner = "".join(f'<li><a href="owners/{s}.html">{html.escape(t)}</a></li>' for s, t, _ in LESSONS)
    body = f"""<section class="hero hero-compact"><div class="container">
<h1>Pick your road in.</h1>
<p class="lead">This library has two tracks that share one set of marks. If you run the business or keep the office going, start with owners. If you want to connect AI to your tools or build something that runs on its own, start with builders.</p>
</div></section>
<section class="block"><div class="container">
<div class="section-header"><h2 class="section-title">Which one is you?</h2></div>
<ul class="hub-list">
<li><a href="owners/index.html"><span class="hub-title">"I run the business and want AI to save my team time."</span><span class="hub-desc">The owner track. No code, short lessons, one task per lesson.</span><span class="hub-arrow"></span></a></li>
<li><a href="owners/index.html"><span class="hub-title">"I am the person everyone asks about the office tools."</span><span class="hub-desc">Owner track first for the ground rules, then MCP and Claude Code in the builder track.</span><span class="hub-arrow"></span></a></li>
<li><a href="../framework/index.html"><span class="hub-title">"I write code or build automations."</span><span class="hub-desc">The builder track: models, MCP, Claude Code, skills, subagents, and hands-on builds.</span><span class="hub-arrow"></span></a></li>
</ul>
</div></section>
<section class="block"><div class="container">
<div class="tracks">
<article class="track"><h3>The owner track</h3><span class="t-for">For owners and office staff</span><p>Sixteen short lessons. Pick an assistant, know the costs, protect customer data, check the work.</p><ol>{owner}</ol><div class="t-cta"><a class="btn-primary" href="owners/index.html">Start lesson 01</a></div></article>
<article class="track is-builder"><h3>The builder track</h3><span class="t-for">For people who build</span><p>The Framework: how the parts fit, then builds you can run.</p><ol>
<li><a href="../framework/what-is-autonomous-ai.html">What autonomous AI actually is</a></li>
<li><a href="../framework/claude/overview.html">Claude: the models and how to pick</a></li>
<li><a href="../framework/mcp/what-is-mcp.html">MCP: how AI reaches your tools</a></li>
<li><a href="../framework/claude-code/index.html">Claude Code: the harness</a></li>
<li><a href="../framework/claude-code/skills.html">Skills</a></li>
<li><a href="../framework/claude-code/subagents.html">Subagents</a></li>
<li><a href="../framework/build/first-agent.html">Build your first agent</a></li>
<li><a href="../framework/build/mcp-server.html">Build an MCP server</a></li>
</ol><div class="t-cta"><a class="btn-ghost" href="../framework/index.html">Open the framework</a></div></article>
<article class="track is-changing"><h3>The change log</h3><span class="t-for">Still changing</span><p>Every time I re-check a page, the date and what changed go here.</p><div class="t-cta"><a href="changes.html">Read the change log</a></div></article>
</div>
</div></section>"""
    return hub_shell("Start here: learn AI for real work", "Two tracks for learning AI at work: a plain-English owner track and a hands-on builder track.", "learn/", "Start here", body)


def library_page() -> str:
    topics = [
        ("expertise/agents/index.html", "AI agents"), ("expertise/rag/index.html", "RAG"), ("expertise/seo/index.html", "SEO"),
        ("expertise/paid-ads/index.html", "Paid ads"), ("expertise/cold-email/index.html", "Cold email"), ("expertise/email-marketing/index.html", "Email marketing"),
        ("expertise/growth-marketing/index.html", "Growth"), ("expertise/cro/index.html", "Conversion"), ("expertise/direct-response/index.html", "Direct response"),
        ("expertise/business-management/index.html", "Running a business"),
    ]
    pills = "".join(f'<a class="pill" href="../{h}">{t}</a>' for h, t in topics)
    rows = [
        ("framework/index.html", count("framework/**/*.html"), "lessons", "The Framework", "The builder handbook: Claude, MCP, plugins, Claude Code, agent patterns, going autonomous, and build guides."),
        ("learn/owners/index.html", len(LESSONS), "lessons", "The owner track", "Plain-English lessons for owners and office staff. No code."),
        ("expertise/index.html", count("expertise/**/*.html"), "pages", "Expertise libraries", "Ten deep libraries on AI and the business skills around it."),
        ("playbooks/index.html", count("playbooks/**/*.html"), "modules", "Industry playbooks", "Step-by-step AI playbooks for 15 kinds of business."),
        ("compare/index.html", count("compare/*.html"), "matchups", "Tool comparisons", "Head-to-head pages with a plain verdict."),
        ("glossary/index.html", count("glossary/*.html"), "terms", "Glossary", "Every term the library uses, explained simply."),
        ("writing.html", count("writing/*.html"), "essays", "Essays", "Longer pieces on systems, small business, and AI."),
    ]
    cat = "".join(f'<li><a href="../{h}"><span class="c-count">{n}<small>{u}</small></span><span class="c-name">{t}</span><span class="c-desc">{d}</span><span class="c-arrow" aria-hidden="true"></span></a></li>' for h, n, u, t, d in rows)
    body = f"""<section class="hero hero-compact"><div class="container"><h1>Everything in one place.</h1>
<p class="lead">About {sum(r[1] for r in rows):,} pages, free to read. AI pages carry a last-checked date; business pages are marked with when they were written.</p></div></section>
<section class="block"><div class="container"><ul class="catalog">{cat}</ul>
<div class="section-header" style="margin-top:56px"></div><div class="pills">{pills}</div></div></section>"""
    return hub_shell("The library", "Every section of samuelochoa.com: the Framework, the owner track, expertise libraries, playbooks, comparisons, glossary, and essays.", "learn/library", "Library", body)


def changes_page() -> str:
    entries = (SRC / "changes.html").read_text(encoding="utf-8") if (SRC / "changes.html").exists() else ""
    body = f"""<section class="hero hero-compact"><div class="container"><h1>What changed, and when.</h1>
<p class="lead">AI facts go stale. When I re-check a page, the date and what changed go here, newest first. If you spot something out of date, <a href="../contact.html">tell me</a>.</p></div></section>
<section class="block"><div class="container"><div class="framework-content" style="max-width:820px">{entries}</div></div></section>"""
    return hub_shell("Change log", "What changed in the samuelochoa.com AI library, and when it was last checked.", "learn/changes", "Change log", body)


if __name__ == "__main__":
    (ROOT / "learn" / "index.html").write_text(start_page(), encoding="utf-8")
    (ROOT / "learn" / "library.html").write_text(library_page(), encoding="utf-8")
    (ROOT / "learn" / "changes.html").write_text(changes_page(), encoding="utf-8")
    print("built learn/index.html, library.html, changes.html")
