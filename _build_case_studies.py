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
#  CASE STUDY: calls that file themselves (GHL -> Whisper -> GHL)
# ===========================================================================
VOICE_LD = '''<script type="application/ld+json">{"@context":"https://schema.org","@type":"Article","headline":"Calls that file themselves | Samuel Ochoa","description":"A GHL to Whisper to GHL loop. Dialer call recordings get transcribed locally with Whisper, qualified from the transcript, and written back into GoHighLevel so the right automation fires.","author":{"@type":"Person","name":"Samuel Ochoa","url":"https://samuelochoa.com/about.html"},"publisher":{"@type":"Person","name":"Samuel Ochoa","logo":{"@type":"ImageObject","url":"https://samuelochoa.com/logo.png"}},"mainEntityOfPage":"https://samuelochoa.com/case-studies/voice-intake.html","image":"https://samuelochoa.com/sam-hero.png"}</script>
<script type="application/ld+json">{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":"https://samuelochoa.com/"},{"@type":"ListItem","position":2,"name":"Case Studies","item":"https://samuelochoa.com/case-studies/"},{"@type":"ListItem","position":3,"name":"Calls that file themselves","item":"https://samuelochoa.com/case-studies/voice-intake.html"}]}</script>'''

VOICE_BODY = r'''<div class="container"><div class="page">
<p class="eyebrow" style="color:var(--primary-purple); font-weight:700; letter-spacing:0.15em; text-transform:uppercase; font-size:13px; margin-bottom:10px;"><a href="index.html" style="color:inherit;">Case studies</a> / Calls that file themselves</p>
<h1 class="title">Calls that file themselves</h1>
<p class="lede">A dialer makes hundreds of calls a day and records every one. The useful part, who is hot, who said call back, who is a dead end, is locked inside the audio. This is the loop I built to get it out. GoHighLevel hands off the recording, Whisper transcribes it on a machine I own, a model qualifies the transcript, and the answer gets written straight back into GHL so the right automation fires. Nobody has to listen to the calls.</p>

<h2>The problem with call recordings</h2>
<p>Every dialer produces the same thing at the end of the day. A long list of recordings nobody has time to play back. The signal you actually want is in there, but it is trapped in audio, and audio is slow. Someone has to listen, decide what the call was, and update the CRM by hand. That last mile is where the follow-up dies. The hot lead who asked for a quote at 2pm does not get tagged until tomorrow, if at all.</p>
<p>I did not want to replace the dialer or the CRM. Both already work. I wanted to close the gap between them, the part where a human listens to a call and types in what happened, and let software do that part instead.</p>

<h2>The shape of it</h2>
<p>It is a round trip. GoHighLevel sends the recording out, the transcription and the judgment happen on a local machine, and the result comes back into GoHighLevel as a tag the automations can see. Three hops, and the middle one never leaves my own hardware.</p>

<div class="sketch" data-viewbox="0 0 960 250" id="dg-voice-loop">
  <svg></svg>
  <div class="sketch-caption">~ ghl out, whisper and qualify in the middle, ghl back in ~</div>
</div>
<script>
document.addEventListener('sketch:ready', function() {
  var wrap = document.getElementById('dg-voice-loop');
  if (!wrap || wrap.dataset.drawn) return;
  wrap.dataset.drawn = '1';
  var svg = wrap.querySelector('svg');
  var rc = sketch.rc(svg);
  var stages = [
    { x: 20,  title: 'GHL',        sub: 'call recorded',  dim: 'the dialer' },
    { x: 210, title: 'Whisper',    sub: 'transcribe',     dim: 'local box', local: true },
    { x: 400, title: 'Qualify',    sub: 'read + score',   dim: 'the transcript', local: true },
    { x: 590, title: 'GHL',        sub: 'tag + field',    dim: 'written back' },
    { x: 780, title: 'Automation', sub: 'right workflow', dim: 'fires in GHL', go: true }
  ];
  stages.forEach(function(s) {
    var o = { x: s.x, y: 70, w: 150, h: 104, title: s.title, sub: s.sub, dim: s.dim,
      titleY: 46, subY: 74, titleSize: 19, subSize: 12 };
    if (s.local) { o.fillColor = '#fff7ed'; o.strokeColor = '#d97706'; o.textColor = '#b45309'; o.subColor = '#b45309'; }
    if (s.go)    { o.fillColor = '#ecfdf5'; o.strokeColor = '#059669'; o.textColor = '#047857'; o.subColor = '#047857'; }
    sketch.box(svg, rc, o);
  });
  for (var i = 0; i < stages.length - 1; i++) {
    sketch.arrow(svg, rc, { x1: stages[i].x + 150, x2: stages[i+1].x, y: 122, bidirectional: false });
  }
  sketch.note(svg, 380, 234, 'this middle runs locally, no audio leaves', { size: 15 });
});
</script>

<h2>Step 1. GHL hands off the recording</h2>
<p>The dialer logs each call in GoHighLevel with the recording attached, which it already does. When a call wraps, a webhook fires and sends that recording to a small worker running on my own machine. Nothing about the existing setup changes. The dialer keeps dialing, GHL keeps logging, and the only new thing is that the audio now has somewhere to go.</p>

<h2>Step 2. Whisper transcribes it locally</h2>
<p>The worker runs <a href="https://github.com/openai/whisper" target="_blank" rel="noopener nofollow">Whisper</a> on the machine itself, not through a paid API. It takes the recording and turns it into text. Running it locally matters for two reasons. The recordings never leave my environment, and the transcription cost does not scale with call volume, because there is no per-minute meter running.</p>
<div class="callout note"><strong>Why local and not a cloud API.</strong> Transcription is the highest-volume step in the whole loop, one job per call, every call. Paying per minute for that adds up fast, and it means shipping customer call audio to a third party. Whisper on a box you own removes both problems at once.</div>

<h2>Step 3. Qualify the transcript</h2>
<p>A transcript on its own is just text. The judgment is deciding what the call actually was. The worker hands the transcript to <a href="../framework/claude/index.html">Claude</a> with a short rubric, and it returns three things. A disposition, what kind of call this was. A one line summary, so a human can scan it without listening. And the next action, what should happen to this lead now.</p>

<div class="sketch" data-viewbox="0 0 920 340" id="dg-voice-qualify">
  <svg></svg>
  <div class="sketch-caption">~ one call, read and routed in seconds ~</div>
</div>
<script>
document.addEventListener('sketch:ready', function() {
  var wrap = document.getElementById('dg-voice-qualify');
  if (!wrap || wrap.dataset.drawn) return;
  wrap.dataset.drawn = '1';
  var svg = wrap.querySelector('svg');
  var rc = sketch.rc(svg);
  sketch.box(svg, rc, { x: 24, y: 120, w: 190, h: 100, title: 'Transcript', sub: 'what was said',
    titleY: 46, subY: 74, titleSize: 23, subSize: 14 });
  sketch.box(svg, rc, { x: 350, y: 95, w: 210, h: 150, title: 'Claude', sub: 'reads + decides',
    titleY: 70, subY: 100, titleSize: 30, subSize: 15 });
  sketch.box(svg, rc, { x: 700, y: 24, w: 196, h: 84, title: 'Hot', sub: 'book a call',
    titleY: 40, subY: 64, titleSize: 22, subSize: 13,
    fillColor: '#ecfdf5', strokeColor: '#059669', textColor: '#047857', subColor: '#047857' });
  sketch.box(svg, rc, { x: 700, y: 128, w: 196, h: 84, title: 'Nurture', sub: 'into a sequence',
    titleY: 40, subY: 64, titleSize: 22, subSize: 13,
    fillColor: '#fffbeb', strokeColor: '#d97706', textColor: '#b45309', subColor: '#b45309' });
  sketch.box(svg, rc, { x: 700, y: 232, w: 196, h: 84, title: 'Not now', sub: 'suppress + tag',
    titleY: 40, subY: 64, titleSize: 22, subSize: 13,
    fillColor: '#fef2f2', strokeColor: '#dc2626', textColor: '#b91c1c', subColor: '#b91c1c' });
  sketch.arrow(svg, rc, { x1: 214, x2: 350, y: 170, bidirectional: false });
  sketch.arrow(svg, rc, { x1: 560, y1: 140, x2: 700, y2: 66,  bidirectional: false, color: '#059669' });
  sketch.arrow(svg, rc, { x1: 560, y1: 170, x2: 700, y2: 170, bidirectional: false, color: '#d97706' });
  sketch.arrow(svg, rc, { x1: 560, y1: 200, x2: 700, y2: 274, bidirectional: false, color: '#dc2626' });
  sketch.note(svg, 283, 152, 'one of three', { size: 14 });
});
</script>

<p>The disposition is the important output, because it is the thing the next step can act on. Everything else, the summary and the notes, is there so a person can trust the call without playing it back.</p>

<h2>Step 4. Write it back into GHL</h2>
<p>The worker writes the result onto the contact in GoHighLevel through the API. The disposition becomes a tag, the summary goes into a field, and that is the whole trick. A tag is something GHL automations can trigger on. The moment it lands, the CRM knows what the call was, in the same place it keeps everything else.</p>

<div class="sketch" data-viewbox="0 0 920 290" id="dg-voice-table">
  <svg></svg>
  <div class="sketch-caption">~ the disposition map, transcript signal to the right workflow ~</div>
</div>
<script>
document.addEventListener('sketch:ready', function() {
  var wrap = document.getElementById('dg-voice-table');
  if (!wrap || wrap.dataset.drawn) return;
  wrap.dataset.drawn = '1';
  var svg = wrap.querySelector('svg');
  var rc = sketch.rc(svg);
  sketch.table(svg, rc, {
    x: 12, y: 18, rowH: 38, headerH: 44,
    cols: [
      { title: 'What the caller said', w: 320 },
      { title: 'Tag written to GHL',   w: 268 },
      { title: 'Automation that fires', w: 308 }
    ],
    rows: [
      ['"Send me a quote"',     'quote-requested', 'Quote follow-up sequence'],
      ['"Call me next month"',  'nurture-30d',     '30-day nurture drip'],
      ['"Already covered"',     'not-interested',  'Suppress and remove'],
      ['Voicemail, no answer',  'no-contact',      'Retry cadence'],
      ['"Who is this?"',        'bad-data',        'Flag for a human']
    ]
  });
});
</script>

<h2>Step 5. GHL automations take over</h2>
<p>From here it is all GoHighLevel, doing what it is good at. The new tag drops the contact into the workflow that fits. A quote request starts the quote follow-up. A polite brush-off gets suppressed. A no-answer goes back into the retry cadence. These are the same automations you would build by hand. The difference is what triggers them. Instead of a person deciding, it is what the caller actually said.</p>

<h2>What a day of calls looks like</h2>
<p>Here is the throughput across one representative day. The point is the bottom bar. Every call gets transcribed, tagged, and routed without anyone touching it, and a human only gets pulled in for the handful that are worth a live follow-up.</p>

<div class="sketch" data-viewbox="0 0 920 280" id="dg-voice-funnel">
  <svg></svg>
  <div class="sketch-caption">~ a full day of calls, and you only touch the hot 48 ~</div>
</div>
<script>
document.addEventListener('sketch:ready', function() {
  var wrap = document.getElementById('dg-voice-funnel');
  if (!wrap || wrap.dataset.drawn) return;
  wrap.dataset.drawn = '1';
  var svg = wrap.querySelector('svg');
  var rc = sketch.rc(svg);
  sketch.bars(svg, rc, {
    x: 16, y: 40, w: 880, barH: 42, gap: 26, labelW: 270, max: 480,
    items: [
      { label: 'Calls recorded',          value: 400, note: '400 in a day' },
      { label: 'Transcribed by Whisper',  value: 392, note: '392 usable' },
      { label: 'Tagged and routed',       value: 392, note: '392 auto-handled' },
      { label: 'Flagged hot for a human', value: 48,  note: '48 need you' }
    ]
  });
});
</script>

<h2>Why Whisper runs locally</h2>
<p>The whole design leans on one decision. Keep the transcription on a machine I control instead of renting it. That choice pays off on both cost and on where the recordings live.</p>

<div class="sketch" data-viewbox="0 0 920 300" id="dg-voice-compare">
  <svg></svg>
  <div class="sketch-caption">~ why the transcription runs at home ~</div>
</div>
<script>
document.addEventListener('sketch:ready', function() {
  var wrap = document.getElementById('dg-voice-compare');
  if (!wrap || wrap.dataset.drawn) return;
  wrap.dataset.drawn = '1';
  var svg = wrap.querySelector('svg');
  var rc = sketch.rc(svg);
  sketch.compare(svg, rc, {
    x: 24, y: 30, w: 872, h: 240,
    left: {
      title: 'Cloud transcription API',
      items: [
        'A per-minute charge on every call',
        'Audio leaves your environment',
        'The bill scales with call volume',
        'Whatever model they hand you',
        'One more vendor to depend on'
      ]
    },
    right: {
      title: 'Whisper on your own box',
      items: [
        'Free to run after setup',
        'Recordings never leave',
        'Fixed cost at any volume',
        'Swap the model when you want',
        'No outside dependency'
      ]
    }
  });
});
</script>

<p>None of this is exotic. A webhook, a transcription model, a qualifying prompt, and an API write. The reason it works is that it does not try to be clever. It takes the one slow human step, listening to a call and deciding what it was, and moves it onto a machine, then hands the result back to the CRM you already trust.</p>

<div class="callout insight"><strong>Honest notes.</strong> The numbers above are from a representative day, not a client testimonial, and this is a pattern I build, not a product I sell off a shelf. Whisper is good but not perfect on bad audio, so the worst recordings still get flagged for a human rather than guessed at. Qualification is a filter, not a verdict. And you keep handling call-recording consent exactly the way you do today. This only reads the recordings your dialer already makes.</div>

<div class="contact-card">
  <h3>Have a pile of calls nobody listens to?</h3>
  <p>If your dialer is filling up with recordings and the follow-up keeps slipping, this is the loop I build. Tell me what your dialer and CRM are, and I will tell you honestly whether this fits.</p>
  <a href="../contact.html" class="btn btn-primary">Tell me about your call flow</a>
</div>

<h2>Related reading</h2>
<div class="cards">
  <a href="free-lead-engine.html" class="card">
    <h3>The free lead engine</h3>
    <p>The companion case study. Scrape, verify, qualify, and send, end to end.</p>
  </a>
  <a href="../framework/autonomous/scheduling.html" class="card">
    <h3>Scheduling autonomous agents</h3>
    <p>How a worker ends up running on a trigger instead of a person.</p>
  </a>
  <a href="../framework/claude/tool-use.html" class="card">
    <h3>Tool use</h3>
    <p>How a model reaches out and writes a result back into a real system.</p>
  </a>
  <a href="../ai-consulting.html" class="card">
    <h3>Work with me</h3>
    <p>Advisory and build engagements on systems like this one.</p>
  </a>
</div>
'''

voice_study = head(
    "Calls that file themselves | Samuel Ochoa",
    "A GHL to Whisper to GHL loop. Dialer call recordings get transcribed locally with Whisper, qualified from the transcript, and written back into GoHighLevel so the right automation fires.",
    "https://samuelochoa.com/case-studies/voice-intake.html",
    ld=VOICE_LD,
) + nav + VOICE_BODY + FOOT + navscript + "</body></html>"
(ROOT / "case-studies" / "voice-intake.html").write_text(voice_study)

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
    <p>LeadScrape to Reoon to Claude to Instantly. An outbound pipeline that scrapes leads for nothing, qualifies them with AI, and then runs itself through a second bot. Five diagrams of how it fits together.</p>
  </a>
  <a href="voice-intake.html" class="card">
    <h3>Calls that file themselves</h3>
    <p>GHL to Whisper to GHL. Dialer call recordings get transcribed locally, qualified from the transcript, and written back into the CRM so the right automation fires. Nobody has to listen to the calls.</p>
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
