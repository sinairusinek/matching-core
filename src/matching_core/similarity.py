"""Similarity primitives — character trigrams + Jaccard.

The workhorse across every surveyed service. `trigrams` is promoted to a
top-level function here so it stops being reinvented (Kimatch had it inline,
Shidduch had a private `_trigrams`).
"""
from .normalize import normalize_name


def trigrams(s: str) -> set[str]:
    """Character trigrams of a string. Strings shorter than 3 chars yield the
    whole string as a single token (so single short tokens still compare)."""
    if len(s) < 3:
        return {s} if s else set()
    return {s[i:i + 3] for i in range(len(s) - 2)}


def trigram_jaccard(a: str, b: str) -> float:
    """Jaccard overlap of two strings' trigram sets, 0.0–1.0. Assumes inputs
    are already normalized."""
    ta, tb = trigrams(a), trigrams(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def token_jaccard(a: str, b: str) -> float:
    """Order-independent Jaccard over whitespace-split tokens of two names.

    The complement to `name_similarity` (which uses character trigrams): use
    this when word order shouldn't matter but identity-of-words should.
    Examples: "Wiener Stadttheater" ↔ "Stadttheater Wien"; "Yitzhak Singer" ↔
    "Singer Yitzhak". Both inputs are normalized first.

    Returns 0.0–1.0; 1.0 when token sets are identical after normalization.

    NOTE for People: a comma carries name-order information ("Singer, Yitzhak"
    means LastName first). That refinement is a People-domain wrapper around
    this primitive — keep it in the People service, not here.
    """
    a, b = normalize_name(a), normalize_name(b)
    if not a or not b:
        return 0.0
    ta, tb = set(a.split()), set(b.split())
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def name_similarity(a: str, b: str) -> float:
    """Normalize both names, then trigram-Jaccard. Falls back to token overlap
    when trigrams are unavailable (e.g. one-word inputs after normalization).
    Returns 0.0–1.0; 1.0 on exact normalized equality."""
    a, b = normalize_name(a), normalize_name(b)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    ta, tb = trigrams(a), trigrams(b)
    if not ta or not tb:
        wa, wb = set(a.split()), set(b.split())
        if not wa or not wb:
            return 0.0
        return len(wa & wb) / len(wa | wb)
    return len(ta & tb) / len(ta | tb)
