"""Golden test set — the shared definition of "correct".

Every service depends on these behaviours being stable. Changing an asserted
output here is a cross-vetting event (see entity-matching-skill/process/cross-vetting.md):
it means all services' notion of normalization just changed.
"""
from matching_core import (
    normalize_name, is_hebrew, detect_script,
    trigrams, name_similarity,
    extract_kima_id, extract_wikidata_qid, normalize_kima_url,
    run_cascade, Stage, MatchResult, route,
)


# ── normalize_name ────────────────────────────────────────────────────────────
NORMALIZE_CASES = [
    ("", ""),
    ("  Warsaw  ", "warsaw"),
    ("Łódź", "łodz"),                       # Latin diacritics folded (NFD strips Mn)
    ("Kraków", "krakow"),
    ("שלום", "שלום"),                        # plain Hebrew unchanged
    ("שָׁלוֹם", "שלום"),                       # nikud stripped
    ("ד״ר", "דר"),                           # gershayim removed
    ("ב׳", "ב"),                             # geresh removed
    ("O'Brien", "obrien"),                   # apostrophe removed
    ("New   York", "new york"),              # whitespace collapsed
]


def test_normalize_name_golden():
    for raw, expected in NORMALIZE_CASES:
        assert normalize_name(raw) == expected, raw


def test_is_hebrew():
    assert is_hebrew("שלום")
    assert is_hebrew("Tel שלום")
    assert not is_hebrew("Warsaw")
    assert not is_hebrew("")


def test_detect_script():
    assert detect_script("Warsaw") == "latin"
    assert detect_script("ורשע") == "hebrew"
    assert detect_script("Москва") == "cyrillic"
    assert detect_script("القاهرة") == "arabic"
    assert detect_script("123 !!!") == "unknown"
    # Mixed: dominant script wins
    assert detect_script("ורשע Warsaw ורשע ורשע") == "hebrew"


# ── trigrams / similarity ─────────────────────────────────────────────────────

def test_trigrams_short_string():
    assert trigrams("ab") == {"ab"}
    assert trigrams("") == set()
    assert trigrams("abc") == {"abc"}
    assert trigrams("abcd") == {"abc", "bcd"}


def test_name_similarity_bounds():
    assert name_similarity("Warsaw", "Warsaw") == 1.0
    assert 0.2 < name_similarity("Warsaw", "Warszawa") < 0.5  # partial overlap
    assert name_similarity("Warsaw", "") == 0.0
    assert name_similarity("Warsaw", "Tokyo") < 0.2
    # normalization makes diacritic variants near-identical
    assert name_similarity("Kraków", "Krakow") == 1.0


# ── identifiers ───────────────────────────────────────────────────────────────

def test_extract_kima_id():
    assert extract_kima_id("https://data.geo-kima.org/Places/Details/123") == 123
    assert extract_kima_id("https://x/Details?id=456") == 456
    assert extract_kima_id("789") == 789
    assert extract_kima_id("") is None
    assert extract_kima_id("not-an-id") is None


def test_normalize_kima_url():
    canon = "https://data.geo-kima.org/Places/Details/42"
    assert normalize_kima_url("42") == canon
    assert normalize_kima_url(canon) == canon
    assert normalize_kima_url("42|99") == canon  # pipe list → first


def test_extract_wikidata_qid():
    assert extract_wikidata_qid("https://www.wikidata.org/wiki/Q1741") == "Q1741"
    assert extract_wikidata_qid("Q1741") == "Q1741"
    assert extract_wikidata_qid("nope") is None


# ── cascade + routing ─────────────────────────────────────────────────────────

def test_run_cascade_first_non_none_wins():
    def id_pass(q, cands):
        return None  # falls through

    def exact_pass(q, cands):
        return MatchResult(matched_id="X1", score=1.0, stage=Stage.EXACT_NAME)

    res = run_cascade("q", [], {Stage.IDENTIFIER: id_pass,
                                Stage.EXACT_NAME: exact_pass})
    assert res.matched_id == "X1"
    assert res.stage == Stage.EXACT_NAME


def test_run_cascade_no_match():
    res = run_cascade("q", [], {Stage.IDENTIFIER: lambda q, c: None})
    assert res.stage == Stage.NO_MATCH
    assert res.matched_id is None


def test_route_grades():
    assert route(0.95) == "A_autolink"
    assert route(0.80) == "B_review"
    assert route(0.65) == "C_review"
    assert route(0.10) == "D_no_link"
