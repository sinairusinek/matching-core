"""The cascade skeleton + review-band routing.

This is the *shape* every service shares, per the entity-matching skill:

    1. identifier   — exact match on stable IDs (QID, Kima ID). Cheapest, highest precision.
    2. exact_name   — exact match after normalization.
    3. fuzzy        — trigram-Jaccard, threshold tuned per entity type.
    4. phonetic     — only when scripts differ / transliteration is the dominant failure mode.
    5. domain       — kinnui, abbreviation expansion, org-token equivalence, etc.
    6. no_match     — surface for human review rather than forcing a low-confidence merge.

Core ships the skeleton and the routing primitive. Each service supplies the
actual pass callables (especially phonetic + domain) and its own thresholds.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional, Sequence


class Stage(str, Enum):
    IDENTIFIER = "identifier"
    EXACT_NAME = "exact_name"
    FUZZY = "fuzzy"
    PHONETIC = "phonetic"
    DOMAIN = "domain"
    NO_MATCH = "no_match"


# Canonical ordering: cheaper/more-precise passes first, lossy passes as fallback.
CANONICAL_ORDER: tuple[Stage, ...] = (
    Stage.IDENTIFIER,
    Stage.EXACT_NAME,
    Stage.FUZZY,
    Stage.PHONETIC,
    Stage.DOMAIN,
)


@dataclass
class MatchResult:
    matched_id: Optional[str]
    score: float
    stage: Stage
    candidate: object = None
    notes: dict = field(default_factory=dict)


# A pass takes (query, candidates) and returns a MatchResult or None to fall through.
Pass = Callable[[object, Sequence[object]], Optional[MatchResult]]


def run_cascade(query: object,
                candidates: Sequence[object],
                passes: dict[Stage, Pass],
                order: Sequence[Stage] = CANONICAL_ORDER) -> MatchResult:
    """Run the supplied passes in canonical order; first non-None wins.
    Stages absent from `passes` are skipped (e.g. a service with no phonetic
    pass simply omits Stage.PHONETIC). Returns a NO_MATCH result if all fall
    through."""
    for stage in order:
        fn = passes.get(stage)
        if fn is None:
            continue
        result = fn(query, candidates)
        if result is not None:
            return result
    return MatchResult(matched_id=None, score=0.0, stage=Stage.NO_MATCH)


# ── Review-band routing ───────────────────────────────────────────────────────
# Shared convention across services: a score (or pass) maps to an action grade.
# A = auto-link, B/C = human review tiers, D = no link. Services pick their own
# band edges but use the same grade vocabulary so review queues are comparable.

@dataclass
class ReviewBands:
    autolink: float = 0.90   # >= this → A_autolink
    review_hi: float = 0.75  # >= this → B_review
    review_lo: float = 0.60  # >= this → C_review; below → D_no_link


def route(score: float, bands: ReviewBands = ReviewBands()) -> str:
    """Map a similarity score to a review grade: A_autolink / B_review /
    C_review / D_no_link."""
    if score >= bands.autolink:
        return "A_autolink"
    if score >= bands.review_hi:
        return "B_review"
    if score >= bands.review_lo:
        return "C_review"
    return "D_no_link"
