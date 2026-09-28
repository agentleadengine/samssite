---
name: Samuel Ochoa · The Record
description: A free library for learning AI at work, kept as a dated provenance record on archival paper with one red silk custody line.
colors:
  ribbon: "#a1171c"
  ribbon-deep: "#7b0f14"
  ruby-faint: "#f0d6cd"
  ruby-wash: "#f6e4dc"
  stamp: "#4d5a66"
  gap: "#8f8a80"
  ok: "#3f6b3a"
  paper: "#f3ecdd"
  paper-deep: "#e9dfca"
  paper-hi: "#faf6ec"
  paper-edge: "#d9ccb1"
  ink: "#2a1f1a"
  ink-2: "#544639"
  ink-3: "#6e604f"
  rule: "#cdbfa5"
  rule-strong: "#a8977b"
  code-ground: "#2a211c"
  code-text: "#efe6d6"
typography:
  display:
    fontFamily: "Gloock, Georgia, serif"
    fontSize: "clamp(50px, 7.4vw, 108px)"
    fontWeight: 400
    lineHeight: 0.98
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "Gloock, Georgia, serif"
    fontSize: "clamp(38px, 5.6vw, 72px)"
    fontWeight: 400
    lineHeight: 1.06
    letterSpacing: "-0.01em"
  section:
    fontFamily: "Gloock, Georgia, serif"
    fontSize: "clamp(28px, 3.4vw, 40px)"
    fontWeight: 400
    lineHeight: 1.06
    letterSpacing: "-0.01em"
  title:
    fontFamily: "Source Serif 4, Source Serif Pro, Georgia, serif"
    fontSize: "21px"
    fontWeight: 650
    lineHeight: 1.3
  lede:
    fontFamily: "Source Serif 4, Source Serif Pro, Georgia, serif"
    fontSize: "21px"
    fontWeight: 400
    lineHeight: 1.55
  body:
    fontFamily: "Source Serif 4, Source Serif Pro, Georgia, serif"
    fontSize: "18.5px"
    fontWeight: 400
    lineHeight: 1.68
    fontFeature: "\"kern\", \"liga\", \"onum\""
  label:
    fontFamily: "Source Serif 4, Source Serif Pro, Georgia, serif"
    fontSize: "14px"
    fontWeight: 600
    letterSpacing: "0.13em"
    fontFeature: "\"smcp\", \"c2sc\", \"lnum\", \"tnum\""
  mono:
    fontFamily: "JetBrains Mono, ui-monospace, SFMono-Regular, Menlo, monospace"
    fontSize: "0.84em"
    fontWeight: 400
rounded:
  none: "0px"
  code: "2px"
  slip: "3px"
  round: "50%"
spacing:
  gutter: "28px"
  gutter-phone: "16px"
  inline: "14px"
  card-gap: "22px"
  chapter: "56px"
  section: "80px"
  section-phone: "56px"
  wrap: "1240px"
  reading: "780px"
components:
  button-primary:
    backgroundColor: "{colors.ribbon}"
    textColor: "{colors.paper-hi}"
    rounded: "{rounded.none}"
    padding: "0 34px 0 22px"
    height: "50px"
  button-primary-hover:
    backgroundColor: "{colors.ribbon-deep}"
    textColor: "{colors.paper-hi}"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "0 30px 0 22px"
    height: "50px"
  button-ghost-hover:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper-hi}"
  nav-cta:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.slip}"
    padding: "0 16px 0 14px"
    height: "40px"
  nav-cta-hover:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper-hi}"
  input:
    backgroundColor: "{colors.paper-hi}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "12px 14px"
    height: "50px"
  filter-chip:
    backgroundColor: "{colors.paper-hi}"
    textColor: "{colors.ink-2}"
    rounded: "{rounded.none}"
    padding: "0 14px"
    height: "36px"
  filter-chip-active:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper-hi}"
  card:
    backgroundColor: "{colors.paper-hi}"
    textColor: "{colors.ink}"
    rounded: "{rounded.slip}"
    padding: "30px 26px 26px"
  record-strip:
    backgroundColor: "{colors.paper-hi}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "16px 64px 16px 22px"
  code-block:
    backgroundColor: "{colors.code-ground}"
    textColor: "{colors.code-text}"
    rounded: "{rounded.slip}"
    padding: "20px 22px"
---

# Design System: Samuel Ochoa · The Record

## Overview

**Creative North Star: "The Provenance Record"**

The site is a record, not a course. Every lesson is kept like an archival entry: buff paper with a faint grain, ledger type, a dated stamp, and one red silk ribbon that runs through the whole library as the custody line. The ribbon says who vouches for a fact and how: solid where the claim was checked against a source, dashed where it is Sam's own take from real setups, dotted gray where the fact is still moving. The reader should always know what is true now, when it was checked, and what might change.

Density is a reading density: generous serif body, a 780px reading column, hairline rules and dotted leaders instead of boxes and fills. Ornament is limited to things a real record would carry (a bookmark ribbon, a lozenge rule, an ink stamp, a double rule under a definition). The world rejects the default AI-course page named in the direction contract: gradient hero, feature-icon grid, logo wall. It is light only; the owner dislikes dark mode.

The build landed close to the direction contract. Two divergences, where the build wins: the home journey ribbon splits three ways (owner, builder, still changing), not two; and the stamp moved from CSS rings to a single authored ink asset (`images/stamp.svg`).

**Key Characteristics:**
- Archival buff paper with an SVG grain on `body`; lighter slips (`paper-hi`) for anything that sits on the page.
- One accent: ribbon red, woven with a silk texture wherever it is a surface.
- Three custody marks (solid, dashed, dotted gray) carry meaning everywhere claims appear.
- Gloock display over Source Serif 4 text; labels in true small caps, never uppercase.
- Square ribbon controls with a swallowtail notch; paper slips with a 3px corner.
- Flat by default; soft, warm, long shadows only under objects that lift off the paper.

## Colors

One ribbon red on warm paper, with a faded stamp blue-gray as the only second voice and an unwoven gray reserved for "still changing".

### Primary
- **Ribbon Red** (`ribbon`): the custody line and every call to action. Primary buttons, bookmarks, the claim line, the h2 tick, table header underline, active tab, focus outline, list markers. Wherever it is a band or tab it carries the silk texture (see Named Rules).
- **Oxblood** (`ribbon-deep`): red as text. Page titles (h1 in reading layouts, glossary terms), link color, table header text, primary button hover.
- **Ruby Faint** (`ruby-faint`) and **Ruby Wash** (`ruby-wash`): tints only. Text selection, the halo around the active sidebar node and the "today" journey node, notice banners, submenu hover.

### Secondary
- **Faded Stamp** (`stamp`): the builder track and secondary marks. Builder track band and numerals, builder record ribbon, Spanish-site bookmarks, source-type labels in Sources lists, links inside claim marks.

### Tertiary
- **Unwoven Gray** (`gap`): the "Changing" mark. Dotted claim lines, the dashed idle sidebar line, the dashed "still changing" track border, the dashed journey segment. Lines only: at 2.9:1 on paper it never carries text.
- **Ledger Green** (`ok`): completion only. Checked-off playbook modules, success confirmations.

### Neutral
- **Archival Paper** (`paper`): page ground, always with the grain overlay.
- **Deep Paper** (`paper-deep`): alternate section bands (at 55%), footer, inline code ground, video placeholders.
- **Slip Paper** (`paper-hi`): every object that sits on the page: cards, record strip, record card, form fields, sketches, sidebars on mobile.
- **Paper Edge** (`paper-edge`): the 1px bottom lip under lifted slips (contact card, record card).
- **Ledger Ink** (`ink`), **Ink 2** (`ink-2`), **Ink 3** (`ink-3`): body text, secondary text, and meta text. Ink 3 is the floor for readable text (5.2:1 on paper).
- **Rule** (`rule`) and **Strong Rule** (`rule-strong`): hairlines, dotted leaders, slip borders; strong rule for top rules of lists and tables and for lifted slips.
- **Code Ground** (`code-ground`) and **Code Text** (`code-text`): the one dark surface, code blocks only, with a 3px ribbon inset along the top.

### Named Rules
**The One Ribbon Rule.** Red is the only accent. Stamp blue-gray marks the builder track and secondary metadata; it never competes for a call to action.

**The Woven Silk Rule.** Any ribbon red that reads as a surface (a button, a bookmark tab, a track band, a progress fill, the journey tab and ribbon) carries the silk texture from `images/silk-h.svg` (horizontal runs) or `images/silk-v.svg` (vertical tabs) over a solid `ribbon` background color. Hairline strokes of 3px or less stay flat ribbon. Ribbon red is never a CSS gradient.

**The Unwoven Gray Rule.** Gap gray only draws lines and borders. Text that belongs to a "Changing" item uses Ink 2 or Ink 3.

## Typography

**Display Font:** Gloock (with Georgia, serif)
**Body Font:** Source Serif 4 (with Source Serif Pro, Georgia, serif), variable optical size
**Mono Font:** JetBrains Mono (with ui-monospace, SFMono-Regular, Menlo)

**Character:** A high-contrast ledger display over a sturdy book serif. The pairing reads like a register entry: heavy, dated headings, calm running text, and small-caps labels in the same serif instead of a separate UI sans.

### Hierarchy
- **Display** (Gloock 400, `clamp(50px, 7.4vw, 108px)`, line-height 0.98, -0.02em, Oxblood): the home hero line only.
- **Headline** (Gloock 400, `clamp(38px, 5.6vw, 72px)` default; reading-page titles `clamp(38px, 5vw, 60px)`, line-height 1.05; glossary terms `clamp(44px, 7vw, 84px)`): one h1 per page, in Oxblood on hero and reading layouts.
- **Section** (Gloock 400, `clamp(28px, 3.4vw, 40px)`; inside lessons `clamp(27px, 3vw, 34px)`, line-height 1.12, with a 44 x 2px ribbon tick above and 56px space before).
- **Title** (Source Serif 4 650, 21px, line-height 1.3): h3 in running text. Card and slip titles in Gloock at 25 to 40px are the display face used as object names (track, catalog entry, record card, glossary card).
- **Lede** (Source Serif 4 400, 21px, line-height 1.55, Ink 2): the paragraph under a page title. 18.5px on phones.
- **Body** (Source Serif 4 400, 18px base, 18.5px in reading columns, line-height 1.62 to 1.68; 17 to 17.5px on phones): old-style figures by default (`onum`). Reading columns cap at 780px (about 70ch); essays at 740px.
- **Label** (Source Serif 4 600, 13 to 15px, `font-variant-caps: all-small-caps`, 0.12 to 0.16em tracking, lining tabular figures): record strip terms, statuses, nav links, buttons, table heads, chips, meta lines.
- **Mono** (JetBrains Mono, 0.84em): inline code (Oxblood on Deep Paper) and code blocks.

### Named Rules
**The Small Caps Rule.** Labels are true small caps of the text face (`all-small-caps` plus `smcp`/`c2sc`), never `text-transform: uppercase` and never a separate sans.

**The Heading First Rule.** Nothing sits above a heading. Metadata, audience tags, and topic labels follow the heading (the track "For owners" line sits under its h3; the glossary topic sits beside the term, not over it).

**The One Red Tail Rule.** The red italic tail (an `<em>` inside the h1, set in Source Serif 4 italic 500, Ribbon Red) appears on the home hero only: "Every AI claim needs a *date.*" Everywhere else h1 is plain Gloock.

**The Figures Rule.** Running text uses old-style figures; anything tabulated or dated (record strips, tables, counts, dates, footer colophon) switches to lining tabular figures.

## Layout

A single 1240px wrap with 28px gutters (16px on phones). Home and hub pages stack full-width chapters (`section.block`, 80px vertical padding, 56px on phones) separated by 1px rules, with every even chapter washed in Deep Paper at 55%. Reading pages use a two-column grid: a 270px sticky sidebar and a content column capped at 780px, 64px apart; glossary and comparison plates are a single 820px column; essays 740px.

Spacing is an observed rhythm rather than a numeric scale: 14px between inline actions, 22px between cards, 26 to 34px around slips inside the reading column, 56px before a section heading and before the prev/next pair, 80px between chapters. Lists and indexes use rows with top and bottom hairlines and dotted leaders, not cards, whenever the content is a list (hub list, catalog, Sources, sidebar, record card rows).

Breakpoints: at 1000px the nav collapses to a hamburger drawer, the sidebar becomes a collapsible "In this section" panel above the content, and the home hero goes single column. At 860px the journey ribbon turns vertical and the catalog tightens. At 640px gutters drop to 16px, type steps down, CTA rows stack full width, and the record strip goes to two columns and drops its stamp. No horizontal page scroll; wide tables scroll inside `.table-wrap`.

**The List Is A Ledger Rule.** When content is a sequence of entries, it is ruled rows with numerals or counts in the left column, not a grid of boxes.

## Elevation & Depth

Flat by default. Depth comes from paper tone (Slip Paper on Archival Paper) and hairline borders. Shadows are warm (brown-black at 35 to 60%), long, and pulled in with a large negative spread, so an object looks like a sheet resting on paper, never a floating UI card. They appear only on objects that physically lift: the record card, the contact slip, the keeper photo, the nav submenu, and a card on hover.

### Shadow Vocabulary
- **Resting slip** (`box-shadow: 0 1px 0 var(--paper-edge), 0 24px 40px -30px rgba(60,35,20,.4)`): contact card; the record card uses `0 30px 50px -36px rgba(60,35,20,.55)` with the same paper-edge lip.
- **Lift on hover** (`box-shadow: 0 14px 28px -20px rgba(60,35,20,.45)` with `translateY(-2px)`): linked cards.
- **Dropdown** (`box-shadow: 0 18px 40px -18px rgba(60,35,20,.35)`): nav submenu; the mobile drawer uses `0 20px 30px -20px rgba(60,35,20,.4)`.
- **Pinned photo** (`box-shadow: 0 24px 40px -30px rgba(60,35,20,.6)` with a -1.2deg tilt): the keeper portrait.
- **Double rule** (`box-shadow: 0 3px 0 -2px var(--paper), 0 4px 0 -2px var(--rule)`): the sticky top bar's second hairline; the footer mirrors it as an inset.

**The Resting Sheet Rule.** A shadow always has a negative spread at least half its blur. If it reads as a glow or a hard offset, it is wrong.

## Shapes

Two corner families. Anything that is ribbon (buttons, chips, inputs, callouts, the record strip, the brief form row) is square, 0 radius. Anything that is a paper slip (cards, the contact slip, the nav submenu, code blocks, the hamburger) gets a barely-there 3px corner. Circles are reserved for the stamp, avatars, and journey and sidebar nodes.

The signature silhouette is the swallowtail: ribbon ends are cut with a V notch (`clip-path: polygon(0 0,100% 0,100% 100%,50% 74%,0 100%)` for hanging bookmarks; a 12px notch on the right end of primary buttons; an outlined 14px swallowtail SVG on ghost buttons). Bookmarks hang from the top edge of slips (record card, contact slip, cards, lesson task, glossary example, sign-up slip, demo specimens), usually near the right. Ornaments are lozenges: a 45deg square on the ornamental rule, between meta items, and as the list marker.

## Components

### Buttons
Ribbon tabs: square, small-caps, cut with a swallowtail.
- **Shape:** square (0), 50px min height (56px large), swallowtail notch on the trailing end.
- **Primary:** Ribbon Red woven with `silk-h` at 150 x 38px, Slip Paper text, 17px small caps at 0.14em, padding 0 34px 0 22px.
- **Hover / Focus:** background deepens to Oxblood over 0.2s; focus is a 2px Ribbon outline at 3px offset (site-wide).
- **Ghost:** transparent with a 1px Ink border and an outlined swallowtail end drawn by an inline SVG; hover fills Ink with Slip Paper text and the tail fills solid. On the builder track the ghost button takes Stamp instead of Ink.
- **Nav CTA:** the one boxed item in the top bar ("Daily brief"): 1px Ink border, 3px corner, 40px tall, fills Ink on hover.

### Chips
- **Style:** 36px square chips, 1px Strong Rule border, Slip Paper ground, Ink 2 small caps.
- **State:** hover turns border Ribbon and text Oxblood; active fills Ink with Slip Paper text. Pills (32px) and glossary related links (34px) follow the same pattern.

### Cards / Containers
- **Corner Style:** 3px.
- **Background:** Slip Paper on Archival Paper.
- **Shadow Strategy:** none at rest; lift on hover for linked cards (see Elevation).
- **Border:** 1px Rule; Strong Rule for slips that must stand out (record card, tracks, sign-up slip).
- **Internal Padding:** 30px 26px 26px for cards; 26 to 40px for larger slips.
- **Bookmark:** every card carries a small silk bookmark (11 x 20px) hanging from its top edge.

### Inputs / Fields
- **Style:** square, 50px min height, 1px Strong Rule border, Slip Paper ground, 17px text; placeholders italic Ink 3.
- **Focus:** 2px Ribbon outline at 3px offset.
- **Form rows:** on the home sign-up slip the input and primary button join into one bar (the input drops its right border); they stack on phones.

### Navigation
- **Top bar:** sticky, 68px (62px under 1000px), 94% paper with a 6px backdrop blur and a double hairline beneath. Logo is the stacked SO mark (`images/so-mark.png`) plus the wordmark in Gloock with a small-caps subtitle.
- **Links:** 15px small caps at 0.12em, 44px targets; a 2px Ribbon underline grows from the left on hover and marks `aria-current`. "Get help" is a quiet italic Ink 3 text link with no underline animation; "Daily brief" is the only boxed action.
- **Submenu:** a Slip Paper sheet with a silk bookmark at its top-left, dotted leaders between items, counts in lining figures on the right.
- **Mobile:** hamburger (44px) opens a full-width drawer; groups expand inline with dotted separators.
- **Shell source:** the nav, footer, fonts, and stylesheet version are stamped onto every page by `_rebuild_nav.py`; generators still emit the old shell.

### Claim (signature)
The custody line in running text. A claim is a paragraph with a 3px Ribbon line on its left (dashed 2.5px Ribbon for My take, dotted 2.5px Gap for Changing), followed by a small-caps claim mark: the status, the date checked, and source links in Stamp. This is the only left rule on the site.

### Status marks (signature)
Inline small-caps labels preceded by a 26px rule sample: solid 2.5px Ribbon ("Checked"), dashed Ribbon ("My take"), dotted Gap ("Changing"). The same three samples appear in the record card legend, the journey key, the ledger table, and the footer colophon.

### Record strip (signature)
The dated header under every lesson title: a Slip Paper band of term/value pairs (Track, Reading time, Last checked, Marks) in an auto-fit grid, with the ink stamp overlapping its right edge at -11deg with multiply blending. Without a stamp it shows a hanging silk bookmark instead (Stamp colored on builder lessons). The stamp hides on phones.

### Stamp (signature)
A circular ink mark drawn by `images/stamp.svg` ("CHECKED / 2026 / 28 SEP / SAMUEL OCHOA · RECORD", in stamp ink with a roughened, faded filter). The date is baked into the SVG; the element's own text is hidden and kept only as a fallback. Used on the home record card (112px, overlapping the corner) and the lesson record strip (100px).

### Journey ribbon (signature, home only)
A silk ribbon drawn in SVG through dated nodes from Nov 2022 to Today, solid through checked history, dashed gray through "My take", then forking into the owner (red), builder (stamp), and changing (dashed gray) strands. It draws itself over 2.2s on reveal and turns into a vertical rail under 860px.

### Sidebar custody line
Reading-layout sidebars draw each section as a dashed gray line with hollow nodes per entry; the section containing the current page turns into a solid 2.5px Ribbon line and the current node fills Ribbon with a Ruby Faint halo. Long sidebars fade out at the bottom to signal scroll.

### Lesson task
The "Do this today" slip that ends a lesson: Slip Paper, Strong Rule border, a silk bookmark top-right, a small-caps Oxblood heading, and a numbered list with Ribbon numerals.

### Sources list
Under a 3px double rule in Strong Rule: a small-caps heading with a bookmark, then numbered rows (01, 02) with a Stamp-colored source type and the link, separated by dotted leaders.

### Diagrams
`js/sketch.js` draws every diagram with rough.js in the same grammar: Ledger Ink strokes, Ribbon for emphasis, Slip Paper fills, Source Serif labels, inside a square Slip Paper frame with an italic caption over a dotted rule. It remaps any legacy purple, blue, green, or amber passed in by old pages to the record palette.

### Motion
One easing, `cubic-bezier(.2,.7,.2,1)`. Chapters fade up 14px over 0.7s on reveal; nav underlines grow over 0.25s; card lift 0.25s; color changes 0.15 to 0.2s. All reveal and draw motion sits behind `prefers-reduced-motion: no-preference`, and content is visible without JavaScript.

## Do's and Don'ts

### Do:
- **Do** mark every factual claim with its custody line and status: solid Ribbon for Checked, dashed Ribbon for My take, dotted Gap gray for Changing, plus the date and a source link.
- **Do** texture every ribbon-red surface with `images/silk-h.svg` or `images/silk-v.svg` over a solid `ribbon` background color.
- **Do** draw arrows with `images/arrow.svg` as a CSS mask on `currentColor` (26 x 10px; mirrored with `scaleX(-1)` for back and previous).
- **Do** use `images/stamp.svg` for every stamp, and update the date inside the SVG whenever the site-wide check date changes (`SITE_CHECKED` in `_rebuild_nav.py`).
- **Do** set labels in small caps of Source Serif 4 with lining tabular figures for dates and counts.
- **Do** put metadata after the heading it describes.
- **Do** hang bookmarks from the top edge of slips and cut ribbon ends with the swallowtail.
- **Do** run `python3 _rebuild_nav.py` after any `_build_*.py` generator run, so the page gets the current nav, footer, fonts, and stylesheet version.
- **Do** keep the page light: `color-scheme: light`, Archival Paper with grain, no dark theme.

### Don't:
- **Don't** add a left rule to anything other than a claim. The claim line is the only left rule on the site.
- **Don't** put a label, kicker, or eyebrow above a heading.
- **Don't** use the red italic tail outside the home hero.
- **Don't** paint ribbon red with a gradient, and don't use flat red for a button or tab that should be woven.
- **Don't** use text glyphs for arrows or chevrons.
- **Don't** hand-build a stamp from CSS rings or text; the asset is the stamp.
- **Don't** use em dashes in copy.
- **Don't** set text in Gap gray; it fails contrast and it is a line color.
- **Don't** round buttons, chips, or inputs; only paper slips get the 3px corner.
- **Don't** use a gradient hero, an icon feature grid, or a logo wall.
- **Don't** ship a dark mode.
