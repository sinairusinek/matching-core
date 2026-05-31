"""Tests for the opt-in romanization tables added in 0.3.0 (LEDGER row 15).

Polish digraph→Yiddish substitution: originated in Dybbuk's
translit_latin_to_yiddish.py after the Fiszon-troupe miss (a Polish-romanized
surname `Fiszon` was degrading to פֿיסזאָן because `sz` wasn't recognized as the
Yiddish ש sibilant — pushing the candidate below the fuzzy floor).
"""
from matching_core.transliteration import (
    POLISH_DIGRAPHS_TO_YIDDISH,
    apply_polish_digraphs,
)


def test_table_present():
    # The four digraphs whose absence caused real-world matching failures.
    for src in ("sz", "szcz", "cz", "rz"):
        assert src in POLISH_DIGRAPHS_TO_YIDDISH


def test_longest_first_szcz_beats_sz_cz():
    # `szcz` must win; otherwise it would degrade to ש + טש (sh + ch).
    assert apply_polish_digraphs("szcz") == "שטש"


def test_fiszon_surname_canonical_case():
    # The motivating regression: `Fiszon` was matching as Fi+s+z+on (פיסזאן),
    # not Fi+sh+on (פישאן). After the lift, the digraph wins.
    out = apply_polish_digraphs("Fiszon")
    assert "ש" in out
    assert "סז" not in out


def test_rz_to_zsh():
    assert apply_polish_digraphs("rz") == "זש"


def test_cz_to_tsh():
    assert apply_polish_digraphs("cz") == "טש"


def test_case_insensitive():
    assert apply_polish_digraphs("SZ") == "ש"
    assert apply_polish_digraphs("Sz") == "ש"


def test_non_digraph_chars_passed_through():
    # The function rewrites only the Polish digraphs; everything else is
    # returned unchanged (services compose their own single-letter map next).
    out = apply_polish_digraphs("Fiszon")
    assert out.startswith("Fi")
    assert out.endswith("on")


def test_empty_string():
    assert apply_polish_digraphs("") == ""


def test_no_digraphs_is_identity():
    assert apply_polish_digraphs("Krakow") == "Krakow"


def test_not_in_default_namespace():
    # Opt-in module: must NOT be re-exported from the top-level package.
    import matching_core
    assert not hasattr(matching_core, "apply_polish_digraphs")
    assert not hasattr(matching_core, "POLISH_DIGRAPHS_TO_YIDDISH")
