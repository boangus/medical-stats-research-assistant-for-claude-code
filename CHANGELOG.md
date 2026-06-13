# Changelog

All notable changes to MSRA (Medical Statistics Research Assistant) will be documented in this file.

## [0.6.0] - 2025-06-13

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
