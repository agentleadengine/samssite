#!/usr/bin/env python3
"""Build the Case Studies section: index + the free-lead-engine case study.

Reuses the site's existing top nav and nav-behavior script by lifting them
straight out of work.html, rewriting relative paths to ../, and slotting a
"Case Studies" link in before "Writing". Diagrams use the site's sketch.js
hand-drawn grammar (box / arrow / bars / numberedSteps / compare).
"""
import re, pathlib

ROOT = pathlib.Path(__file__).parent
work = (ROOT / "work.html").read_text()

# --- Lift the nav block from work.html --------------------------------------
nav = work[work.index('<nav class="topbar">'): work.index('</nav>') + len('</nav>')]

def add_rel(html):
    # Prefix ../ to any relative href/src (skip absolute, anchor, mailto, already-../)
    return re.sub(r'(href|src)="(?!https?:|//|/|#|\.\./|mailto:)', r'\1="../', html)

nav = add_rel(nav)
# Idempotent: work.html may already carry the Case Studies link (injected into
# the root pages). Only add it if the lifted nav does not already have it.
if '../case-studies/index.html' not in nav:
    nav = nav.replace(
        '<a href="../writing.html" class="nav-link">Writing</a>',
        '<a href="../case-studies/index.html" class="nav-link">Case Studies</a>\n'
        '<a href="../writing.html" class="nav-link">Writing</a>'
    )

# --- Lift the nav-behavior script (no paths inside, reuse verbatim) ----------
anchor = work.index('const OPEN_DELAY')
js_start = work.rfind('<script>', 0, anchor)
js_end = work.index('</script>', anchor) + len('</script>')
navscript = work[js_start:js_end]

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900'
         '&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500'
         '&family=Kalam:wght@400;700&family=Caveat:wght@500;700&display=swap" rel="stylesheet">')

def head(title, desc, canon, og_img="https://samuelochoa.com/sam-hero.png", ld=""):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="author" content="Samuel Ochoa">
<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:site_name" content="Samuel Ochoa">
{FONTS}
<link rel="stylesheet" href="../styles.css">
<link rel="icon" type="image/png" href="../logo.png">
<script defer src="../js/sketch.js"></script>
<script defer src="../js/translate.js"></script>
<link rel="canonical" href="{canon}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{og_img}">
<meta name="theme-color" content="#4a00e0">
<meta name="robots" content="index,follow,max-image-preview:large">
{ld}
</head>
<body>'''

FOOT = ('</div></div><footer><div class="container">'
        '<p>&copy; 2026 Samuel Ochoa &middot; '
        '<a href="https://www.linkedin.com/in/samuelochoa" target="_blank" rel="noopener">LinkedIn</a> &middot; '
        '<a href="../case-studies/index.html">Case Studies</a> &middot; '
        '<a href="../framework/index.html">Framework</a></p>'
        '</div></footer>')

# ===========================================================================
#  CASE STUDY: the free lead engine
# ===========================================================================
CS_LD = '''<script type="application/ld+json">{"@context":"https://schema.org","@type":"Article","headline":"The free lead engine | Samuel Ochoa","description":"How I wired LeadScrape, Reoon, Claude, and Instantly into one autonomous outbound pipeline that scrapes leads for nothing, qualifies them with AI, and runs itself.","author":{"@type":"Person","name":"Samuel Ochoa","url":"https://samuelochoa.com/about.html"},"publisher":{"@type":"Person","name":"Samuel Ochoa","logo":{"@type":"ImageObject","url":"https://samuelochoa.com/logo.png"}},"mainEntityOfPage":"https://samuelochoa.com/case-studies/free-lead-engine.html","image":"https://samuelochoa.com/sam-hero.png"}</script>
<script type="application/ld+json">{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":"https://samuelochoa.com/"},{"@type":"ListItem","position":2,"name":"Case Studies","item":"https://samuelochoa.com/case-studies/"},{"@type":"ListItem","position":3,"name":"The free lead engine","item":"https://samuelochoa.com/case-studies/free-lead-engine.html"}]}</script>'''

CS_BODY = r'''<div class="container"><div class="page">
<p class="eyebrow" style="color:var(--primary-purple); font-weight:700; letter-spacing:0.15em; text-transform:uppercase; font-size:13px; margin-bottom:10px;"><a href="index.html" style="color:inherit;">Case studies</a> / The free lead engine</p>
<h1 class="title">The free lead engine</h1>
<p class="lede">I wired four cheap tools into one pipeline that scrapes leads for nothing, throws most of them away on purpose, and emails the rest. Then I handed the whole thing to a bot so I would stop touching it. Here is how it fits together.</p>

<h2>The problem with outbound</h2>
<p>Cold outbound is mostly janitorial work. You find the people, you check that their emails are real, you decide who is actually worth contacting, you write the first line, and then you babysit the sender so it does not torch your domain. None of those steps are hard. They are just slow, and the usual fix is to pay a different tool for each one and a person to run the seams between them.</p>
<p>I wanted to see how much of that I could move into software end to end. Scrape, verify, qualify, send, and manage. The constraint I gave myself was simple. The acquisition cost per lead should round to zero, and the judgment work should be done by a model, not by me.</p>

<h2>The shape of it</h2>
<p>Five stages, one direction. Each stage hands a smaller, cleaner list to the next. The first four build and send the list. The fifth one runs the whole thing on a schedule so it keeps going without me.</p>

<div class="sketch" data-viewbox="0 0 960 230" id="dg-pipeline">
  <svg></svg>
  <div class="sketch-caption">~ the whole pipeline, one row ~</div>
</div>
<script>
document.addEventListener('sketch:ready', function() {
  var wrap = document.getElementById('dg-pipeline');
  if (!wrap || wrap.dataset.drawn) return;
  wrap.dataset.drawn = '1';
  var svg = wrap.querySelector('svg');
  var rc = sketch.rc(svg);
  var stages = [
    { x: 20,  title: 'LeadScrape', sub: 'scrape, $0',     dim: 'leadscrape.com' },
    { x: 210, title: 'Reoon',      sub: 'verify',          dim: 'email check' },
    { x: 400, title: 'Claude',     sub: 'qualify + write',  dim: 'ICP rubric' },
    { x: 590, title: 'Instantly',  sub: 'send',             dim: 'warm inboxes' },
    { x: 780, title: 'The bot',    sub: 'run + iterate',    dim: 'daily cron' }
  ];
  stages.forEach(function(s) {
    sketch.box(svg, rc, { x: s.x, y: 60, w: 150, h: 104, title: s.title, sub: s.sub,
      dim: s.dim, titleY: 46, subY: 74, titleSize: 19, subSize: 12 });
  });
  for (var i = 0; i < stages.length - 1; i++) {
    sketch.arrow(svg, rc, { x1: stages[i].x + 150, x2: stages[i+1].x, y: 112, bidirectional: false });
  }
});
</script>

<h2>Step 1. Scrape for free</h2>
<p>The front of the pipeline is <a href="https://leadscrape.com" target="_blank" rel="noopener nofollow">LeadScrape</a>. You point it at a niche and a geography, say independent insurance agencies in a handful of states, and it pulls a list of businesses with names, websites, role titles, and contact emails. The acquisition cost per record is effectively nothing.</p>
<p>What comes out is raw and messy. Plenty of role addresses, plenty of dead inboxes, plenty of companies that are nothing like who I want to reach. That is fine. The whole point of the next three stages is to be ruthless about throwing this list away.</p>

<h2>Step 2. Verify before you trust</h2>
<p>Every raw email goes through <a href="https://reoon.com" target="_blank" rel="noopener nofollow">Reoon</a> before anything else happens to it. Reoon checks whether the address actually accepts mail and flags the ones that do not, the catch-all domains, and the disposable junk. Anything that is not cleanly deliverable gets dropped here.</p>
<div class="callout note"><strong>Why this step is not optional.</strong> Sending to addresses that bounce is the fastest way to wreck a sending domain. Verifying first protects the reputation of the inboxes that do the sending, which is the one asset in this whole system that is genuinely hard to replace.</div>

<h2>Step 3. Let Claude do the sorting</h2>
<p>This is the step that makes the pipeline worth building. A verified list is still just a pile of contacts. It does not know who fits and who does not, and it has no idea what to say to any of them. That judgment is the expensive part of outbound, and it is the part I wanted a model to own.</p>
<p>Each verified row goes to <a href="../framework/claude/index.html">Claude</a> with a short rubric that describes the ideal customer. Claude reads what is known about the lead, the company, the role, a snippet from their website, and does two things at once. It scores how well the lead fits the rubric, and for the ones that pass, it writes a specific opening line based on what it just read. The leads that do not fit are dropped with a reason.</p>

<div class="sketch" data-viewbox="0 0 920 320" id="dg-qualify">
  <svg></svg>
  <div class="sketch-caption">~ the qualification step, where most of the list gets thrown away ~</div>
</div>
<script>
document.addEventListener('sketch:ready', function() {
  var wrap = document.getElementById('dg-qualify');
  if (!wrap || wrap.dataset.drawn) return;
  wrap.dataset.drawn = '1';
  var svg = wrap.querySelector('svg');
  var rc = sketch.rc(svg);
  sketch.box(svg, rc, { x: 24, y: 110, w: 200, h: 110, title: 'Lead row', sub: 'name . site . role',
    titleY: 52, subY: 80, titleSize: 24, subSize: 14 });
  sketch.box(svg, rc, { x: 350, y: 88, w: 220, h: 152, title: 'Claude', sub: 'reads vs ICP rubric',
    titleY: 70, subY: 100, titleSize: 30, subSize: 15 });
  sketch.box(svg, rc, { x: 700, y: 36, w: 196, h: 100, title: 'Qualify', sub: 'score + first line',
    titleY: 46, subY: 72, titleSize: 24, subSize: 14,
    fillColor: '#ecfdf5', strokeColor: '#059669', textColor: '#047857', subColor: '#047857' });
  sketch.box(svg, rc, { x: 700, y: 196, w: 196, h: 100, title: 'Skip', sub: 'off-ICP, no send',
    titleY: 46, subY: 72, titleSize: 24, subSize: 14,
    fillColor: '#fef2f2', strokeColor: '#dc2626', textColor: '#b91c1c', subColor: '#b91c1c' });
  sketch.arrow(svg, rc, { x1: 224, x2: 350, y: 165, bidirectional: false });
  sketch.arrow(svg, rc, { x1: 570, y1: 150, x2: 700, y2: 92,  bidirectional: false, color: '#059669' });
  sketch.arrow(svg, rc, { x1: 570, y1: 182, x2: 700, y2: 240, bidirectional: false, color: '#dc2626' });
  sketch.note(svg, 285, 130, 'scores 1-5', { size: 14 });
});
</script>

<p>This is where the list collapses, and that is the goal. A verified address only tells you a message will arrive. The rubric tells you whether it should. By the time Claude is done, a list of thousands is a list of hundreds, and every survivor already has a first line written for it.</p>

<h2>What the list looks like at each stage</h2>
<p>Here is the attrition across one representative run. The shape matters more than the exact numbers. Most of what you scrape is supposed to disappear, and the biggest single cut is the qualification step, not the verifier.</p>

<div class="sketch" data-viewbox="0 0 920 300" id="dg-funnel">
  <svg></svg>
  <div class="sketch-caption">~ 10k scraped becomes 2.4k worth emailing ~</div>
</div>
<script>
document.addEventListener('sketch:ready', function() {
  var wrap = document.getElementById('dg-funnel');
  if (!wrap || wrap.dataset.drawn) return;
  wrap.dataset.drawn = '1';
  var svg = wrap.querySelector('svg');
  var rc = sketch.rc(svg);
  sketch.bars(svg, rc, {
    x: 24, y: 40, w: 880, barH: 42, gap: 26, labelW: 230, max: 11800,
    items: [
      { label: 'Scraped',            value: 10000, note: '10,000 raw' },
      { label: 'Deliverable',        value: 6800,  note: '6,800 pass Reoon' },
      { label: 'Fits the ICP',       value: 3100,  note: '3,100 pass Claude' },
      { label: 'One per domain, sent', value: 2400, note: '2,400 emailed' }
    ]
  });
});
</script>

<h2>Step 4. Send through Instantly</h2>
<p>The survivors, now verified, qualified, and each carrying their own opening line, get uploaded into <a href="../expertise/cold-email/index.html">Instantly</a>. The sending is spread across a pool of warmed inboxes so no single mailbox carries too much volume, and each lead enters a short sequence rather than a one-shot blast. Because the personalization was written upstream by Claude, every first email is specific to the person receiving it without anyone sitting there typing.</p>

<h2>Step 5. A second bot runs it</h2>
<p>The pipeline so far builds and sends a list. The last piece is what keeps it alive. A second agent runs on a schedule and does the operator job that a person would otherwise do by hand. It reads the campaign stats, decides what needs to change, makes the change, and routes anything that looks like a real reply to me.</p>

<div class="sketch" data-viewbox="0 0 920 240" id="dg-loop">
  <svg></svg>
  <div class="sketch-caption">~ the bot that babysits the campaigns, every morning ~</div>
</div>
<script>
document.addEventListener('sketch:ready', function() {
  var wrap = document.getElementById('dg-loop');
  if (!wrap || wrap.dataset.drawn) return;
  wrap.dataset.drawn = '1';
  var svg = wrap.querySelector('svg');
  var rc = sketch.rc(svg);
  sketch.numberedSteps(svg, rc, {
    x: 40, y: 86, w: 840, radius: 30, direction: 'h',
    items: [
      { title: 'Read stats',   sub: 'opens, replies, bounces' },
      { title: 'Decide',       sub: 'pause / rotate / iterate' },
      { title: 'Act',          sub: 'edit the campaigns' },
      { title: 'Route replies', sub: 'hand off the hot ones' }
    ]
  });
  sketch.note(svg, 460, 210, 'repeats daily, copy gets rewritten weekly', { size: 16 });
});
</script>

<p>Day to day it is reading numbers and making small corrections. Pause an inbox that is bouncing, rotate sending volume, push a lead into a follow-up step. Once a week it does the bigger job of rewriting the copy based on what actually got replies. The leverage is that the boring, daily, easy-to-skip work gets done every single day, because nobody has to remember to do it.</p>

<h2>Why bother building it this way</h2>
<p>The usual outbound stack pays for the same five jobs with four subscriptions and a person. This one moves the judgment into a model and the operations into a scheduled agent, and the only real recurring cost is the per-check verification and the model calls.</p>

<div class="sketch" data-viewbox="0 0 920 300" id="dg-compare">
  <svg></svg>
  <div class="sketch-caption">~ same output, a fraction of the stack ~</div>
</div>
<script>
document.addEventListener('sketch:ready', function() {
  var wrap = document.getElementById('dg-compare');
  if (!wrap || wrap.dataset.drawn) return;
  wrap.dataset.drawn = '1';
  var svg = wrap.querySelector('svg');
  var rc = sketch.rc(svg);
  sketch.compare(svg, rc, {
    x: 24, y: 30, w: 872, h: 240,
    left: {
      title: 'The usual stack',
      items: [
        'A data seat, ZoomInfo or Apollo',
        'Paid list exports per pull',
        'A separate email verifier',
        'A VA to sort and personalize',
        'Hundreds a month, at the floor'
      ]
    },
    right: {
      title: 'This pipeline',
      items: [
        'LeadScrape, free tier',
        'Reoon, pay per check',
        'Claude does the sorting',
        'Instantly plus one agent',
        'Runs while you sleep'
      ]
    }
  });
});
</script>

<p>The real takeaway is not the specific tools. It is that the two expensive parts of outbound, the judgment about who is worth contacting and the discipline to run the campaigns every day, are both things software can now do well. Once you accept that, the rest is plumbing.</p>

<div class="callout insight"><strong>Honest notes.</strong> The numbers above are from a representative run, not a client testimonial, and I built this for my own outbound. Deliverability still depends on real inbox warmup and clean list hygiene, no pipeline fixes a bad domain. And AI qualification is a filter, not a guarantee. It makes the list much better, it does not promise a reply.</div>

<div class="contact-card">
  <h3>Want one like it?</h3>
  <p>If you are drowning in the manual parts of outbound, this is the kind of system I build and hand over. Tell me your niche and what a good lead looks like, and I will tell you honestly whether a pipeline like this fits.</p>
  <a href="../contact.html" class="btn btn-primary">Tell me about your outbound</a>
</div>

<h2>Related reading</h2>
<div class="cards">
  <a href="../expertise/cold-email/index.html" class="card">
    <h3>Cold email, end to end</h3>
    <p>Infrastructure, deliverability, lists, copy, and sequences.</p>
  </a>
  <a href="../framework/patterns/multi-agent.html" class="card">
    <h3>Multi-agent orchestration</h3>
    <p>When splitting work across agents actually pays off.</p>
  </a>
  <a href="../framework/autonomous/scheduling.html" class="card">
    <h3>Scheduling autonomous agents</h3>
    <p>How a bot ends up running something every morning.</p>
  </a>
  <a href="../ai-consulting.html" class="card">
    <h3>Work with me</h3>
    <p>Advisory and build engagements on systems like this one.</p>
  </a>
</div>
'''

case_study = head(
    "The free lead engine | Samuel Ochoa",
    "How I wired LeadScrape, Reoon, Claude, and Instantly into one autonomous outbound pipeline that scrapes leads for nothing, qualifies them with AI, and runs itself.",
    "https://samuelochoa.com/case-studies/free-lead-engine.html",
    ld=CS_LD,
) + nav + CS_BODY + FOOT + navscript + "</body></html>"
(ROOT / "case-studies" / "free-lead-engine.html").write_text(case_study)

# ===========================================================================
#  INDEX: case studies landing
# ===========================================================================
IDX_LD = '''<script type="application/ld+json">{"@context":"https://schema.org","@type":"CollectionPage","name":"Case studies | Samuel Ochoa","description":"Systems I have built and run. Real architectures, honest write-ups, hand-drawn diagrams.","url":"https://samuelochoa.com/case-studies/"}</script>'''

IDX_BODY = r'''<section class="hero hero-compact" style="padding:60px 0 36px;">
<div class="container">
<p class="eyebrow" style="color:var(--primary-purple); font-weight:700; letter-spacing:0.15em; text-transform:uppercase; font-size:13px;">Case studies</p>
<h1 style="margin:12px 0 16px;">Systems I have built and run.</h1>
<p class="lead" style="max-width:720px;">Not polished client logos. Just real architectures I put together, written up honestly, with the same hand-drawn diagrams I use to think them through. Every write-up is something I actually run, and the numbers are from real runs, not a sales deck.</p>
</div>
</section>
<div class="container"><div class="page" style="padding-top:24px;">
<div class="cards">
  <a href="free-lead-engine.html" class="card">
    <h3>The free lead engine</h3>
    <p>LeadScrape to Reoon to Claude to Instantly. An outbound pipeline that scrapes leads for nothing, qualifies them with AI, and then runs itself through a second bot. Four diagrams of how it fits together.</p>
  </a>
</div>
<div class="callout note" style="margin-top:40px;"><strong>More on the way.</strong> I write these up as I build them. If there is a system you want walked through in this much detail, <a href="../contact.html">say so</a> and it might be the next one.</div>
</div></div>'''

# Index lives one level deep too, so the lifted ../ nav and footer work as-is.
index_page = head(
    "Case studies | Samuel Ochoa",
    "Systems I have built and run. Real architectures, honest write-ups, and hand-drawn diagrams, starting with the free lead engine.",
    "https://samuelochoa.com/case-studies/",
    ld=IDX_LD,
) + nav + IDX_BODY + FOOT + navscript + "</body></html>"
(ROOT / "case-studies" / "index.html").write_text(index_page)

print("wrote case-studies/index.html and case-studies/free-lead-engine.html")
