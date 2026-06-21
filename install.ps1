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
    Write-Host "[1/7] Checking Python..." -ForegroundColor Yellow
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
    Write-Host "[1/7] Skipping Python check (-SkipPython)" -ForegroundColor DarkGray
}

# 2. Check R
if (-not $SkipR) {
    Write-Host "`n[2/7] Checking R..." -ForegroundColor Yellow
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
    Write-Host "[2/7] Skipping R check (-SkipR)" -ForegroundColor DarkGray
}

# 3. Create output directories
Write-Host "`n[3/7] Creating output directories..." -ForegroundColor Yellow
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

# 4. Initialize passport.json
Write-Host "`n[4/7] Initializing passport..." -ForegroundColor Yellow
$passportPath = Join-Path $ProjectRoot "MSRA\passport\passport.json"
if (-not (Test-Path $passportPath)) {
    $passport = @{
        passport_id = "msra-$(Get-Date -Format 'yyyyMMdd')-001"
        passport_schema_version = "1"
        pipeline_version = "0.8.1"
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

# 5. Initialize calibration_db.json
Write-Host "`n[5/7] Initializing calibration database..." -ForegroundColor Yellow
$calibPath = Join-Path $ProjectRoot "MSRA\calibration\calibration_db.json"
if (-not (Test-Path $calibPath)) {
    $calibDb = @()  # CalibrationDatabase expects a JSON array of entries
    $calibDb = $calibDb | ConvertTo-Json -Depth 5
    Set-Content -Path $calibPath -Value $calibDb
    Write-Host "  Created: calibration_db.json" -ForegroundColor Green
} else {
    Write-Host "  Exists:  calibration_db.json" -ForegroundColor DarkGray
}

# 6. Verify all skill directories and key files present
Write-Host "`n[6/7] Verifying project integrity..." -ForegroundColor Yellow
$skillDirs = @(
    "skills\pipeline",
    "skills\data-prep",
    "skills\analysis-plan",
    "skills\analysis-exec",
    "skills\report",
    "skills\calibration",
    "skills\deep-research",
    "skills\academic-paper-reviewer"
)
$keyFiles = @(
    "shared\handoff_schemas.md",
    "shared\passport\passport_schema.md",
    "shared\sap\sap_standard.md",
    ".claude\CLAUDE.md",
    "commands\msra.md",
    "commands\ars-full.md",
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

# 7. Verify all SKILL.md files exist
Write-Host "`n[7/7] Verifying SKILL.md files..." -ForegroundColor Yellow
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

# Dev mode: install dev dependencies
if ($Dev) {
    Write-Host "`n[DEV] Installing development dependencies..." -ForegroundColor Magenta
    $devReqFile = Join-Path $ProjectRoot "requirements-dev.txt"
    if (Test-Path $devReqFile) {
        pip install -r $devReqFile --quiet
        Write-Host "  Dev dependencies installed." -ForegroundColor Green
    }
}

Write-Host "`n=== MSRA Installation Complete ===" -ForegroundColor Cyan
Write-Host "Quick start:" -ForegroundColor White
Write-Host "  1. Place your data in MSRA\data\" -ForegroundColor White
Write-Host "  2. Run: /msra in Claude Code" -ForegroundColor White
Write-Host "  3. At Stage 4 checkpoint: [A] stats report done / [B] continue to paper" -ForegroundColor White
Write-Host "  4. Or:  /msra-calibrate --status to check calibration" -ForegroundColor White
