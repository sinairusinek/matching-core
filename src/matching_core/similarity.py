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
