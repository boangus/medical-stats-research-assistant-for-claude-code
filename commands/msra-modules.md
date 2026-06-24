---
description: MSRA Modules — manage experimental modules (medical imaging, bioinformatics, realtime analytics, cross-domain)
argument-hint: "list|info <module>|check <module>"
---

Manage experimental modules in MSRA. These modules provide additional capabilities beyond the core pipeline.

## Available Modules

| Module | Description | Status |
|--------|-------------|--------|
| medical_imaging | Medical image processing (DICOM, segmentation, classification) | experimental |
| bioinformatics | Bioinformatics analysis (scRNA-seq, differential expression) | experimental |
| realtime_analytics | Real-time data processing (stream analysis, anomaly detection) | experimental |
| cross_domain | Cross-domain integration (radiomics-DEG correlation, realtime prediction, multi-modal visualization) | experimental |

## Usage

```
/msra-modules list                 # List all modules
/msra-modules info medical_imaging # View module details
/msra-modules check bioinformatics # Check dependencies
/msra-modules info cross_domain    # View cross-domain module details
/msra-modules check cross_domain   # Check cross-domain dependencies
```

## Dispatch

Parse the command from `$ARGUMENTS`. If no arguments, list all modules.

For `list`: Call `msra_modules.list_modules()` and display the results.

For `info <module>`: Call `msra_modules.check_module_dependencies(module)` and display detailed information.

For `check <module>`: Call `msra_modules.check_module_dependencies(module)` and return exit code based on dependency status.

## Module Details

### cross_domain

Cross-domain multi-modal fusion analysis module. Integrates outputs from medical_imaging, bioinformatics, and realtime_analytics modules.

**Entry command**: `/msra-cross`

**Scenarios**:
- `correlation`: Radiomics-DEG correlation analysis
- `prediction`: Realtime prediction model training
- `visualization`: Multi-modal linked visualization
- `full`: Complete fusion workflow (all scenarios)

**Quality Gates**:
- Gate CD-1.5: Data alignment gate (3 items, 2 key)
- Gate CD-3.5: Fusion results gate (3 items, 2 key)

**Output Schema**: `msra/cross_domain_result/v1`

**Dependencies**: scipy, scikit-learn, matplotlib (core dependencies, no extra installs needed)

## Note

Experimental modules require additional dependencies. Install with:
```bash
pip install "medical-stats-research-assistant[imaging]"
pip install "medical-stats-research-assistant[bioinformatics]"
pip install "medical-stats-research-assistant[realtime]"
pip install "medical-stats-research-assistant[cross_domain]"
```

For full installation:
```bash
pip install "medical-stats-research-assistant[experimental]"
```
