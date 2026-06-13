# Changelog

All notable changes to MSRA (Medical Statistics Research Assistant) will be documented in this file.

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
