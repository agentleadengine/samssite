#!/usr/bin/env python3
"""Apply the mechanical design-v2 cleanup to legacy HTML pages.

Idempotent. Protected page trees and the home page are never changed.
Run both cleanups with ``python3 _cleanup_v2.py`` or one phase with
``python3 _cleanup_v2.py --only labels`` / ``--only arrows``.
"""

import argparse
import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SKIP_DIRS = {"demos", "framework", "learn"}

TAG_RE = re.compile(r"<[^>]+>", re.S)
LABEL_RE = re.compile(
    r"(?P<label><(?P<tag>[A-Za-z][\w:-]*)\b"
    r"(?P<attrs>[^>]*\bclass\s*=\s*['\"][^'\"]*\b(?:eyebrow|kicker|badge)\b[^'\"]*['\"][^>]*)>"
    r"(?P<body>.*?)</(?P=tag)>)(?P<gap>\s*)"
    r"(?P<head><h[12]\b[^>]*>(?P<head_body>.*?)</h[12]>)",
    re.I | re.S,
)
ANCHOR_RE = re.compile(r"<a\b(?P<attrs>[^>]*)>(?P<body>.*?)</a>", re.I | re.S)
CLASS_RE = re.compile(r"\bclass\s*=\s*(['\"])(?P<classes>.*?)\1", re.I | re.S)
WORD_RE = re.compile(r"[A-Za-z][A-Za-z'’-]*")
RETAINED_LEAD_RE = re.compile(
    r"(?P<head><h[12]\b[^>]*>.*?</h[12]>)(?P<gap>\s*)"
    r"(?P<lead><p\b(?P<attrs>[^>]*\bclass\s*=\s*['\"][^'\"]*\blead\b[^'\"]*['\"][^>]*)>"
    r"(?P<body>.*?)</p>)",
    re.I | re.S,
)
HUB_ARROW_RE = re.compile(
    r"<[^>]+\bclass\s*=\s*['\"][^'\"]*\bhub-arrow\b[^'\"]*['\"][^>]*>",
    re.I,
)

# Title-cased proper names cannot be distinguished from ordinary words without
# a dictionary. Keep the names and products used by this site's labels while
# acronym and mixed-case preservation remains automatic.
PROPER_WORDS = {
    "Amazon", "Apple", "Claude", "Facebook", "Gemini", "GitHub", "Google",
    "Instagram", "JavaScript", "LinkedIn", "Meta", "Microsoft", "Ochoa",
    "OpenAI", "Sam", "Samuel", "Shopify", "TikTok", "WordPress", "YouTube",
}


def pages():
    for path in sorted(ROOT.rglob("*.html")):
        relative = path.relative_to(ROOT)
        if path == ROOT / "index.html" or relative.parts[0] in SKIP_DIRS:
            continue
        if any(part.startswith("_") for part in relative.parts):
            continue
        yield path


def plain_text(markup: str) -> str:
    return " ".join(html.unescape(TAG_RE.sub("", markup)).split())


def comparable(value: str) -> str:
    return re.sub(r"[^\w]+", " ", value.casefold()).strip()


def sentence_case_markup(markup: str) -> str:
    """Sentence-case visible label text without changing its HTML markup."""
    at_start = True

    def clean_text(value: str) -> str:
        nonlocal at_start

        def clean_word(match: re.Match[str]) -> str:
            nonlocal at_start
            word = match.group(0)
            letters = "".join(character for character in word if character.isalpha())
            initialism_part = (
                len(letters) == 1
                and letters.isupper()
                and (
                    (match.start() >= 2 and value[match.start() - 1] == "&" and value[match.start() - 2].isupper())
                    or (match.end() + 1 < len(value) and value[match.end()] == "&" and value[match.end() + 1].isupper())
                )
            )
            preserve = (
                at_start
                or word in PROPER_WORDS
                or (len(letters) > 1 and letters.isupper())
                or initialism_part
                or (not word.istitle() and any(character.isupper() for character in word[1:]))
            )
            at_start = False
            return word if preserve else word.lower()

        cleaned = WORD_RE.sub(clean_word, value)
        if re.search(r"(?:^|\s)[/|•]\s*$", html.unescape(value)):
            at_start = True
        return cleaned

    pieces = re.split(r"(<[^>]+>)", markup)
    return "".join(piece if piece.startswith("<") else clean_text(piece) for piece in pieces)


def clean_labels(text: str, counts: dict[str, int]) -> str:
    def replace(match: re.Match[str]) -> str:
        label_text = plain_text(match.group("body"))
        heading_text = plain_text(match.group("head_body"))
        counts["labels_found"] += 1
        if not label_text or comparable(label_text) == comparable(heading_text):
            counts["labels_removed"] += 1
            return match.group("head")

        counts["labels_to_lead"] += 1
        return (
            match.group("head")
            + match.group("gap")
            + f'<p class="lead" data-cleanup-v2-label>{sentence_case_markup(match.group("body"))}</p>'
        )

    text = LABEL_RE.sub(replace, text)

    def normalize_retained(match: re.Match[str]) -> str:
        attrs = match.group("attrs")
        body = match.group("body")
        generated = "data-cleanup-v2-label" in attrs
        breadcrumb = "<a" in body.lower() and bool(re.search(r"\s/\s", plain_text(body)))
        if not generated and not breadcrumb:
            return match.group(0)
        normalized = sentence_case_markup(body)
        if normalized != body:
            counts["labels_sentence_cased"] += 1
        return (
            match.group("head") + match.group("gap")
            + f'<p{attrs}>{normalized}</p>'
        )

    return RETAINED_LEAD_RE.sub(normalize_retained, text)


def visible_character_positions(markup: str) -> list[int]:
    positions = []
    in_tag = False
    for index, character in enumerate(markup):
        if character == "<":
            in_tag = True
        elif character == ">" and in_tag:
            in_tag = False
        elif not in_tag and not character.isspace():
            positions.append(index)
    return positions


def remove_arrow(markup: str, index: int, *, back: bool) -> str:
    start = end = index
    if back:
        while end + 1 < len(markup) and markup[end + 1] in " \t":
            end += 1
    else:
        while start > 0 and markup[start - 1] in " \t":
            start -= 1
    return markup[:start] + markup[end + 1 :]


def add_classes(attrs: str, additions: list[str]) -> str:
    match = CLASS_RE.search(attrs)
    if match:
        classes = match.group("classes").split()
        classes.extend(item for item in additions if item not in classes)
        replacement = f'class={match.group(1)}{" ".join(classes)}{match.group(1)}'
        return attrs[: match.start()] + replacement + attrs[match.end() :]
    return attrs.rstrip() + f' class="{" ".join(additions)}"' + attrs[len(attrs.rstrip()) :]


def remove_classes(attrs: str, removals: set[str]) -> str:
    match = CLASS_RE.search(attrs)
    if not match:
        return attrs
    classes = [item for item in match.group("classes").split() if item not in removals]
    if classes:
        replacement = f'class={match.group(1)}{" ".join(classes)}{match.group(1)}'
        return attrs[: match.start()] + replacement + attrs[match.end() :]
    return attrs[: match.start()] + attrs[match.end() :]


def clean_arrows(text: str, counts: dict[str, int]) -> str:
    def replace(match: re.Match[str]) -> str:
        attrs = match.group("attrs")
        body = match.group("body")
        has_hub_arrow = bool(HUB_ARROW_RE.search(body))
        class_match = CLASS_RE.search(attrs)
        classes = class_match.group("classes").split() if class_match else []
        if has_hub_arrow and "arrow-link" in classes:
            attrs = remove_classes(attrs, {"arrow-link", "is-back"})
            counts["arrows_deduplicated"] += 1

        positions = visible_character_positions(body)
        if not positions:
            return f"<a{attrs}>{body}</a>"

        back = body[positions[0]] == "←"
        forward = body[positions[-1]] == "→"
        if not back and not forward:
            return f"<a{attrs}>{body}</a>"

        if forward:
            body = remove_arrow(body, positions[-1], back=False)
            counts["arrows_forward"] += 1
        if back:
            positions = visible_character_positions(body)
            body = remove_arrow(body, positions[0], back=True)
            counts["arrows_back"] += 1

        if not has_hub_arrow:
            additions = ["arrow-link"]
            if back:
                additions.append("is-back")
            attrs = add_classes(attrs, additions)
        return f"<a{attrs}>{body}</a>"

    return ANCHOR_RE.sub(replace, text)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", choices=("labels", "arrows"))
    args = parser.parse_args()
    counts = {
        "files_scanned": 0,
        "files_changed": 0,
        "labels_found": 0,
        "labels_removed": 0,
        "labels_to_lead": 0,
        "labels_sentence_cased": 0,
        "arrows_forward": 0,
        "arrows_back": 0,
        "arrows_deduplicated": 0,
    }

    for path in pages():
        counts["files_scanned"] += 1
        original = path.read_text(encoding="utf-8")
        updated = original
        if args.only in (None, "labels"):
            updated = clean_labels(updated, counts)
        if args.only in (None, "arrows"):
            updated = clean_arrows(updated, counts)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            counts["files_changed"] += 1

    print(" ".join(f"{key}={value}" for key, value in counts.items()))


if __name__ == "__main__":
    main()
