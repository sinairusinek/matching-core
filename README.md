# matching-core

Shared primitives for multilingual entity matching, depended on by the
separately-released matching **services**:

- **Places** — [Kimatch](https://github.com/sinairusinek/Kimatch)
- **People** — Shidduch
- **Orgs** — Dybbuk/Zylbercweig

This package is the **single source of truth** for behaviour that is true
regardless of entity type. Domain logic (kinnui tables, patronymic parsing,
coordinate guards, org-token stripping, troupe typology) stays in the service
packages — it does **not** belong here.

> Architecture, the core/domain boundary, the Diátaxis doc split, and the
> cross-vetting process all live in the canonical doc repo:
> **[entity-matching-skill](https://github.com/sinairusinek/entity-matching-skill)**.
> Read [`architecture/matching-core-and-services.md`](https://github.com/sinairusinek/entity-matching-skill/blob/main/architecture/matching-core-and-services.md) first.

## What's in here

| Module | Provides |
|---|---|
| `normalize` | `normalize_name`, `is_hebrew`, `detect_script` |
| `similarity` | `trigrams`, `trigram_jaccard`, `name_similarity` |
| `identifiers` | `extract_kima_id`, `normalize_kima_url`, `extract_wikidata_qid`, `normalize_wikidata_url` |
| `cascade` | `Stage`, `CANONICAL_ORDER`, `run_cascade`, `MatchResult`, `ReviewBands`, `route` |

```python
from matching_core import normalize_name, name_similarity, run_cascade, Stage

normalize_name("שָׁלוֹם")          # "שלום"
name_similarity("Kraków", "Krakow")  # 1.0
```

## The cascade

Core ships the *shape*; each service supplies its own pass callables and
thresholds:

1. identifier → 2. exact_name → 3. fuzzy → 4. phonetic → 5. domain → 6. no_match

```python
result = run_cascade(query, candidates, passes={
    Stage.IDENTIFIER: my_id_pass,
    Stage.EXACT_NAME: my_exact_pass,
    Stage.FUZZY: my_fuzzy_pass,
    # phonetic/domain optional — omit a stage to skip it
})
```

## Develop

```bash
pip install -e ".[dev]"
pytest
```

The `tests/test_golden.py` set is the shared definition of "correct". Changing
an asserted output is a **cross-vetting event** — see the process doc.

## Changing core behaviour

Any change here affects every service. Follow
[the cross-vetting process](https://github.com/sinairusinek/entity-matching-skill/blob/main/process/cross-vetting.md):
log it in [`LEDGER.md`](LEDGER.md) with the Places/People/Orgs disposition.
