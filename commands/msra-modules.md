---
description: MSRA Modules — manage experimental modules (medical imaging, bioinformatics, realtime analytics)
argument-hint: "list|info <module>|check <module>"
---

Manage experimental modules in MSRA. These modules provide additional capabilities beyond the core pipeline.

## Available Modules

| Module | Description | Status |
|--------|-------------|--------|
| medical_imaging | Medical image processing (DICOM, segmentation, classification) | experimental |
| bioinformatics | Bioinformatics analysis (scRNA-seq, differential expression) | experimental |
| realtime_analytics | Real-time data processing (stream analysis, anomaly detection) | experimental |
| cross_domain | Cross-domain integration (radiomics-DEG correlation) | experimental |

## Usage

```
/msra-modules list                 # List all modules
/msra-modules info medical_imaging # View module details
/msra-modules check bioinformatics # Check dependencies
```

## Dispatch

Parse the command from `$ARGUMENTS`. If no arguments, list all modules.

For `list`: Call `msra_modules.list_modules()` and display the results.

For `info <module>`: Call `msra_modules.check_module_dependencies(module)` and display detailed information.

For `check <module>`: Call `msra_modules.check_module_dependencies(module)` and return exit code based on dependency status.

## Note

Experimental modules require additional dependencies. Install with:
```bash
pip install "medical-stats-research-assistant[imaging]"
pip install "medical-stats-research-assistant[bioinformatics]"
pip install "medical-stats-research-assistant[realtime]"
```
