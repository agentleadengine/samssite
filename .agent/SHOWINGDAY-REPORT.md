# Showingday handoff

Implemented on `showingday-demos-2026-10-12`, based on `9d739afb`. Ready for coordinator browser review. No push, deployment, Netlify change, external message, or client/harness change.

## Changes

Changed: `index.html`, `ai-consulting.html`, `contact.html`, `about.html`, `links.html`, `es/index.html`, `offer-contract.json`, `assets/showingday-demo.{js,css}`, `tests/test_offer.py`, `tests/test_funnels.py`, `tests/showingday.test.mjs`, and this report.

Showingday is named across the current offer and metadata. Agent Lead Engine creates QUEVA OS; QUEVA OS powers Showingday; Sam sets up and runs it. The existing purple/Inter style remains, including homepage-only purple overrides for the portable demo components.

Three shared interactive samples appear before homepage testimonials. Direct share target: `/#demo-examples`; service, contact, about, links and Spanish home link there. A separate product page was unnecessary. Request-a-demo CTAs remain `/contact`; phone, email and LinkedIn remain intact.

The entire homepage testimonial section is byte-identical to the base. Existing testimonial/video checks pass. Commercial contract sections are unchanged and checked against the base. Capture forms, historical educational pages, existing scripts, service terms and native Netlify password configuration were not changed.

## Shared source

Copied after `/Users/ale/ale-wt-showingday/.agent/SHOWINGDAY-REPORT.md` existed, from task `20261012-172216-97c3c9`. Both assets and all three complete `article.sd-demo` blocks match the source byte for byte. Shared test copied with only its page list narrowed to Sam's homepage.

SHA-256:

- `assets/showingday-demo.js`: `78e2e99184d778993d6d7ac27680ff2baae8f4031953eff9e4b2ac1f06a3f500`
- `assets/showingday-demo.css`: `2c07262af3934a1a2c05a6606c34deff7c4a437b705cdf868ec3ecd22e49bda9`

## Exact checks

Python below is `/Library/Frameworks/Python.framework/Versions/3.13/bin/python3`.

```sh
python3 tests/test_offer.py
node --test tests/showingday.test.mjs
python3 -m unittest \
  tests.test_funnels.FunnelTests.test_capture_contract \
  tests.test_funnels.FunnelTests.test_links_hub_has_no_form_or_nav \
  tests.test_funnels.FunnelTests.test_copy_and_metadata \
  tests.test_funnels.FunnelTests.test_sample_is_fictional_and_in_word_budget \
  tests.test_funnels.FunnelTests.test_thank_you_and_sitemap \
  tests.test_funnels.FunnelTests.test_booking_single_target \
  tests.test_funnels.FunnelTests.test_internal_links_and_assets_resolve
python3 .agent/check-showingday-static.py
git diff --check
```

All pass: offer, one shared behavior check, seven funnel checks, local links/fragments/assets, static HTML/JSON, ten inline scripts plus module syntax, eight local HTTP responses/MIME types, shared-copy equality and full testimonial-section equality. Static files are served directly; no aggregate build or browser suite ran. Node reports a harmless module-type detection warning; no package/dependency changes were made. Logs and the one-off static verification script remain local under `.agent/`.

Known baseline reproduced unchanged: `python3 -m unittest tests.test_funnels.FunnelTests.test_resource_strips` fails because the homepage has zero strips; the current test expects one. No unrelated baseline was loosened.

## Limits

Supplied `CONTEXT.md` was absent. Coordinator owns browser acceptance and any frozen release/publication. Samples use fictional data with simulated approval, no collection/uploads/API calls or connected CRM operations. Lease preview does not sign or deliver. Weekly money is a beta preview under final validation. Full client deployment is not verified. Root must propagate any later shared-asset review changes before release.
