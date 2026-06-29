#!/bin/bash
# MSRA (Medical Statistics Research Assistant) - Install Script for Mac/Linux
# Usage: ./install.sh [--skip-r] [--skip-python] [--dev]

set -e

PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SKIP_R=false
SKIP_PYTHON=false
DEV=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --skip-r) SKIP_R=true ;;
        --skip-python) SKIP_PYTHON=true ;;
        --dev) DEV=true ;;
    esac
done

echo -e "\033[1;36m=== MSRA Installer ===\033[0m"
echo "Project root: $PROJECT_ROOT"
echo ""

# 1. Check Python
if [ "$SKIP_PYTHON" = false ]; then
    echo -e "\033[1;33m[1/9] Checking Python...\033[0m"
    if command -v python3 &> /dev/null; then
        PY_VERSION=$(python3 --version)
        echo -e "\033[0;32m  Found: $PY_VERSION\033[0m"
        PY_CMD="python3"
    elif command -v python &> /dev/null; then
        PY_VERSION=$(python --version)
        echo -e "\033[0;32m  Found: $PY_VERSION\033[0m"
        PY_CMD="python"
    else
        echo -e "\033[0;31m  ERROR: Python not found. Install Python 3.9+ and retry.\033[0m"
        exit 1
    fi

    REQ_FILE="$PROJECT_ROOT/requirements.txt"
    if [ -f "$REQ_FILE" ]; then
        echo -e "\033[1;33m  Installing Python dependencies...\033[0m"
        "$PY_CMD" -m pip install -r "$REQ_FILE" --quiet
        echo -e "\033[0;32m  Done.\033[0m"
    else
        echo -e "\033[0;90m  No requirements.txt found, skipping pip install.\033[0m"
    fi
else
    echo -e "\033[0;90m[1/9] Skipping Python check (--skip-python)\033[0m"
fi

# 2. Check R
if [ "$SKIP_R" = false ]; then
    echo -e "\n\033[1;33m[2/9] Checking R...\033[0m"
    if command -v Rscript &> /dev/null; then
        R_VERSION=$(Rscript --version | head -n 1)
        echo -e "\033[0;32m  Found: $R_VERSION\033[0m"

        R_PACKAGES=("survival" "tableone" "forestplot" "ggplot2" "dplyr" "tidyr" "broom" "sandwich" "lmtest" "logistf")
        echo -e "\033[1;33m  Checking R packages...\033[0m"
        R_SCRIPT=""
        for pkg in "${R_PACKAGES[@]}"; do
            R_SCRIPT+="if (!require('$pkg', quietly=TRUE)) install.packages('$pkg', repos='https://cran.r-project.org/');"
        done
        R_SCRIPT+="cat('R packages installed\n')"
        TEMP_R=$(mktemp)
        echo "$R_SCRIPT" > "$TEMP_R"
        Rscript "$TEMP_R"
        rm -f "$TEMP_R"
    else
        echo -e "\033[1;33m  WARNING: R not found. R-based analysis will not work.\033[0m"
        echo -e "\033[1;33m  Install R 4.0+ from https://cran.r-project.org/\033[0m"
    fi
else
    echo -e "\n\033[0;90m[2/9] Skipping R check (--skip-r)\033[0m"
fi

# 3. Create output directories
echo -e "\n\033[1;33m[3/9] Creating output directories...\033[0m"
DIRS=(
    "MSRA/data"
    "MSRA/reports/figures"
    "MSRA/reports/tables"
    "MSRA/passport"
    "MSRA/calibration"
)
for dir in "${DIRS[@]}"; do
    FULL_PATH="$PROJECT_ROOT/$dir"
    if [ ! -d "$FULL_PATH" ]; then
        mkdir -p "$FULL_PATH"
        echo -e "\033[0;32m  Created: $dir\033[0m"
    else
        echo -e "\033[0;90m  Exists:  $dir\033[0m"
    fi
done

# 4. Create .claude/commands/ and .claude/skills/ symlinks for Claude Code discovery
echo -e "\n\033[1;33m[4/9] Setting up Claude Code discovery paths...\033[0m"

CLAUDE_DIR="$PROJECT_ROOT/.claude"
COMMANDS_LINK="$CLAUDE_DIR/commands"
SKILLS_LINK="$CLAUDE_DIR/skills"
COMMANDS_SOURCE="$PROJECT_ROOT/commands"
SKILLS_SOURCE="$PROJECT_ROOT/skills"

# Ensure .claude directory exists
mkdir -p "$CLAUDE_DIR"

# Create commands symlink
if [ ! -e "$COMMANDS_LINK" ]; then
    ln -s "$COMMANDS_SOURCE" "$COMMANDS_LINK"
    echo -e "\033[0;32m  Created symlink: .claude/commands/ -> commands/\033[0m"
else
    echo -e "\033[0;90m  Exists:  .claude/commands/\033[0m"
fi

# Create skills directory and symlink each skill subdirectory
mkdir -p "$SKILLS_LINK"
SKILL_NAMES=(
    "pipeline" "data-prep" "exploratory-causal" "analysis-plan" "analysis-exec"
    "report" "calibration" "peer-review" "systematic-survey"
)
for skill in "${SKILL_NAMES[@]}"; do
    SKILL_LINK_PATH="$SKILLS_LINK/$skill"
    SKILL_SOURCE_PATH="$SKILLS_SOURCE/$skill"
    if [ ! -e "$SKILL_LINK_PATH" ] && [ -d "$SKILL_SOURCE_PATH" ]; then
        ln -s "$SKILL_SOURCE_PATH" "$SKILL_LINK_PATH"
        echo -e "\033[0;32m  Created symlink: .claude/skills/$skill -> skills/$skill\033[0m"
    fi
done
echo -e "\033[0;32m  Claude Code discovery paths configured.\033[0m"

# 5. Initialize passport.json
echo -e "\n\033[1;33m[5/9] Initializing passport...\033[0m"
PASSPORT_PATH="$PROJECT_ROOT/MSRA/passport/passport.json"
if [ ! -f "$PASSPORT_PATH" ]; then
    PASSPORT="{
        \"passport_id\": \"msra-$(date +%Y%m%d)-001\",
        \"passport_schema_version\": \"1\",
        \"pipeline_version\": \"0.9.0\",
        \"created_at\": \"$(date +%Y-%m-%dT%H:%M:%S)\",
        \"updated_at\": \"$(date +%Y-%m-%dT%H:%M:%S)\",
        \"status\": \"in_progress\",
        \"study_type\": null,
        \"track\": null,
        \"current_stage\": \"stage_1\",
        \"artifacts\": [],
        \"checkpoints\": {
            \"last_completed\": null,
            \"last_verified\": null,
            \"resume_point\": \"stage_1\"
        },
        \"gates\": {}
    }"
    echo "$PASSPORT" > "$PASSPORT_PATH"
    echo -e "\033[0;32m  Created: passport.json\033[0m"
else
    echo -e "\033[0;90m  Exists:  passport.json\033[0m"
fi

# 6. Initialize calibration_db.json
echo -e "\n\033[1;33m[6/9] Initializing calibration database...\033[0m"
CALIB_PATH="$PROJECT_ROOT/MSRA/calibration/calibration_db.json"
if [ ! -f "$CALIB_PATH" ]; then
    echo "[]" > "$CALIB_PATH"
    echo -e "\033[0;32m  Created: calibration_db.json\033[0m"
else
    echo -e "\033[0;90m  Exists:  calibration_db.json\033[0m"
fi

# 7. Verify all skill directories and key files present
echo -e "\n\033[1;33m[7/9] Verifying project integrity...\033[0m"
SKILL_DIRS=(
    "skills/pipeline"
    "skills/data-prep"
    "skills/exploratory-causal"
    "skills/analysis-plan"
    "skills/analysis-exec"
    "skills/report"
    "skills/calibration"
    "skills/peer-review"
    "skills/systematic-survey"
)
KEY_FILES=(
    "resources/shared/handoff_schemas.md"
    "src/shared/passport/passport_schema.md"
    "src/shared/sap/sap_standard.md"
    ".claude/CLAUDE.md"
    "commands/msra.md"
    "commands/msra-full.md"
    "manifest.json"
)

MISSING_DIRS=()
for d in "${SKILL_DIRS[@]}"; do
    FULL_PATH="$PROJECT_ROOT/$d"
    if [ ! -d "$FULL_PATH" ]; then
        MISSING_DIRS+=("$d")
    fi
done
MISSING_FILES=()
for f in "${KEY_FILES[@]}"; do
    FULL_PATH="$PROJECT_ROOT/$f"
    if [ ! -f "$FULL_PATH" ]; then
        MISSING_FILES+=("$f")
    fi
done

if [ ${#MISSING_DIRS[@]} -gt 0 ] || [ ${#MISSING_FILES[@]} -gt 0 ]; then
    echo -e "\033[1;33m  WARNING: Project files missing:\033[0m"
    if [ ${#MISSING_DIRS[@]} -gt 0 ]; then
        echo -e "\033[1;33m  Missing skill directories:\033[0m"
        for m in "${MISSING_DIRS[@]}"; do
            echo -e "\033[1;33m    - $m\033[0m"
        done
    fi
    if [ ${#MISSING_FILES[@]} -gt 0 ]; then
        echo -e "\033[1;33m  Missing key files:\033[0m"
        for m in "${MISSING_FILES[@]}"; do
            echo -e "\033[1;33m    - $m\033[0m"
        done
    fi
    echo -e "\033[1;33m  This is a self-contained plugin. If files are missing, reinstall from source.\033[0m"
else
    echo -e "\033[0;32m  All 9 skills and key files present. Project is self-contained.\033[0m"
fi

# 8. Verify all SKILL.md files exist
echo -e "\n\033[1;33m[8/9] Verifying SKILL.md files...\033[0m"
MISSING_SKILL_MD=()
for d in "${SKILL_DIRS[@]}"; do
    SKILL_MD_PATH="$PROJECT_ROOT/$d/SKILL.md"
    if [ ! -f "$SKILL_MD_PATH" ]; then
        MISSING_SKILL_MD+=("$d/SKILL.md")
    fi
done
if [ ${#MISSING_SKILL_MD[@]} -gt 0 ]; then
    echo -e "\033[1;33m  WARNING: Missing SKILL.md files:\033[0m"
    for m in "${MISSING_SKILL_MD[@]}"; do
        echo -e "\033[1;33m    - $m\033[0m"
    done
else
    echo -e "\033[0;32m  All 9 SKILL.md files present.\033[0m"
fi

# 9. Dev mode: install dev dependencies
if [ "$DEV" = true ]; then
    echo -e "\n\033[1;35m[9/9] [DEV] Installing development dependencies...\033[0m"
    DEV_REQ_FILE="$PROJECT_ROOT/requirements-dev.txt"
    if [ -f "$DEV_REQ_FILE" ]; then
        "$PY_CMD" -m pip install -r "$DEV_REQ_FILE" --quiet
        echo -e "\033[0;32m  Dev dependencies installed.\033[0m"
    fi
fi

echo -e "\n\033[1;36m=== MSRA Installation Complete ===\033[0m"
echo -e "\033[1;37mQuick start:\033[0m"
echo -e "\033[1;37m  1. Place your data in MSRA/data/\033[0m"
echo -e "\033[1;37m  2. Run: /msra in Claude Code\033[0m"
echo -e "\033[1;37m  3. At Stage 4 checkpoint: [A] stats report done / [B] continue to paper\033[0m"
echo -e "\033[1;37m  4. Or:  /msra-calibrate --status to check calibration\033[0m"
