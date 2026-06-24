# Changelog

All notable changes to MSRA (Medical Statistics Research Assistant) will be documented in this file.

## [1.0.0] - 2026-06-26

**First stable release.** All four extension modules reach Stable maturity. End-to-end test suite covers 10 scenarios. User tutorials and API reference documentation complete.

### Added

- **`msra_modules/cross_domain/quality_gates.py`** — `CrossDomainQualityGateChecker`: Gate CD-1.5 (5 items: feature matrix integrity 🔑, sample ID alignment 🔑, missing rate, data type consistency, modality coverage) + Gate CD-3.5 (5 items: correlation significance 🔑, model performance 🔑, feature stability 🔑, visualization consistency, cross-modal evidence). Reuses `shared/quality_gates/GateRunner`.
- **`msra_modules/cross_domain/integration.py`** — `DataAligner` class (multi-modal data alignment by sample ID, missing value handling, feature matrix export) + `export_v1_schema()` for msra/cross_domain_result/v1 output + 3 existing classes (CorrelationAnalyzer, PredictionModelBuilder, MultiModalVisualizer).
- **`msra_modules/cross_domain/__init__.py`** — Exports 6 symbols: `CrossDomainQualityGateChecker`, `DataAligner`, `CorrelationAnalyzer`, `PredictionModelBuilder`, `MultiModalVisualizer`, `export_v1_schema`.
- **`skills/cross-domain/SKILL.md`** — Skill entry point for `/msra-cross`. Phase 0-4 (interactive config → QC+alignment → background fusion analysis → result review → integration). 4 IRON RULES, Gate CD-1.5/3.5 references.
- **`shared/contracts/cross_domain_result_schema.md`** — Schema contract for msra/cross_domain_result/v1.
- **`tests/test_cross_domain/`** — 42 unit tests covering quality gates, data aligner, correlation analyzer, prediction model builder, visualizer, and integration.
- **`tests/e2e/`** — End-to-end test suite: 53 tests across 10 scenarios (correlation, prediction, visualization, full pipeline, error handling). Includes `conftest.py` + 4 test files + 5 fixture generators.
- **`docs/user_guide/`** — 8 user tutorial documents (4 modules × zh/en bilingual): bioinformatics, medical_imaging, realtime_analytics, cross_domain.
- **`docs/api/`** — 8 API reference documents (4 modules × zh/en bilingual): bioinformatics, medical_imaging, realtime_analytics, cross_domain.
- **`docs/dev/harmonypy-windows-installation.md`** — Windows installation guide for harmonypy (optional bioinformatics dependency).
- **`pyproject.toml`** — Added `cross_domain` optional dependency group (scipy, scikit-learn, matplotlib). Added `experimental` group (includes all 4 modules). Added `all` group (experimental + dev).
- **`manifest.json`** — Registered `/msra-cross` command. Updated `/msra-modules` description to include cross-domain.

### Changed

- **Version**: 0.9.7 → 1.0.0 (pyproject.toml, manifest.json)
- **Development Status classifier**: `4 - Beta` → `5 - Production/Stable`
- **Module maturity — all 4 modules promoted to Stable**:
  - `bioinformatics`: 🟡 Beta → 🟢 Stable (62 tests, full Skill + quality gates + documentation)
  - `medical_imaging`: 🟡 Beta → 🟢 Stable (60 tests, full Skill + quality gates + documentation)
  - `realtime_analytics`: 🟡 Beta → 🟢 Stable (102 tests, full Skill + quality gates + documentation)
  - `cross_domain`: 🔴 Alpha → 🟢 Stable (42 unit tests + 53 E2E tests, full Skill + quality gates + documentation)
- **`README.md`** — Updated command count (12 → 16), added `/msra-cross` to command table, added cross_domain module to maturity table, updated project structure (added `skills/cross-domain/`, `tests/e2e/`, `docs/user_guide/`, `docs/api/` directories), added `/msra-cross` usage examples, updated all 3 experimental modules to Stable.
- **`docs/dev/18-实验性模块设计.md`** — Updated cross_domain status (🔴 Alpha → 🟢 Stable), updated bio/imaging/rt status (🟡 Beta → 🟢 Stable), added Gate CD-1.5/3.5 definitions, updated §18.8.2 status table.
- **`docs/dev/MSRA开发进度表.md`** — Added cross_domain module progress (100% Stable), updated three experimental modules to 100% Stable, updated version to v1.0.0.

### Test Results

- **319 passed, 0 failed, 0 skipped**
  - 42 cross_domain unit tests
  - 53 E2E tests (10 scenarios)
  - 62 bioinformatics tests
  - 60 medical_imaging tests
  - 102 realtime_analytics tests

## [0.9.7] - 2026-06-24

Realtime Analytics module Phase 3: Alpha → Beta. Full SOP pipeline (PM → Architect → Engineer → QA).

### Added
- **`skills/realtime-monitor/SKILL.md`** — Skill entry point for `/msra-rt`. Phase 0-4 (config → stream+QC → background processing → review → report). 4 IRON RULES, Gate RT-1 references.
- **`msra_modules/realtime_analytics/quality_gates.py`** — `RealtimeQualityGateChecker`: Gate RT-1 (3 items: data source available 🔑, timestamp continuity 🔑, detection sensitivity). Reuses `shared/quality_gates/GateRunner`.
- **`msra_modules/realtime_analytics/anomaly_detector.py`** — Added `DetectionResult` dataclass + `MultivariateDetector` class (Isolation Forest via sklearn). Resolves naming conflict with `alert_system.Alert`.
- **`msra_modules/realtime_analytics/stream_processor.py`** — Added `aggregate()`, `get_all_metrics()`, `process_event()` methods.
- **`manifest.json`** — Registered `/msra-rt` command.
- **`pyproject.toml`** — Added `realtime_analytics` optional dependency group (numpy, scipy, scikit-learn).
- **`tests/test_realtime_analytics/`** — 102 test cases (all passed):
  - `test_stream_processor.py` (26 tests)
  - `test_anomaly_detector.py` (20 tests)
  - `test_alert_system.py` (11 tests)
  - `test_quality_gates.py` (22 tests)
  - `test_integration.py` (9 tests)

### Changed
- **`msra_modules/realtime_analytics/__init__.py`** — version 1.1.0 → 1.2.0, added exports: `DetectionResult`, `MultivariateDetector`, `RealtimeQualityGateChecker`
- **`docs/dev/18-实验性模块设计.md`** — realtime_analytics status updated to Beta
- **`docs/dev/MSRA开发进度表.md`** — #61 realtime_analytics 10% → 100%

### Test Results
- Total: 102 realtime analytics tests (102 passed, 0 failed)

## [0.9.6] - 2026-06-24

Medical Imaging module Phase 2: Alpha → Beta. Full SOP pipeline (PM → Architect → Engineer → QA).

### Added
- **`skills/imaging-analysis/SKILL.md`** — Skill entry point for `/msra-imaging`. Phase 0-4 (config → QC+preprocess → background analysis → review → integration). 4 IRON RULES, Gate IMG-1 references.
- **`msra_modules/medical_imaging/quality_gates.py`** — `ImagingQualityGateChecker`: Gate IMG-1 (4 items: file readable 🔑, voxel spacing 🔑, ROI match 🔑, image quality). Reuses `shared/quality_gates/GateRunner`.
- **`msra_modules/medical_imaging/feature_selection.py`** — `FeatureSelector`: 7 methods (variance_threshold, k_best, mutual_info, rfe, correlation_filter, auto_select, select). Based on sklearn.
- **`msra_modules/medical_imaging/image_loader.py`** — Added `load_nifti()` (nibabel) and `load_nrrd()` (SimpleITK) utility functions.
- **`msra_modules/medical_imaging/radiomics.py`** — Added `export_v1_schema()` for msra/imaging_features/v1 output (feature_matrix.csv + feature_metadata.csv).
- **`manifest.json`** — Registered `/msra-imaging` command.
- **`pyproject.toml`** — Added `medical_imaging` optional dependency group (nibabel, SimpleITK, pyradiomics, scikit-image).
- **`tests/test_medical_imaging/`** — 60 test cases (46 passed, 14 skipped due to optional nibabel/SimpleITK):
  - `test_image_loader.py` (10 tests)
  - `test_radiomics.py` (9 tests)
  - `test_feature_selection.py` (14 tests)
  - `test_quality_gates.py` (16 tests)
  - `test_integration.py` (4 tests)

### Changed
- **`msra_modules/medical_imaging/__init__.py`** — version 1.1.0 → 1.2.0, added exports: `FeatureSelector`, `ImagingQualityGateChecker`, `load_nifti`, `load_nrrd`
- **`docs/dev/18-实验性模块设计.md`** — medical_imaging status updated to ✅ Beta
- **`docs/dev/MSRA开发进度表.md`** — #59 medical_imaging 50% → 80%

### Test Results
- Total: 60 imaging tests (46 passed, 14 skipped — nibabel/SimpleITK not installed)

## [0.9.5] - 2026-06-24

Bioinformatics module Phase 1: Alpha → Beta. Full SOP pipeline (PM → Architect → Engineer → QA).

### Added
- **`skills/bioinformatics/SKILL.md`** — Skill entry point for `/msra-bio` command. Phase 0-4 definition (interactive config → QC+standardization → background analysis → result review → integration). 6 IRON RULES, Gate Bio-1.5/3.5 references.
- **`msra_modules/bioinformatics/enrichment.py`** — `PathwayEnrichment` class: GO (BP/MF/CC), KEGG, GSEA, Enrichr ORA via gseapy. Export to CSV/TSV/JSON.
- **`msra_modules/bioinformatics/batch_correction.py`** — `BatchCorrector` class: batch effect detection (PCA variance), ComBat correction, Harmony correction, before/after comparison.
- **`msra_modules/bioinformatics/quality_gates.py`** — `BioQualityGateChecker` class: Gate Bio-1.5 (5 items: count matrix integrity 🔑, sample consistency 🔑, library size, gene annotation, batch effect) + Gate Bio-3.5 (5 items: p-value distribution 🔑, effect consistency 🔑, multiple testing 🔑, enrichment FDR, visualization consistency). Reuses `shared/quality_gates/GateRunner`.
- **`manifest.json`** — Registered `/msra-bio` command pointing to `skills/bioinformatics/SKILL.md`.
- **`tests/test_bioinformatics/`** — 62 test cases (39 passed, 23 skipped due to optional deps):
  - `test_enrichment.py` (15 tests): PathwayEnrichment unit tests
  - `test_batch_correction.py` (10 tests): BatchCorrector unit tests
  - `test_quality_gates.py` (25 tests): Gate Bio-1.5/3.5 logic tests
  - `test_integration.py` (12 tests): end-to-end integration tests
- **`docs/prd/bioinformatics-module-prd.md`** — Product Requirements Document
- **`docs/system_design.md`** — Architecture design + task decomposition
- **`docs/dev/18-实验性模块设计.md`** — bioinformatics status updated to 🟡 Beta

### Changed
- **`msra_modules/bioinformatics/__init__.py`** — version 1.0.0 → 1.1.0, added exports: `PathwayEnrichment`, `BatchCorrector`, `BioQualityGateChecker`
- **`docs/dev/MSRA开发进度表.md`** — #60 bioinformatics 10% → 60%, test count updated

### Test Results
- Total: 62 bioinformatics tests (39 passed, 23 skipped — anndata not installed)
- QA Verdict: PASS, smart routing: NoOne
- Global consistency check: IS_PASS: YES

## [0.9.3] - 2026-06-23

System optimization round: graceful degradation, test fixes, unified evaluation, anti-pattern cases.

### Added
- **`scripts/run_evals.py`** — unified evaluation runner for 3 suites (pipeline-gold 21 cases + method-selection 10 cases + end-to-end 5 cases = 36 cases, 100% pass)
- **Anti-pattern detailed code cases** — 6 cases (A1/A2/A5/A6/B1/D1) with ❌ wrong vs ✅ correct code examples, +8 detection checklist items (AP-01~AP-08). File grew from 609→841 lines
- **`pyyaml`** to requirements-dev.txt (for variable_standardization YAML mapping support)

### Changed
- **`shared/large_scale_processing/engine_factory.py`**: graceful degradation — when preferred engine unavailable, auto-fallback to next best engine with warning log. Added `_ENGINE_FALLBACK` mapping and `allow_fallback` parameter
- **`shared/large_scale_processing/dask_engine.py`**: safe import using `TYPE_CHECKING` + `_DASK_AVAILABLE` flag. Module can be safely imported even when dask is not installed
- **`pytest.ini` + `pyproject.toml`**: added `asyncio_mode = auto` for async test support
- **`tests/test_psm.py`**: fixed API mismatch — `nearest_neighbor_match` was called with 2 DataFrames but expects (data, treatment_col, ...). Now correctly passes full DataFrame + column name
- **`tests/test_large_scale_integration.py`**: updated dask tests to accept fallback engines and skip when dask unavailable

### Fixed
- **27 async test failures** in `test_agent_framework.py` — were failing because `pytest-asyncio` wasn't configured with auto mode
- **2 large_scale_integration failures** — dask engine import crashed the factory; now gracefully degrades to duckdb
- **3 PSM test skips** — API mismatch caused `ValueError: No matches found`; now correctly uses single-DataFrame API

### Test Results
- Before: 507 passed, 2 failed, 3 skipped
- After: 511 passed, 0 failed, 1 skipped
- Evaluation: 36/36 gold cases pass (100%)

## [0.9.2] - 2026-06-23

Documentation system + Multi-Agent architecture design.

### Added
- 28 development documents in `docs/dev/` covering architecture, modules, contracts, quality gates, templates
- Multi-Agent framework design: 5 Agent roles + HybridModeBridge for Skill-Agent integration
- Mixed mode architecture (Mode C): orchestrator Skill + key roles as sub-Agents

## [0.9.1] - 2026-06-21

Medical domain refactoring, protocol adherence framework, and quality control enhancements.

### Added
- **Stage 1.8: exploratory-causal skill** 9data-driven causal discovery (PC/FCI algorithm), confounding analysis, hypothesis generation, with Bradford Hill 9 criteria + Pearl SCM framework integration
- **`shared/protocol_adherence/`** (3 files) 9protocol adherence & change management framework:
  - `protocol_adherence_framework.md` (620 lines): 4-tier change management (A/B/C/D), progress tracking, four-point consistency check
  - `progress_tracker_template.md` (176 lines): analysis progress tracking template
  - `method_consistency_rules.md` (603 lines): weighted data consistency rules, chart standards, variable name confirmation workflow
- **`shared/variable_naming_standards.md`** (677 lines) 9academic variable naming & statistical format standards (50+ variable mapping table)
- **`shared/variable_standardization/`** (4 files) 9automated standardization module:
  - `VariableStandardizer`: 40+ built-in medical variable mappings, DataFrame column standardization
  - `StatFormatter`: P-value/CI/median-IQR/mean-SD/survival time formatting
  - `mapping_template.yaml`: 60+ variable mapping template
- **KM survival curve professional rules** 9weighted/unweighted risk table display rules, statistical test selection, censoring visualization standards

### Changed
- **Medical domain refactoring**: all upstream-derived content rewritten as medical-specific versions
  - `systematic-survey` 9`systematic-survey` (medical systematic review search)
  - `medical-paper-reviewer` 9`peer-review` (medical journal peer review)
  - `resources/medical-paper/` 9`resources/medical-paper/`
  - `resources/medical-pipeline/` 9`resources/medical-pipeline/`
  - 14 shared/ protocol files rewritten to 6 medical-specific versions
  - 5 shared/references/ files rewritten with medical terminology
  - 14 shared/contracts/ reduced to 8 medical pipeline schemas
- **analysis-exec SKILL.md**: added Phase 0.5 (progress tracking init), Phase 0.6 (variable name confirmation), enhanced Phase 4 quality checklist (13 new items)
- **License**: CC BY-NC-SA 4.0 → dual MIT + CC BY-NC-SA 4.0 (code=MIT, knowledge-base=CC-BY-NC-SA)

### Fixed
- CI test failures: pytest.ini --cov removed (pytest-cov not installed), test assertions updated
- Python module naming: `chart-understanding` 9`chart_understanding`, `report-assembler` 9`report_assembler`, `table-understanding` 9`table_understanding`

## [0.9.0] - 2026-06-21

Large-scale data processing: handle datasets >1M rows (GB-TB scale) without memory overflow.

### Summary
Adds three processing engines (Polars/DuckDB/Dask) with automatic engine selection based on data size.
Solves the core pain point of pandas memory overflow for large medical datasets.

### Added
- **`shared/large_scale_processing/`** (7 files) 9unified data processing module:
  - `engine_selector.py`: `ProcessingEngine` enum + `EngineSelector` class for auto-selection
  - `base_engine.py`: `BaseEngine` abstract class defining unified API
  - `polars_engine.py`: Fast in-memory processing (<10GB), 31 tests
  - `duckdb_engine.py`: SQL-friendly OLAP (10-100GB), 20 tests
  - `dask_engine.py`: Distributed processing (>100GB), 15 tests
  - `engine_factory.py`: `EngineFactory` for unified instantiation

- **`tests/`** (6 new files):
  - `test_engine_selector.py`: 27 tests
  - `test_polars_engine.py`: 31 tests
  - `test_duckdb_engine.py`: 20 tests
  - `test_dask_engine.py`: 15 tests
  - `test_engine_factory.py`: 21 tests
  - `test_large_scale_integration.py`: 22 integration tests

- **`scripts/benchmark_large_scale.py`**: Performance benchmark script (100K-10M rows)

- **`docs/large-scale-processing-guide.md`**: Complete usage guide with examples and tips

- **`requirements.txt`**: New dependencies (polars, duckdb, dask, pyarrow)

### Engine Selection Logic
| Data Size | Engine | Use Case |
|-----------|--------|----------|
| <1GB | pandas | Compatibility |
| 1-10GB | Polars | Fast in-memory |
| 10-100GB | DuckDB | SQL OLAP |
| >100GB | Dask | Distributed |

### Performance (100K rows)
| Engine | CSV Read | GroupBy |
|--------|----------|---------|
| Polars | 0.01s | 0.009s |
| DuckDB | 0.071s | 0.002s |
| Dask | 0.146s | 0.146s |

### Test Results
- Total: 88 passed tests
- Coverage: 95+ unit tests + 22 integration tests

## [0.8.0] - 2026-06-18

MSRA × MSRA integration 9unified pipeline: raw data 9statistical report 9(optional) submittable paper.

### Summary
Merges MSRA (Academic Research Skills) capability into MSRA, forming a single project.
Users flow from Stage 1 through Stage 4 (stats report), then choose [A] done / [B] write paper.
The Paper Track dispatches to MSRA's `medical-pipeline` skill (literature 9write 9review 9revise 9finalize).
MSRA provides clinical reporting expertise (CONSORT/STROBE/STARD/16 checklists) that MSRA natively lacks.

### Added
- **`shared/` MSRA dependencies merged** (44 files): handoff_schemas, contracts, references, templates, .claude/CLAUDE.md
- **`commands/MSRA-*.md`** (14 files): MSRA slash commands (MSRA-full, MSRA-reviewer, MSRA-revision, etc.)
- **Paper Track (Stage 5)**: Stage 5.0 Paper Intake + dispatch to medical-pipeline for Stage 5.1-5.9
- **`scripts/generate_msra_handoff_bundle.py`**: generates MSRA Handoff Bundle (spec §4.4) for medical-paper bridge
- **`commands/msra-paper.md`**: new `/msra-paper` command for direct Paper Track entry
- **`shared/passport/passport.py`**: `track` field (`report_only`|`full_paper`), `get_track()`/`set_track()`, Stage 5 stages in STAGE_ORDER
- **`resources/medical-paper/agents/paper_config_agent.md`**: `# [MSRA-BRIDGE]` MSRA Handoff Detection block + `clinical` Domain Evidence Profile activation
- **`install.ps1`**: [6/6] MSRA shared dependency verification step (non-blocking WARNING)
- **`skills/pipeline/SKILL.md`**: Stage 4 checkpoint (M4'), Stage 5 Paper Track dispatch, intent detection update
- **`skills/report/SKILL.md`**: Stage 4 checkpoint section (M4'), slimmed to 7-step statistical-only flow

### Changed
- **Stage 4 slimmed**: Phase 2 (reporting-guideline selection) and Phase 2.5 (journal template) moved to Paper Track Stage 5.0
- **Phase 6 slimmed**: full reporting-guideline compliance 9statistical quality check only (statcheck + anti-patterns + statistical dimensions)
- **Manifest**: v0.7.6 9v0.8.0, `/msra` description updated, `/msra-paper` added
- **Passport schema**: `track` field added, `stage_5_0_intake` + `stage_5_paper` stages added (9 total)
- **`test_passport.py`**: updated STAGE_ORDER count 79, added `TestPaperTrack` class (6 tests)

### Architecture
- MSRA stays a **pure orchestrator** (IRON RULE) 9Paper Track delegates to `medical-pipeline` skill
- Six fusion points: Passport unified / Quality Gate reuse / Literature seed / Methods reuse / Journal template pass / Tables+Figures reuse
- Data-driven positioning: this plugin is for data-processing projects only; pure writing uses MSRA directly

## [0.7.6-R7] - 2026-06-15

Research-fusion round 7: PRISMA 2020 + STARD 2015 reporting standards.
Fills checklist gaps where the project referenced these standards but
had no structured checklist files.

### Reporting guidelines (2 new)
- **`shared/reporting-guidelines/PRISMA_2020_checklist.md` NEW** 9  PRISMA 2020 systematic review reporting (Page 2021, BMJ). 27 items.
  Previously the project had PRISMA-NMA but no main PRISMA checklist.
  Includes PRISMA 2020 flow chart template, GRADE integration,
  and bias assessment tool cross-references.
- **`shared/reporting-guidelines/STARD_checklist.md` NEW** 9STARD 2015
  diagnostic accuracy reporting (Bossuyt 2015, BMJ). 30 items.
  Previously referenced but had no checklist file. Includes 2×2
  contingency table template, calculation formulas, and QUADAS-2
  cross-reference.

### Skills integration
- **`report` SKILL.md** 9Phase 2/6 updated with PRISMA 2020 (27 items)
  and STARD 2015 (30 items) compliance check rows.

## [0.7.6-R6] - 2026-06-15

Research-fusion round 6: risk-of-bias assessment tools + CHEERS 2022
health economic reporting standard. Targets structural gaps identified
via GitHub + literature search (not marginal polish). Branch
`auto-optimize/research-fusion`.

### Risk-of-bias assessment framework (5 new files)
- **`shared/risk-of-bias/RoB_2_checklist.md` NEW** 9Cochrane RoB 2
  risk-of-bias tool for RCTs (Sterne 2019, BMJ). 5 domains with
  signaling questions 9Low/Some/High judgments. Complements CONSORT
  2025 (reporting) with bias assessment (quality).
- **`shared/risk-of-bias/ROBINS_I_V2_checklist.md` NEW** 9ROBINS-I V2
  for non-randomized studies of interventions (Sterne 2016, BMJ;
  Cochrane 2024 update). 7 domains 95-level judgment. Includes
  target trial emulation framework. Complements STROBE.
- **`shared/risk-of-bias/PROBAST_checklist.md` NEW** 9PROBAST+AI
  (Wolff 2019 + Collins 2025 BMJ) for prediction model bias. 4 domains,
  20 signaling questions. AI-specific extensions for ML/fairness.
  Complements TRIPOD-AI/LLM.
- **`shared/risk-of-bias/QUADAS_2_checklist.md` NEW** 9QUADAS-2
  (Whiting 2011) for diagnostic accuracy studies. 4 domains 9RoB +
  applicability. Complements STARD.
- **`shared/risk-of-bias/GRADE_framework.md` NEW** 9GRADE certainty
  of evidence framework (Guyatt 2008). 5 downgrade + 3 upgrade factors
  9⊕⊕⊕⊕~⊕○○○. Includes Summary of Findings (SoF) table template.

### Reporting guidelines (1 new)
- **`shared/reporting-guidelines/CHEERS_checklist.md` NEW** 9CHEERS
  2022 health economic evaluation reporting (Husereau 2022, Value
  Health). 28 items. Complements ch40 cost-effectiveness analysis
  (methods) with reporting standards. 🆕 2022 new items marked.

### Skills integration
- **`report` SKILL.md** 9Phase 2/6 updated with risk-of-bias tool
  selection table + CHEERS compliance check row + mandatory bias
  assessment for systematic reviews.
- **`analysis-plan` SKILL.md** 9Phase 4/5 updated with bias assessment
  plan review references.

### Documentation updates
- `shared/statistics-methods/INDEX.md` 9new "Shared knowledge base
  extensions" section with risk-of-bias + CHEERS references.
- `README.md` 9updated project structure (risk-of-bias directory),
  reporting guidelines count (1394), new "Risk-of-bias tools" section
  with 5-tool comparison table.

> **Gap analysis**: GitHub + literature search confirmed zero coverage
> for RoB 2, ROBINS-I, PROBAST, QUADAS-2, GRADE, and CHEERS 2022 9> all structural gaps, not marginal polish. These tools are essential
> for systematic reviews and evidence synthesis workflows.

## [0.7.5] - 2026-06-14

Research-fusion optimization loop: 5 rounds of targeted literature/GitHub
research 9integration 9Darwin re-evaluation 9push. Each round sourced
from peer-reviewed 2024-2026 statements and verified against the existing
project for true structural gaps (not marginal polish). Branch
`auto-optimize/research-fusion`.

### Reporting guidelines (3 new + 1 rewrite)
- **`CONSORT_checklist.md` REWRITE** 9restructured from self-authored
  22-item layout to the official CONSORT 2025 **30-item** structure
  (Hopewell 2025, PMC11996237). Adds the 7 substantively new items:
  Item 4 (stopping rules), Item 8 (PPI 9patient and public involvement),
  Item 12b (intervention delivery, TIDieR-integrated), Item 13b
  (non-pharmacological blinding), Item 21b (harms collection method),
  Item 22 (delivery fidelity), Item 24 (clinical vs statistical
  significance), Item 26 (protocol access), Item 27 (IPD sharing),
  Item 30 (AI use disclosure).
- **`SPIRIT_checklist.md` NEW** 9SPIRIT 2025 **34-item** trial-protocol
  checklist (Knowles 2025, PMC12035670). Previously the project had zero
  SPIRIT references (findstr-confirmed). Covers Title/Registration/
  Funding/Governance/Background/Objectives through Ethics/Dissemination/
  Consent, with ICH E9(R1) Estimands framework integration and FDA
  Diversity Action Plan 2024 linkage.
- **`statcheck_rules.md` NEW** 9NHST reporting-consistency auto-check
  rules (borrows statcheck methodology, Epskamp & Nuijten 2016,
  PMC7540394). APA-format regex patterns, scipy recompute formulas,
  4-tier tolerance table, 4-class false-positive mitigation (one-tailed,
  adjusted-p, rounding, robust SE). No new R/Python dependencies.
- **`TRIPOD_LLM_checklist.md` NEW** 9TRIPOD-LLM **19 main + 50
  subitems** (Collins 2024, PMC12104976). The LLM-specific extension of
  TRIPOD+AI. Previously the project had TRIPOD+AI but no LLM-specific
  checklist. Covers LLM-specific gaps: foundation-model version, prompt
  engineering, context window, multi-run variance, hallucination control,
  bias amplification, training-data memorization.

### Causal inference
- **`causal_inference_workflow.md §3.3.5` NEW** 9Negative Control
  Outcomes (NCO) falsification test. Full section: core logic
  (confounding bridge function), 3-criteria NCO selection, double-NCO
  design (NCO+NCE cross-validation), Python implementation
  (`negative_control_test` + `coca_correction`, statsmodels only),
  5-step decision tree, 5 NCO anti-patterns. Sources: Shi 2025
  (Taylor & Francis), DANCE JMLR 2024, COCA AJE 2014.
- **`ch28-e-value.md` extension** 9new "MSRA extension" section at
  chapter end (clearly marked non-translation addition) clarifying the
  E-value/NCO complementary relationship: E-value answers "how strong
  would confounding need to be" (sensitivity), NCO answers "is
  confounding actually present" (falsification). Both should be reported.
- **`ch18-multiple-comparisons-methods.md §5` NEW** 9Bretz graphical
  approach (Bretz 2009, Stat Med). Core idea (directed weighted graph
  for alpha-allocation), ASCII diagram, gMCPLite R implementation,
  relationship to ch19 gatekeeping (gatekeeping is a special case).

### Skill updates
- **report SKILL.md Phase 6** 9reworked: per-guideline checklist
  references (CONSORT 30 / STROBE / TRIPOD-AI / TRIPOD-LLM / PRISMA-NMA /
  CARE / ARRIVE / REMARK) replacing a self-authored 9-item summary;
  new Step 6b statcheck consistency check as MANDATORY-M4 sub-gate;
  explicit LLM-vs-ML guideline decision rule.
- **analysis-plan SKILL.md** 9SPIRIT 2025 reference + protocol-
  completeness self-check (Items 9/10/11/12/14/22); NCO references at
  sensitivity-analysis row / ch28 / parameter table / anti-pattern #17;
  Bretz graphical method in §5 + method overview.
- **calibration SKILL.md mode 7** NEW 9External Benchmark Evaluation.
  Three external gold-standard sources (A. published, B. benchmark
  datasets StatLLM/MIMIC/Framingham/NHANES, C. expert review) with
  priority C>A>B>synthetic. StatLLM-style 4-task layered eval (T1 EDA /
  T2 modeling / T3 inference / T4 interpretation). MedHELM-style 6-
  dimension holistic eval (safety is a hard gate). RWE-LLM-style
  adversarial test set (5 dangerous scenarios). Synthetic gold standard
  demoted to reference use.

### Darwin re-evaluation (.darwin-results/results.tsv)
- report 89.5 -> 92.3 (+2.8 across R1+R3)
- analysis-plan 89.5 -> 91.7 (+2.2 across R1+R4+R5)
- calibration 86.1 -> 89.0 (+2.9 in R2, fixing the weakest dim8=6)
- Estimated 6-skill average: 89.8 -> ~91.3

### Sources
CONSORT 2025 (PMC11996237), SPIRIT 2025 (PMC12035670), TRIPOD-LLM
(PMC12104976), statcheck (PMC7540394), StatLLM (Nature SciData 2026),
MedHELM (Stanford HAI 2025), RWE-LLM (medRxiv 2025.03.17.25324157),
NCO (Shi 2025, DANCE JMLR 2024), Bretz graphical (Stat Med 2009), FDA
Diversity Action Plans (June 2024), E-value (VanderWeele 2017).

## [0.7.4] - 2026-06-14

### Fixed
- **Quality-gate item-count inconsistency**: Stage 1.5 (data) and Stage 3.5 (results)
  gates actually contain 9 checklist items each, but were documented as "8 9 in the
  Pipeline §1 flow diagram, §3 stage headers, §4.1 M-table, the QC Inspector dispatch
  table, and `data-prep/SKILL.md` §7. All occurrences now read **9 9* (Stage 2.5
  remains 8 9.
- **MANDATORY Checkpoint numbering drift**: §3 stage headers labelled the gates
  M2/M3/M4 while §4.1 defines them as M1/M2/M3 (M1=Stage 1.5, M2=Stage 2.5,
  M3=Stage 3.5, M4=Stage 4 compliance). All in-stage labels corrected to M1/M2/M3.
- **report/SKILL.md** referenced a non-existent `MANDATORY-M5` for the compliance
  checkpoint; corrected to **MANDATORY-M4**.
- **§7.3 convergence section** referenced a non-existent "M6 Checkpoint". The
  convergence/acceptance decision point is now formally defined as **MANDATORY-M5**
  in the §4.1 table, and §7.3 references it consistently.
- **Version drift**: `manifest.json` (0.7.1) and all `SKILL.md` frontmatter
  (0.6.0 / 0.7.1) lagged behind the released 0.7.3. All bumped to **0.7.4**.

### Changed
- `data-prep/SKILL.md` §7 product table: added row #9 mapping the Phase 1 PHI/隐私
  compliance report to gate item 9.

### Added
- `scripts/lint_gate_counts.py`: CI lint that asserts, for each blocking gate
  (Stage 1.5 / 2.5 / 3.5), the actual checklist length, the stage header "N 9 claim,
  and the §4.1 M-table row claim all agree. Wired into `.github/workflows/ci.yml`
  so a future edit that adds/removes a checklist item without updating the prose
  fails CI.
- README project-structure tree: `statistics-methods/` chapter count corrected
  from 41 to **48** (chapters ch42–ch48 added in 0.7.09.7.3).

## [0.7.2] - 2026-06-14

### Changed
- Pipeline SKILL.md: 精简9789990 9(-12.5%)，压缩示9角色切换/进度追踪
- analysis-plan SKILL.md: 消除"建议"软化措辞，改为强制性指9
### Added
- `shared/reporting-guidelines/PRISMA_NMA_checklist.md` 9网络Meta分析报告规范 (25项检查
- Anti-patterns catalog: 新增 G(网络Meta)/H(孟德尔随机化)/T(目标试验)/J(GEE) 四类99 条反模式
- CI: 新增 Python 模板语法检查步9
## [0.7.1] - 2026-06-13

### Added
- **New templates**:
  - `shared/templates/mendelian_randomization_template.R` 9MR analysis (IVW, MR-Egger, weighted median, mode, MR-PRESSO, leave-one-out, scatter/forest plots)
  - `shared/templates/network_meta_template.R` 9Network meta-analysis (frequentist/Bayesian, SUCRA ranking, league table, network plot, inconsistency test)
  - `shared/templates/adaptive_design_template.R` 9Bayesian adaptive design (group sequential, sample size re-estimation, enrichment, interim analysis, simulation)
  - `shared/templates/cdisc_integration_template.R` 9CDISC data integration (SDTM/ADaM detection, XPT export, ADaM validation)
- **Knowledge base chapters**:
  - `ch45-mendelian-randomization.md` 9Three assumptions, instrument selection, methods, sensitivity, reporting
  - `ch46-network-meta-analysis.md` 9Indirect comparison, consistency, SUCRA, league table, PRISMA-NMA
- **analysis-plan SKILL.md**: TTE added to observational study advanced methods table
- **End-to-end evaluation framework** (`evals/gold/end-to-end/`):
  - 4 evaluation dimensions: code executability, numeric accuracy, compliance, robustness
  - 5 test cases with standard answers (E001-E005)
  - Compliance templates for CONSORT 2025 and STROBE
  - Robustness tests: missing injection, noise, case mixing, date format chaos
- **Version bump**: manifest.json updated to 0.7.1

## [0.7.0] - 2026-06-13

### Fixed
- `shared/templates/prediction_model_template.py` line 58: syntax error (`outcome prevalence` 9`outcome_prevalence`)
- `shared/templates/bland_altman_template.R` line 79: replaced `...` placeholder with proper comment
- `CHANGELOG.md`: corrected date from 2025-06-13 to 2026-06-13
- `README.md`: corrected skill count (59), command count (59), quality gate item counts (79/9), added `/msra-calibrate` command, added calibration skill to project structure, expanded supported methods and reporting guidelines lists

### Added
- **New templates**:
  - `shared/templates/gee_template.R` 9GEE (Generalized Estimating Equations) for longitudinal data (geepack)
  - `shared/templates/gee_template.py` 9GEE for longitudinal data (statsmodels)
  - `shared/templates/nonparametric_template.R` 9Mann-Whitney U, Kruskal-Wallis, Wilcoxon signed-rank, Friedman, non-parametric Table 1
  - `shared/templates/competing_risks_template.R` 9Cumulative incidence, cause-specific hazards, Fine-Gray subdistribution model (tidycmprsk)
  - `shared/templates/ps_diagnostics_template.R` 9Love plot, weight distribution, PS overlap, balance table (MatchIt/cobalt)
  - `shared/templates/repeated_measures_anova_template.R` 9Sphericity check, post-hoc, effect sizes (rstatix/emmeans)
- **Knowledge base chapters**:
  - `ch42-nonparametric-tests.md` 9Mann-Whitney, Kruskal-Wallis, Wilcoxon, Friedman, decision tree, effect sizes, anti-patterns
  - `ch43-gee-longitudinal-analysis.md` 9GEE theory, working correlation selection (QIC), sandwich estimator, marginal vs conditional effects
- **Evaluation framework**:
  - `evals/gold/method-selection/` 910 method-selection gold standard tuples (M001-M010) covering RCT ANCOVA, survival Cox, observational IPTW, diagnostic ROC, non-inferiority, negative binomial, multiplicity, Firth logistic, competing risks
- **Enhanced causal inference workflow**:
  - Added Section 6: complete DAG 9identification 9estimation 9sensitivity pipeline
  - Added identification strategy selection table
  - Added doubly robust estimation (AIPW) examples
  - Added PS diagnostics template reference
- **Data Prep test-prompts**: expanded from 10 to 15 test cases (added: mixed missing patterns, multi-format import, outlier strategy, time series validation, encoding conversion)
- **CI enhancement**: added Python template syntax check step for all 8 Python templates

## [0.6.0] - 2026-06-13

### Added
- **Calibration Skill** (`skills/calibration/`): Metric calibration framework with gold standard comparison
  - Confusion matrix metrics (TPR, TNR, FPR, FNR) for method selection and conclusion accuracy
  - Numerical deviation metrics (MAE, RMSE, MAPE, PCC) for estimation accuracy
  - Three modes: full calibration run, status check, incremental update
  - `/msra-calibrate` command registered in manifest.json
- **Passport artifact tracking** in Pipeline SKILL.md
  - Material Passport lifecycle: `planned` 9`in_progress` 9`completed` 9`verified` 9`consumed`
  - Mid-entry prerequisite checks via passport.json
- **Calibration-gate linkage** in Stage 3.5 Results Quality Gate
  - New check item #9: calibration confidence based on historical TPR/FPR
  - Dynamic thresholds: TPR90%/FPR90% 9high confidence; TPR<80%/FPR>15% 9mandatory review
- **Error diagnostics integration** in analysis-exec SKILL.md
  - References to `shared/error-diagnostics/error_patterns.md` and `auto_fix_suggestions`
  - Integrated into self-healing code execution loop (rounds 1-2)
- **Gold standard dataset** expanded from 20 to 100 records, covering 25 statistical methods
  - Methods: Logistic/Cox/Linear regression, t-test, Chi-square, Mann-Whitney U, ANCOVA, Repeated Measures ANOVA, Mixed Effects, Kaplan-Meier, Log-rank, Competing Risks, PSM, IPTW, ROC/DeLong, Meta Analysis, E-value, Mediation, DID, Fisher Exact, McNemar, Conditional Logistic, Poisson, Negative Binomial, RCS, DCA, Bland-Altman, Kruskal-Wallis
- **Test coverage expansion**: All skill test-prompts.json expanded to 10+ test cases each
  - pipeline: quality gate failure, RCT/observational workflows, artifact checks, calibration status, stage jumping, interruption recovery
  - data-prep: TCM term normalization, missing pattern assessment, blinded review, EDA, data dictionary validation, database locking
  - analysis-plan: SAP quality gate, RCT sample size, confounding control, multiple comparison, variable construction, non-inferiority trial
  - analysis-exec: assumption testing, deviation recording, sensitivity analysis, [SKIP] handling, Generator-Evaluator differences, reproducibility
  - report: compliance failure, journal template switching, results interpretation, DOCX export, TRIPOD-AI
  - calibration: standard run, status check, incremental update, format validation, low-confidence handling
- **CI enhancements**:
  - R template syntax checking via `Rscript parse()`
  - Gold standard CSV validation (min 50 records, 10+ methods)
  - Calibration skill added to SKILL frontmatter validation
- **Install script** (`install.ps1`): Automated setup for Python/R dependencies, output directories, passport.json, calibration_db.json

### Changed
- Pipeline SKILL.md: `depends_on` now includes `calibration`; `works_with` includes `shared/passport/passport_schema.md`
- Stage 3.5 quality gate expanded from 7 to 9 check items (added calibration linkage + [SKIP] marking)
