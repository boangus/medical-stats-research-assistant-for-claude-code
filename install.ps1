# MSRA (Medical Statistics Research Assistant) - Install Script
# Usage: .\install.ps1 [-SkipR] [-SkipPython] [-Dev]

param(
    [switch]$SkipR = $false,
    [switch]$SkipPython = $false,
    [switch]$Dev = $false
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot

Write-Host "=== MSRA Installer ===" -ForegroundColor Cyan
Write-Host "Project root: $ProjectRoot`n"

# 1. Check Python
if (-not $SkipPython) {
    Write-Host "[1/9] Checking Python..." -ForegroundColor Yellow
    try {
        $pyVersion = python --version 2>&1
        Write-Host "  Found: $pyVersion" -ForegroundColor Green
    } catch {
        Write-Host "  ERROR: Python not found. Install Python 3.9+ and retry." -ForegroundColor Red
        exit 1
    }

    # Install Python dependencies
    $reqFile = Join-Path $ProjectRoot "requirements.txt"
    if (Test-Path $reqFile) {
        Write-Host "  Installing Python dependencies..." -ForegroundColor Yellow
        pip install -r $reqFile --quiet
        Write-Host "  Done." -ForegroundColor Green
    } else {
        Write-Host "  No requirements.txt found, skipping pip install." -ForegroundColor DarkGray
    }
} else {
    Write-Host "[1/9] Skipping Python check (-SkipPython)" -ForegroundColor DarkGray
}

# 2. Check R
if (-not $SkipR) {
    Write-Host "`n[2/9] Checking R..." -ForegroundColor Yellow
    try {
        $rVersion = Rscript --version 2>&1
        Write-Host "  Found: $rVersion" -ForegroundColor Green
    } catch {
        Write-Host "  WARNING: R not found. R-based analysis will not work." -ForegroundColor DarkYellow
        Write-Host "  Install R 4.0+ from https://cran.r-project.org/" -ForegroundColor DarkYellow
    }

    # Install R packages
    $rPackages = @("survival", "tableone", "forestplot", "ggplot2", "dplyr", "tidyr", "broom", "sandwich", "lmtest", "logistf")
    Write-Host "  Checking R packages..." -ForegroundColor Yellow
    $rScript = $rPackages | ForEach-Object { "if (!require('$_', quietly=TRUE)) install.packages('$_', repos='https://cran.r-project.org/')" }
    $rScript += "cat('R packages installed\n')"
    $tempR = Join-Path $env:TEMP "msra_install.R"
    $rScript | Set-Content $tempR
    Rscript $tempR
    Remove-Item $tempR -ErrorAction SilentlyContinue
} else {
    Write-Host "[2/9] Skipping R check (-SkipR)" -ForegroundColor DarkGray
}

# 3. Create output directories
Write-Host "`n[3/9] Creating output directories..." -ForegroundColor Yellow
$dirs = @(
    "MSRA\data",
    "MSRA\reports\figures",
    "MSRA\reports\tables",
    "MSRA\passport",
    "MSRA\calibration"
)
foreach ($dir in $dirs) {
    $fullPath = Join-Path $ProjectRoot $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "  Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "  Exists:  $dir" -ForegroundColor DarkGray
    }
}

# 4. Create .claude/commands/ and .claude/skills/ symlinks for Claude Code discovery
Write-Host "`n[4/9] Setting up Claude Code discovery paths..." -ForegroundColor Yellow

$claudeDir = Join-Path $ProjectRoot ".claude"
$commandsLink = Join-Path $claudeDir "commands"
$skillsLink = Join-Path $claudeDir "skills"
$commandsSource = Join-Path $ProjectRoot "commands"
$skillsSource = Join-Path $ProjectRoot "skills"

# Ensure .claude directory exists
if (-not (Test-Path $claudeDir)) {
    New-Item -ItemType Directory -Path $claudeDir -Force | Out-Null
}

# Create commands junction/symlink
if (-not (Test-Path $commandsLink)) {
    try {
        New-Item -ItemType Junction -Path $commandsLink -Target $commandsSource | Out-Null
        Write-Host "  Created junction: .claude/commands/ -> commands/" -ForegroundColor Green
    } catch {
        # Fallback: copy files if junction fails (e.g. non-admin)
        New-Item -ItemType Directory -Path $commandsLink -Force | Out-Null
        Copy-Item "$commandsSource\*.md" $commandsLink -Force
        Write-Host "  Copied commands to .claude/commands/ (junction failed)" -ForegroundColor DarkYellow
    }
} else {
    Write-Host "  Exists:  .claude/commands/" -ForegroundColor DarkGray
}

# Create skills directory and symlink each skill subdirectory
if (-not (Test-Path $skillsLink)) {
    New-Item -ItemType Directory -Path $skillsLink -Force | Out-Null
}
$skillDirs = @(
    "pipeline", "data-prep", "analysis-plan", "analysis-exec",
    "report", "calibration", "systematic-survey", "medical-paper-reviewer"
)
foreach ($skill in $skillDirs) {
    $skillLinkPath = Join-Path $skillsLink $skill
    $skillSourcePath = Join-Path $skillsSource $skill
    if (-not (Test-Path $skillLinkPath) -and (Test-Path $skillSourcePath)) {
        try {
            New-Item -ItemType Junction -Path $skillLinkPath -Target $skillSourcePath | Out-Null
            Write-Host "  Created junction: .claude/skills/$skill -> skills/$skill" -ForegroundColor Green
        } catch {
            # Fallback: copy if junction fails
            Copy-Item $skillSourcePath $skillLinkPath -Recurse -Force
            Write-Host "  Copied skill: .claude/skills/$skill (junction failed)" -ForegroundColor DarkYellow
        }
    }
}
Write-Host "  Claude Code discovery paths configured." -ForegroundColor Green

# 5. Initialize passport.json
Write-Host "`n[5/9] Initializing passport..." -ForegroundColor Yellow
$passportPath = Join-Path $ProjectRoot "MSRA\passport\passport.json"
if (-not (Test-Path $passportPath)) {
    $passport = @{
        passport_id = "msra-$(Get-Date -Format 'yyyyMMdd')-001"
        passport_schema_version = "1"
        pipeline_version = "0.9.0"
        created_at = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
        updated_at = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
        status = "in_progress"
        study_type = $null
        track = $null
        current_stage = "stage_1"
        artifacts = @()
        checkpoints = @{
            last_completed = $null
            last_verified = $null
            resume_point = "stage_1"
        }
        gates = @{}
    } | ConvertTo-Json -Depth 5
    Set-Content -Path $passportPath -Value $passport
    Write-Host "  Created: passport.json" -ForegroundColor Green
} else {
    Write-Host "  Exists:  passport.json" -ForegroundColor DarkGray
}

# 6. Initialize calibration_db.json
Write-Host "`n[6/9] Initializing calibration database..." -ForegroundColor Yellow
$calibPath = Join-Path $ProjectRoot "MSRA\calibration\calibration_db.json"
if (-not (Test-Path $calibPath)) {
    $calibDb = @()  # CalibrationDatabase expects a JSON array of entries
    $calibDb = $calibDb | ConvertTo-Json -Depth 5
    Set-Content -Path $calibPath -Value $calibDb
    Write-Host "  Created: calibration_db.json" -ForegroundColor Green
} else {
    Write-Host "  Exists:  calibration_db.json" -ForegroundColor DarkGray
}

# 7. Verify all skill directories and key files present
Write-Host "`n[7/9] Verifying project integrity..." -ForegroundColor Yellow
$skillDirs = @(
    "skills\pipeline",
    "skills\data-prep",
    "skills\analysis-plan",
    "skills\analysis-exec",
    "skills\report",
    "skills\calibration",
    "skills\systematic-survey",
    "skills\medical-paper-reviewer"
)
$keyFiles = @(
    "shared\handoff_schemas.md",
    "shared\passport\passport_schema.md",
    "shared\sap\sap_standard.md",
    ".claude\CLAUDE.md",
    "commands\msra.md",
    "commands\msra-full.md",
    "manifest.json"
)

$missingDirs = @()
foreach ($d in $skillDirs) {
    $fullPath = Join-Path $ProjectRoot $d
    if (-not (Test-Path $fullPath)) { $missingDirs += $d }
}
$missingFiles = @()
foreach ($f in $keyFiles) {
    $fullPath = Join-Path $ProjectRoot $f
    if (-not (Test-Path $fullPath)) { $missingFiles += $f }
}

if ($missingDirs.Count -gt 0 -or $missingFiles.Count -gt 0) {
    Write-Host "  WARNING: Project files missing:" -ForegroundColor DarkYellow
    if ($missingDirs.Count -gt 0) {
        Write-Host "  Missing skill directories:" -ForegroundColor DarkYellow
        foreach ($m in $missingDirs) { Write-Host "    - $m" -ForegroundColor DarkYellow }
    }
    if ($missingFiles.Count -gt 0) {
        Write-Host "  Missing key files:" -ForegroundColor DarkYellow
        foreach ($m in $missingFiles) { Write-Host "    - $m" -ForegroundColor DarkYellow }
    }
    Write-Host "  This is a self-contained plugin. If files are missing, reinstall from source." -ForegroundColor DarkYellow
} else {
    Write-Host "  All 8 skills and key files present. Project is self-contained." -ForegroundColor Green
}

# 8. Verify all SKILL.md files exist
Write-Host "`n[8/9] Verifying SKILL.md files..." -ForegroundColor Yellow
$missingSkillMd = @()
foreach ($d in $skillDirs) {
    $skillMdPath = Join-Path $ProjectRoot "$d\SKILL.md"
    if (-not (Test-Path $skillMdPath)) { $missingSkillMd += "$d\SKILL.md" }
}
if ($missingSkillMd.Count -gt 0) {
    Write-Host "  WARNING: Missing SKILL.md files:" -ForegroundColor DarkYellow
    foreach ($m in $missingSkillMd) { Write-Host "    - $m" -ForegroundColor DarkYellow }
} else {
    Write-Host "  All 8 SKILL.md files present." -ForegroundColor Green
}

# 9. Dev mode: install dev dependencies
if ($Dev) {
    Write-Host "`n[9/9] [DEV] Installing development dependencies..." -ForegroundColor Magenta
    $devReqFile = Join-Path $ProjectRoot "requirements-dev.txt"
    if (Test-Path $devReqFile) {
        pip install -r $devReqFile --quiet
        Write-Host "  Dev dependencies installed." -ForegroundColor Green
    }
} else {
    Write-Host "`n[9/9] Skipping dev dependencies." -ForegroundColor DarkGray
}

Write-Host "`n=== MSRA Installation Complete ===" -ForegroundColor Cyan
Write-Host "Quick start:" -ForegroundColor White
Write-Host "  1. Place your data in MSRA\data\" -ForegroundColor White
Write-Host "  2. Run: /msra in Claude Code" -ForegroundColor White
Write-Host "  3. At Stage 4 checkpoint: [A] stats report done / [B] continue to paper" -ForegroundColor White
Write-Host "  4. Or:  /msra-calibrate --status to check calibration" -ForegroundColor White
