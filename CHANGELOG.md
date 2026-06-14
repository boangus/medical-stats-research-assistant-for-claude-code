# Changelog

All notable changes to MSRA (Medical Statistics Research Assistant) will be documented in this file.

## [0.7.5] - 2026-06-14

Research-fusion optimization loop: 5 rounds of targeted literature/GitHub
research → integration → Darwin re-evaluation → push. Each round sourced
from peer-reviewed 2024-2026 statements and verified against the existing
project for true structural gaps (not marginal polish). Branch
`auto-optimize/research-fusion`.

### Reporting guidelines (3 new + 1 rewrite)
- **`CONSORT_checklist.md` REWRITE** — restructured from self-authored
  22-item layout to the official CONSORT 2025 **30-item** structure
  (Hopewell 2025, PMC11996237). Adds the 7 substantively new items:
  Item 4 (stopping rules), Item 8 (PPI — patient and public involvement),
  Item 12b (intervention delivery, TIDieR-integrated), Item 13b
  (non-pharmacological blinding), Item 21b (harms collection method),
  Item 22 (delivery fidelity), Item 24 (clinical vs statistical
  significance), Item 26 (protocol access), Item 27 (IPD sharing),
  Item 30 (AI use disclosure).
- **`SPIRIT_checklist.md` NEW** — SPIRIT 2025 **34-item** trial-protocol
  checklist (Knowles 2025, PMC12035670). Previously the project had zero
  SPIRIT references (findstr-confirmed). Covers Title/Registration/
  Funding/Governance/Background/Objectives through Ethics/Dissemination/
  Consent, with ICH E9(R1) Estimands framework integration and FDA
  Diversity Action Plan 2024 linkage.
- **`statcheck_rules.md` NEW** — NHST reporting-consistency auto-check
  rules (borrows statcheck methodology, Epskamp & Nuijten 2016,
  PMC7540394). APA-format regex patterns, scipy recompute formulas,
  4-tier tolerance table, 4-class false-positive mitigation (one-tailed,
  adjusted-p, rounding, robust SE). No new R/Python dependencies.
- **`TRIPOD_LLM_checklist.md` NEW** — TRIPOD-LLM **19 main + 50
  subitems** (Collins 2024, PMC12104976). The LLM-specific extension of
  TRIPOD+AI. Previously the project had TRIPOD+AI but no LLM-specific
  checklist. Covers LLM-specific gaps: foundation-model version, prompt
  engineering, context window, multi-run variance, hallucination control,
  bias amplification, training-data memorization.

### Causal inference
- **`causal_inference_workflow.md §3.3.5` NEW** — Negative Control
  Outcomes (NCO) falsification test. Full section: core logic
  (confounding bridge function), 3-criteria NCO selection, double-NCO
  design (NCO+NCE cross-validation), Python implementation
  (`negative_control_test` + `coca_correction`, statsmodels only),
  5-step decision tree, 5 NCO anti-patterns. Sources: Shi 2025
  (Taylor & Francis), DANCE JMLR 2024, COCA AJE 2014.
- **`ch28-e-value.md` extension** — new "MSRA extension" section at
  chapter end (clearly marked non-translation addition) clarifying the
  E-value/NCO complementary relationship: E-value answers "how strong
  would confounding need to be" (sensitivity), NCO answers "is
  confounding actually present" (falsification). Both should be reported.
- **`ch18-multiple-comparisons-methods.md §5` NEW** — Bretz graphical
  approach (Bretz 2009, Stat Med). Core idea (directed weighted graph
  for alpha-allocation), ASCII diagram, gMCPLite R implementation,
  relationship to ch19 gatekeeping (gatekeeping is a special case).

### Skill updates
- **report SKILL.md Phase 6** — reworked: per-guideline checklist
  references (CONSORT 30 / STROBE / TRIPOD-AI / TRIPOD-LLM / PRISMA-NMA /
  CARE / ARRIVE / REMARK) replacing a self-authored 9-item summary;
  new Step 6b statcheck consistency check as MANDATORY-M4 sub-gate;
  explicit LLM-vs-ML guideline decision rule.
- **analysis-plan SKILL.md** — SPIRIT 2025 reference + protocol-
  completeness self-check (Items 9/10/11/12/14/22); NCO references at
  sensitivity-analysis row / ch28 / parameter table / anti-pattern #17;
  Bretz graphical method in §5 + method overview.
- **calibration SKILL.md mode 7** NEW — External Benchmark Evaluation.
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
  gates actually contain 9 checklist items each, but were documented as "8 项" in the
  Pipeline §1 flow diagram, §3 stage headers, §4.1 M-table, the QC Inspector dispatch
  table, and `data-prep/SKILL.md` §7. All occurrences now read **9 项** (Stage 2.5
  remains 8 项).
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
  compliance report to gate item □9.

### Added
- `scripts/lint_gate_counts.py`: CI lint that asserts, for each blocking gate
  (Stage 1.5 / 2.5 / 3.5), the actual checklist length, the stage header "N 项" claim,
  and the §4.1 M-table row claim all agree. Wired into `.github/workflows/ci.yml`
  so a future edit that adds/removes a checklist item without updating the prose
  fails CI.
- README project-structure tree: `statistics-methods/` chapter count corrected
  from 41 to **48** (chapters ch42–ch48 added in 0.7.0–0.7.3).

## [0.6.0] - 2026-06-13

### Added
- **Calibration Skill** (`skills/calibration/`): Metric calibration framework with gold standard comparison
  - Confusion matrix metrics (TPR, TNR, FPR, FNR) for method selection and conclusion accuracy
  - Numerical deviation metrics (MAE, RMSE, MAPE, PCC) for estimation accuracy
  - Three modes: full calibration run, status check, incremental update
  - `/msra-calibrate` command registered in manifest.json
- **Passport artifact tracking** in Pipeline SKILL.md
  - Material Passport lifecycle: `planned` → `in_progress` → `completed` → `verified` → `consumed`
  - Mid-entry prerequisite checks via passport.json
- **Calibration-gate linkage** in Stage 3.5 Results Quality Gate
  - New check item #9: calibration confidence based on historical TPR/FPR
  - Dynamic thresholds: TPR≥90%/FPR≤10% → high confidence; TPR<80%/FPR>15% → mandatory review
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

## [0.7.1] - 2026-06-13

### Added
- **New templates**:
  - `shared/templates/mendelian_randomization_template.R` — MR analysis (IVW, MR-Egger, weighted median, mode, MR-PRESSO, leave-one-out, scatter/forest plots)
  - `shared/templates/network_meta_template.R` — Network meta-analysis (frequentist/Bayesian, SUCRA ranking, league table, network plot, inconsistency test)
  - `shared/templates/adaptive_design_template.R` — Bayesian adaptive design (group sequential, sample size re-estimation, enrichment, interim analysis, simulation)
  - `shared/templates/cdisc_integration_template.R` — CDISC data integration (SDTM/ADaM detection, XPT export, ADaM validation)
- **Knowledge base chapters**:
  - `ch45-mendelian-randomization.md` — Three assumptions, instrument selection, methods, sensitivity, reporting
  - `ch46-network-meta-analysis.md` — Indirect comparison, consistency, SUCRA, league table, PRISMA-NMA
- **analysis-plan SKILL.md**: TTE added to observational study advanced methods table
- **End-to-end evaluation framework** (`evals/gold/end-to-end/`):
  - 4 evaluation dimensions: code executability, numeric accuracy, compliance, robustness
  - 5 test cases with standard answers (E001-E005)
  - Compliance templates for CONSORT 2025 and STROBE
  - Robustness tests: missing injection, noise, case mixing, date format chaos
- **Version bump**: manifest.json updated to 0.7.1

## [0.7.2] - 2026-06-14

### Changed
- Pipeline SKILL.md: 精简从 789→690 行 (-12.5%)，压缩示例/角色切换/进度追踪
- analysis-plan SKILL.md: 消除"建议"软化措辞，改为强制性指令

### Added
- `shared/reporting-guidelines/PRISMA_NMA_checklist.md` — 网络Meta分析报告规范 (25项检查)
- Anti-patterns catalog: 新增 G(网络Meta)/H(孟德尔随机化)/T(目标试验)/J(GEE) 四类共 9 条反模式
- CI: 新增 Python 模板语法检查步骤

## [0.7.0] - 2026-06-13

### Fixed
- `shared/templates/prediction_model_template.py` line 58: syntax error (`outcome prevalence` → `outcome_prevalence`)
- `shared/templates/bland_altman_template.R` line 79: replaced `...` placeholder with proper comment
- `CHANGELOG.md`: corrected date from 2025-06-13 to 2026-06-13
- `README.md`: corrected skill count (5→6), command count (5→6), quality gate item counts (7→8/9), added `/msra-calibrate` command, added calibration skill to project structure, expanded supported methods and reporting guidelines lists

### Added
- **New templates**:
  - `shared/templates/gee_template.R` — GEE (Generalized Estimating Equations) for longitudinal data (geepack)
  - `shared/templates/gee_template.py` — GEE for longitudinal data (statsmodels)
  - `shared/templates/nonparametric_template.R` — Mann-Whitney U, Kruskal-Wallis, Wilcoxon signed-rank, Friedman, non-parametric Table 1
  - `shared/templates/competing_risks_template.R` — Cumulative incidence, cause-specific hazards, Fine-Gray subdistribution model (tidycmprsk)
  - `shared/templates/ps_diagnostics_template.R` — Love plot, weight distribution, PS overlap, balance table (MatchIt/cobalt)
  - `shared/templates/repeated_measures_anova_template.R` — Sphericity check, post-hoc, effect sizes (rstatix/emmeans)
- **Knowledge base chapters**:
  - `ch42-nonparametric-tests.md` — Mann-Whitney, Kruskal-Wallis, Wilcoxon, Friedman, decision tree, effect sizes, anti-patterns
  - `ch43-gee-longitudinal-analysis.md` — GEE theory, working correlation selection (QIC), sandwich estimator, marginal vs conditional effects
- **Evaluation framework**:
  - `evals/gold/method-selection/` — 10 method-selection gold standard tuples (M001-M010) covering RCT ANCOVA, survival Cox, observational IPTW, diagnostic ROC, non-inferiority, negative binomial, multiplicity, Firth logistic, competing risks
- **Enhanced causal inference workflow**:
  - Added Section 6: complete DAG → identification → estimation → sensitivity pipeline
  - Added identification strategy selection table
  - Added doubly robust estimation (AIPW) examples
  - Added PS diagnostics template reference
- **Data Prep test-prompts**: expanded from 10 to 15 test cases (added: mixed missing patterns, multi-format import, outlier strategy, time series validation, encoding conversion)
- **CI enhancement**: added Python template syntax check step for all 8 Python templates
