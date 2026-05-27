# Cross-Vetting Ledger

Append-only record of changes to shared matching behaviour and their disposition
across services. See the process:
[entity-matching-skill/process/cross-vetting.md](https://github.com/sinairusinek/entity-matching-skill/blob/main/process/cross-vetting.md).

One row per triggering change. Never rewrite rows; add new ones.
Vetted column values: `adopt` / `adapt` / `reject` (+reason) / `n/a`.

| Date | Change | Originated in | Belongs in core? | Vetted: Places | Vetted: People | Vetted: Orgs | Status |
|------|--------|---------------|------------------|----------------|----------------|--------------|--------|
| 2026-05-27 | Seed core: normalize_name, is_hebrew, detect_script, trigrams, name_similarity, Kima/Wikidata id helpers, cascade skeleton, review-band routing | matching-core (extraction) | yes | pending re-point | pending re-point | pending packaging | open |
| 2026-05-27 | `trigrams` promoted to top-level (was inline in Kimatch, private `_trigrams` in Shidduch) | matching-core | yes | adopt (Phase 2) | adopt (Phase 2) | n/a | open |
