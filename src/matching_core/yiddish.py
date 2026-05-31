"""Optional Yiddish-morphology helpers.

NOT used by the default cascade and NOT auto-imported by `matching_core`.
Services opt in by importing explicitly:

    from matching_core.yiddish import strip_yiddish_inflections

Disposition (LEDGER row 19, 2026-05-27):
    - Places: not applicable (Hebrew/Latin gazetteer scripts, no Yiddish morphology)
    - Orgs:   primary user — origin of this code (Dybbuk org_normalize.token_key_set)
    - People: OPT-IN — Shidduch may use selectively; do NOT apply unconditionally,
              because person surnames can legitimately end in ס or ער (those are
              not always inflectional)

Covers possessive/plural ``ס`` (and ``׳ס``) and an unmapped adjectival ``ער``
suffix. Service-specific data (org head-nouns, city-adjective maps) stays in
the services that need it.
"""
from __future__ import annotations

import re

# Leading articles, Yiddish + common Latin transliterations.
YIDDISH_ARTICLES: frozenset[str] = frozenset({
    "דער", "די", "דאָס", "דאס", "דעמ",
    "der", "di", "dos",
})

# Prepositions introducing a possessor / origin ("of / from / von").
YIDDISH_OF_TOKENS: frozenset[str] = frozenset({
    "פון", "פֿון",
    "fun", "fon", "von", "of", "from",
})

_POSSESSIVE_S = re.compile(r"[׳']?ס$")


def is_article(token: str) -> bool:
    """True if the token is a Yiddish or transliterated article (דער/די/…)."""
    return token in YIDDISH_ARTICLES


def is_of_token(token: str) -> bool:
    """True if the token is a Yiddish/Latin 'of/from' preposition."""
    return token in YIDDISH_OF_TOKENS


def strip_possessive_s(token: str) -> str:
    """Strip trailing possessive/plural ``ס`` (and an optional preceding
    geresh/apostrophe): ``גאָלדפאדעןס`` → ``גאָלדפאדען``.

    No-op on tokens shorter than 4 chars (avoids mangling short surnames)."""
    if len(token) > 3 and token.endswith("ס"):
        return _POSSESSIVE_S.sub("", token)
    return token


def strip_adjectival_er(token: str) -> str:
    """Strip an adjectival ``ער`` suffix: ``בערלינער`` → ``בערלינ``.

    No-op on tokens shorter than 5 chars. Many adjectival forms map to a known
    city (ניו-יאָרקער → ניו-יאָרק); that mapping is service-specific data and is
    not provided here — services with such a map should apply it *before*
    calling this fallback."""
    if len(token) > 4 and token.endswith("ער"):
        return token[:-2]
    return token


def strip_yiddish_inflections(token: str) -> str:
    """Apply possessive-ס then (if still not matched) adjectival-ער stripping.
    Convenience wrapper — services wanting only one can call the specific
    function directly."""
    return strip_adjectival_er(strip_possessive_s(token))
