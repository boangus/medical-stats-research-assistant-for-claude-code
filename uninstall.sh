#!/bin/bash
# MSRA (Medical Statistics Research Assistant) - Uninstall Script for Mac/Linux
# Usage: ./uninstall.sh [--keep-data]

set -e

PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
KEEP_DATA=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --keep-data) KEEP_DATA=true ;;
    esac
done

echo -e "\033[1;36m=== MSRA Uninstaller ===\033[0m"
echo "Project root: $PROJECT_ROOT"
echo ""

# 1. Remove junction links (if created by install)
echo -e "\033[1;33m[1/3] Removing junction links...\033[0m"

CLAUDE_SKILLS_DIR="$HOME/.claude/skills"
CLAUDE_COMMANDS_DIR="$HOME/.claude/commands"

MSRA_SKILLS=(
    "msra-pipeline"
    "msra-data-prep"
    "msra-analysis-plan"
    "msra-analysis-exec"
    "msra-report"
    "msra-calibration"
    "msra-academic-paper-reviewer"
    "msra-deep-research"
)

for skill in "${MSRA_SKILLS[@]}"; do
    SKILL_PATH="$CLAUDE_SKILLS_DIR/$skill"
    if [ -L "$SKILL_PATH" ]; then
        rm -f "$SKILL_PATH"
        echo -e "\033[0;32m  Removed junction: $skill\033[0m"
    fi
done

MSRA_COMMANDS=(
    "msra.md"
    "msra-data.md"
    "msra-plan.md"
    "msra-exec.md"
    "msra-report.md"
    "msra-calibrate.md"
    "msra-paper.md"
    "ars-paper.md"
    "ars-full.md"
    "ars-reviewer.md"
)

for cmd in "${MSRA_COMMANDS[@]}"; do
    CMD_PATH="$CLAUDE_COMMANDS_DIR/$cmd"
    if [ -L "$CMD_PATH" ]; then
        rm -f "$CMD_PATH"
        echo -e "\033[0;32m  Removed junction: $cmd\033[0m"
    fi
done

# 2. Remove output directories (unless --keep-data)
if [ "$KEEP_DATA" = false ]; then
    echo -e "\n\033[1;33m[2/3] Removing output directories...\033[0m"
    OUTPUT_DIRS=(
        "MSRA/data"
        "MSRA/reports"
        "MSRA/passport"
        "MSRA/calibration"
    )
    for dir in "${OUTPUT_DIRS[@]}"; do
        FULL_PATH="$PROJECT_ROOT/$dir"
        if [ -d "$FULL_PATH" ]; then
            rm -rf "$FULL_PATH"
            echo -e "\033[0;32m  Removed: $dir\033[0m"
        else
            echo -e "\033[0;90m  Not found: $dir\033[0m"
        fi
    done
else
    echo -e "\n\033[0;90m[2/3] Keeping data directories (--keep-data)\033[0m"
fi

# 3. Remove Python virtual environment (if exists)
echo -e "\n\033[1;33m[3/3] Checking for virtual environment...\033[0m"
VENV_DIR="$PROJECT_ROOT/.venv"
if [ -d "$VENV_DIR" ]; then
    rm -rf "$VENV_DIR"
    echo -e "\033[0;32m  Removed: .venv\033[0m"
fi

echo -e "\n\033[1;36m=== MSRA Uninstallation Complete ===\033[0m"
echo -e "\033[1;37mTo completely remove the plugin, delete the project directory:\033[0m"
echo -e "\033[1;37m  rm -rf '$PROJECT_ROOT'\033[0m"
