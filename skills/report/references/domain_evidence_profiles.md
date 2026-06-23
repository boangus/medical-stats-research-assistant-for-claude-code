# Domain Evidence Profiles

> **Advisory only.** A domain evidence profile changes which evidence types the literature screening *admits*. It never changes the A-F Overall Grade and never blocks manuscript ship. It never changes which databases are queried (that stays `Discipline`-driven in `literature_search_agent` Step 2). Consumed only by `medical-paper`'s `literature_search_agent`; produced by `paper_config_agent` Step 12 as the PCR `Domain Evidence Profile` row.

## Domain Evidence Profiles

The ship-ready enum is exactly four values. `unknown_user_defined` is the default and the neutral fallback.

| Profile | Standard evidence types | Common provenance requirements | Critical gaps to surface | Reserved-note |
|---|---|---|---|---|
| `general_social_science` | Peer-reviewed empirical studies, mixed-methods, expert-panel / context-dependent policy analyses | Journal or proceedings; expert-panel reports acceptable where context-dependent | Single-context generalization; weak external validity | 鈥?(ship-ready) |
| `cs_ml` | Peer-reviewed papers AND archival preprints (e.g. arXiv), conference proceedings; industry technical reports | Preprint server or proceedings acceptable; peer-review lags the field | Non-reproducible results; benchmark cherry-picking | 鈥?(ship-ready) |
| `humanities_interpretive` | Primary sources, archival material, canonical/older texts, monographs | Primary-source provenance; recency is not a quality signal | Interpretive over-reach; missing primary-source grounding | 鈥?(ship-ready) |
| `unknown_user_defined` | Neutral single-pyramid (pre-#259 behavior) 鈥?peer-reviewed default | Standard peer-review expectation | (no profile-specific loosening) | Default / neutral fallback |

**Reserved profiles (documented, NOT in the enum).** Selecting one records effective `unknown_user_defined` and surfaces a reserved-fallback advisory 鈥?its checklist does not exist yet, so it falls back to neutral to prevent false rigor:

`clinical` 路 `wet_lab` 路 `materials_physics` 路 `legal_case_based` 路 `education` 鈥?*not in enum yet; selecting this falls back to `unknown_user_defined`.*

## Field-guidance carry-forward (seeded from the systematic-survey evidence hierarchy)

The substance of the field-centric `## Field-Specific Adjustments` table in `systematic-survey/references/source_quality_hierarchy.md` is carried forward here so no per-field guidance is silently dropped. The systematic-survey file is **read, not edited** 鈥?this is a one-time authoring copy, not a runtime dual-read.

Normative (folded into a ship-ready profile row above):
- **Social Science** 鈫?folded into `general_social_science` (Level III-V; mixed methods common).
- **Technology** 鈫?folded into `cs_ml` (Level III + industry reports; peer review lags reality).
- **Humanities** 鈫?folded into `humanities_interpretive` (Level VI primary sources; different epistemology 鈥?"evidence" means different things).
- **Policy** 鈫?folded into `general_social_science` (Level IV-V + VII expert panels; context-dependent, expert opinion valued). There is no dedicated Policy profile.

**Historical reference 鈥?non-normative; current behavior for these domains is neutral `unknown_user_defined` until the `clinical` / `education` profile ships:**
- **Medicine/Health** 鈥?Level I-II (RCTs, meta-analyses); Level I-III common; evidence-based-medicine tradition. *(maps to reserved `clinical`)*
- **Education** 鈥?Level III-IV (quasi-experimental); Level IV-VI common; randomization often impractical. *(maps to reserved `education`)*

These two rows are preserved verbatim for the eventual `clinical` / `education` profiles. They do NOT change runtime behavior today: until those reserved profiles ship, Medicine/Health and Education runs use the neutral `unknown_user_defined` pyramid, exactly as every other unmapped selection does.

## #246 forward reference

Discipline-relative *grade aggregation* (how these evidence expectations roll up into an Overall Grade) is tracked separately in #246 and is **not yet implemented**. Until #246 ships, the A-F Overall Grade lookup in `systematic-survey/references/source_quality_hierarchy.md` applies unchanged. #259 ships no aggregation logic and no placeholder aggregation code.
