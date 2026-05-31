"""Optional romanization / transliteration tables.

NOT used by the default cascade and NOT auto-imported by `matching_core`.
Services opt in by importing explicitly:

    from matching_core.transliteration import (
        POLISH_DIGRAPHS_TO_YIDDISH, apply_polish_digraphs,
    )

Seeds the transliteration layer that core has otherwise lacked. Each table is a
*data primitive* — the orthographic fact that "sz" in Polish romanization spells
the same sibilant Yiddish writes as ש. Services compose these tables into their
own translit pipelines; this module does not own a full Latin→<script>
transliterator (per-target orthography, single-letter maps, and final-form
handling stay service-specific).

Disposition (LEDGER row 15, 2026-05-27 → closed 2026-05-31):
    - Orgs:   primary user — origin (Dybbuk translit_latin_to_yiddish.py was
              missing these and degrading `Fiszon` → פֿיסזאָן)
    - People: OPT-IN — Shidduch sees Polish-spelled surnames (Fiszon, Wiśniewski,
              Bryzgalski) and should apply this on the romanization side before
              its Beider-Morse / translit_me pass
    - Places: ADAPT — Polish town spellings (Krzemieniec, Łódź romanized as
              `Lodz`); for Hebrew/Latin gazetteers the Yiddish target script
              isn't directly useful — Kimatch should treat this as guidance on
              which digraph clusters mean the same phoneme, not as a literal
              substitution
"""
from __future__ import annotations

from typing import Mapping

# Polish romanization → Yiddish-script orthography.
#
# Longest first is significant: ``szcz`` must beat ``sz``+``cz``. Apply via
# left-to-right longest-prefix substitution (see `apply_polish_digraphs`).
#
# Coverage: the four digraphs whose absence causes silent matching failures in
# real corpora. Not exhaustive (Polish has more — ść, ź, ż, dż, ł, etc.); add
# them here, with one test each, as real misses surface in the ledger.
POLISH_DIGRAPHS_TO_YIDDISH: Mapping[str, str] = {
    "szcz": "שטש",
    "sz":   "ש",
    "cz":   "טש",
    "rz":   "זש",
}


def apply_polish_digraphs(text: str) -> str:
    """Apply :data:`POLISH_DIGRAPHS_TO_YIDDISH` as a left-to-right
    longest-prefix substitution, case-insensitively.

    ``Fiszon``  → ``Fi`` + ``ש`` + ``on``  (the surrounding chars are returned
    unchanged; this function only rewrites the Polish digraphs).

    Services typically run this *before* their single-letter Latin→<script>
    map, so the digraph wins over the per-letter fallback (``s``+``z``).
    """
    if not text:
        return ""
    # Sort by length DESC so longest patterns match first inside the scan loop.
    patterns = sorted(POLISH_DIGRAPHS_TO_YIDDISH.items(), key=lambda kv: -len(kv[0]))
    out: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        chunk = text[i:].lower()
        for src, dst in patterns:
            if chunk.startswith(src):
                out.append(dst)
                i += len(src)
                break
        else:
            out.append(text[i])
            i += 1
    return "".join(out)
