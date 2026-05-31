"""Tests for the primitives added in 0.2.0 (LEDGER rows 17-19).

These cover the cross-vetted Orgs-originated primitives:
- token_jaccard (row 17): order-independent token similarity
- script_runs   (row 18): per-script substring extraction
- yiddish       (row 19): opt-in morphology helpers (NOT in default cascade)
"""
from matching_core import token_jaccard, script_runs
from matching_core.yiddish import (
    is_article, is_of_token,
    strip_possessive_s, strip_adjectival_er, strip_yiddish_inflections,
)


# ── token_jaccard ─────────────────────────────────────────────────────────────

def test_token_jaccard_identical():
    assert token_jaccard("Wiener Stadttheater", "Wiener Stadttheater") == 1.0


def test_token_jaccard_word_order_independent():
    # The headline use case: same words, swapped order
    assert token_jaccard("Wiener Stadttheater", "Stadttheater Wien") < 1.0  # "Wien"≠"Wiener"
    assert token_jaccard("Yitzhak Bashevis Singer", "Singer Yitzhak Bashevis") == 1.0


def test_token_jaccard_partial_overlap():
    score = token_jaccard("Yitzhak Bashevis Singer", "Yitzhak Singer")
    # 2 shared / 3 union
    assert abs(score - 2/3) < 1e-9


def test_token_jaccard_disjoint():
    assert token_jaccard("Warsaw", "Tokyo") == 0.0


def test_token_jaccard_empty():
    assert token_jaccard("", "Warsaw") == 0.0
    assert token_jaccard("Warsaw", "") == 0.0


def test_token_jaccard_normalization_applied():
    # Diacritics folded by normalize_name before tokenizing
    assert token_jaccard("Kraków Poland", "Poland Krakow") == 1.0


# ── script_runs ───────────────────────────────────────────────────────────────

def test_script_runs_extracts_yiddish_from_mixed():
    assert script_runs("Kraków קראקא Krakau", "hebrew") == ["קראקא"]


def test_script_runs_multiple_runs():
    # Two separate Yiddish runs separated by a Latin block
    runs = script_runs("שלום Hello בית", "hebrew")
    assert runs == ["שלום", "בית"]


def test_script_runs_keeps_internal_whitespace_strips_trailing():
    # Internal space inside a run is preserved; trailing punct stripped
    assert script_runs("גאָלדפאדעןס טרופּע - Avraham Goldfaden Troupe", "hebrew") == \
        ["גאָלדפאדעןס טרופּע"]


def test_script_runs_latin_request():
    assert script_runs("Kraków קראקא Krakau", "latin") == ["Kraków", "Krakau"]


def test_script_runs_no_match_returns_empty():
    assert script_runs("Hello world", "hebrew") == []


def test_script_runs_unknown_script_returns_empty():
    assert script_runs("anything", "klingon") == []


def test_script_runs_empty_input():
    assert script_runs("", "hebrew") == []


# ── yiddish (opt-in) ──────────────────────────────────────────────────────────

def test_yiddish_articles():
    assert is_article("דער") and is_article("די") and is_article("der")
    assert not is_article("טעאַטער")


def test_yiddish_of_tokens():
    assert is_of_token("פֿון") and is_of_token("of") and is_of_token("von")
    assert not is_of_token("טעאַטער")


def test_strip_possessive_s():
    assert strip_possessive_s("גאָלדפאדעןס") == "גאָלדפאדען"
    assert strip_possessive_s("טרופּעס") == "טרופּע"
    # Too short → no-op (avoid mangling short surnames)
    assert strip_possessive_s("בנס") == "בנס"


def test_strip_adjectival_er():
    assert strip_adjectival_er("בערלינער") == "בערלינ"
    # Too short → no-op
    assert strip_adjectival_er("דער") == "דער"


def test_strip_yiddish_inflections_chain():
    # Possessive then adjectival
    assert strip_yiddish_inflections("גאָלדפאדעןס") == "גאָלדפאדען"
    assert strip_yiddish_inflections("בערלינער") == "בערלינ"


def test_yiddish_module_not_auto_imported():
    """Opt-in: importing matching_core does not pull in yiddish helpers."""
    import matching_core
    assert not hasattr(matching_core, "strip_yiddish_inflections")
    assert not hasattr(matching_core, "is_article")
