"""Stable-identifier extraction and URL canonicalization.

Pass 1 of the cascade (identifier match) is the cheapest, highest-precision
pass. These helpers parse Kima and Wikidata references into a canonical form so
exact-ID matching works regardless of how the source wrote the reference.

Seeded from Kimatch/kimatch/core/normalizers.py.
"""
import re
from typing import Optional


# ── Kima ──────────────────────────────────────────────────────────────────────

def normalize_kima_url(value: str) -> Optional[str]:
    """Canonicalize any Kima reference to
    https://data.geo-kima.org/Places/Details/{N}.

    Handles the canonical URL, the /Details?id=N variant, a bare numeric ID,
    and pipe-separated lists (takes the first value)."""
    if not value:
        return None
    value = str(value).strip().split("|")[0].strip()
    if not value:
        return None
    if "Places/Details/" in value:
        return value
    m = re.search(r"[?&]id=(\d+)", value)
    if m:
        return f"https://data.geo-kima.org/Places/Details/{m.group(1)}"
    if re.match(r"^\d+(\.\d+)?$", value):
        return f"https://data.geo-kima.org/Places/Details/{int(float(value))}"
    return value


def extract_kima_id(value: str) -> Optional[int]:
    """Return the numeric Kima ID from a URL or bare number, or None."""
    if not value:
        return None
    value = str(value).strip()
    m = re.search(r"/Details/(\d+)", value)
    if m:
        return int(m.group(1))
    m = re.search(r"[?&]id=(\d+)", value)
    if m:
        return int(m.group(1))
    if re.match(r"^\d+$", value):
        return int(value)
    return None


# ── Wikidata ────────────────────────────────────────────────────────────────

def normalize_wikidata_url(value: str) -> Optional[str]:
    """Return canonical https://www.wikidata.org/wiki/QXXXX URL, or None."""
    if not value:
        return None
    m = re.search(r"(Q\d+)", str(value).strip())
    return f"https://www.wikidata.org/wiki/{m.group(1)}" if m else None


def extract_wikidata_qid(value: str) -> Optional[str]:
    """Return the bare Q-number from a Wikidata URL or Q-string, or None."""
    if not value:
        return None
    m = re.search(r"(Q\d+)", str(value))
    return m.group(1) if m else None
