"""matching-core — shared primitives for multilingual entity matching.

Single source of truth for behaviour that is true regardless of entity type.
Domain logic (kinnui, patronymics, coordinate guards, org tokens) lives in the
service packages that depend on this one. See the entity-matching-skill repo for
the cascade Reference/Explanation and the cross-vetting process.
"""
from .normalize import normalize_name, is_hebrew, detect_script, script_runs
from .similarity import trigrams, trigram_jaccard, name_similarity, token_jaccard
from .identifiers import (
    normalize_kima_url,
    extract_kima_id,
    normalize_wikidata_url,
    extract_wikidata_qid,
)
from .cascade import (
    Stage,
    CANONICAL_ORDER,
    MatchResult,
    run_cascade,
    ReviewBands,
    route,
)

__version__ = "0.2.0"

__all__ = [
    "normalize_name", "is_hebrew", "detect_script", "script_runs",
    "trigrams", "trigram_jaccard", "name_similarity", "token_jaccard",
    "normalize_kima_url", "extract_kima_id",
    "normalize_wikidata_url", "extract_wikidata_qid",
    "Stage", "CANONICAL_ORDER", "MatchResult", "run_cascade",
    "ReviewBands", "route",
]
