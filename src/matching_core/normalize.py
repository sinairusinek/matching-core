"""Script-agnostic string normalization.

Canonical source for normalization shared across all matching services
(Places/Kimatch, People/Shidduch, Orgs/Dybbuk). Domain-specific normalization
(title stripping, abbreviation expansion, org-token removal) does NOT belong
here — services compose those on top of `normalize_name`.

Seeded from Kimatch/kimatch/core/normalizers.py (the reference shape).
"""
import re
import unicodedata

# Hebrew geresh ׳ (U+05F3), gershayim ״ (U+05F4), ASCII apostrophe,
# and right single quotation mark ’ (U+2019) — punctuation that does not carry
# matching-relevant meaning.
_PUNCT_TO_STRIP = ("'", "׳", "״", "’")


def normalize_name(name: str) -> str:
    """Lowercase, NFD-strip diacritics, drop geresh/gershayim/apostrophe,
    collapse whitespace. The shared baseline every service starts from.

    Note: NFD + removal of combining marks (category Mn) folds Hebrew nikud,
    Arabic harakat, and Latin diacritics. It deliberately does NOT do NFKD
    compatibility folding (ligatures, presentation forms) — that is a
    service-level choice, not a shared default.
    """
    if not name:
        return ""
    nfd = unicodedata.normalize("NFD", name)
    stripped = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
    for p in _PUNCT_TO_STRIP:
        stripped = stripped.replace(p, "")
    return re.sub(r"\s+", " ", stripped).strip().lower()


def is_hebrew(text: str) -> bool:
    """True if the string contains any Hebrew-block character."""
    return any("֐" <= c <= "׿" for c in text)


# Unicode ranges per script, checked in order. Latin is the implicit default.
_SCRIPT_RANGES = [
    ("hebrew", [("֐", "׿"), ("יִ", "ﭏ")]),
    ("arabic", [("؀", "ۿ"), ("ݐ", "ݿ"), ("ﭐ", "﷿"),
                ("ﹰ", "﻿")]),
    ("cyrillic", [("Ѐ", "ӿ"), ("Ԁ", "ԯ")]),
    ("greek", [("Ͱ", "Ͽ"), ("ἀ", "῿")]),
    ("latin", [("A", "Z"), ("a", "z"), ("À", "ɏ")]),
]


def detect_script(text: str) -> str:
    """Return the dominant script: hebrew | arabic | cyrillic | greek | latin |
    unknown. Picks the script with the most letters (ties broken by the order
    above), ignoring digits/punctuation/whitespace."""
    if not text:
        return "unknown"
    counts: dict[str, int] = {}
    for ch in text:
        if not ch.isalpha():
            continue
        for name, ranges in _SCRIPT_RANGES:
            if any(lo <= ch <= hi for lo, hi in ranges):
                counts[name] = counts.get(name, 0) + 1
                break
    if not counts:
        return "unknown"
    order = [name for name, _ in _SCRIPT_RANGES]
    return max(counts, key=lambda k: (counts[k], -order.index(k)))
