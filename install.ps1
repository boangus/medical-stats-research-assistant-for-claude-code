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
    Write-Host "[1/6] Checking Python..." -ForegroundColor Yellow
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
    Write-Host "[1/6] Skipping Python check (-SkipR)" -ForegroundColor DarkGray
}

# 2. Check R
if (-not $SkipR) {
    Write-Host "`n[2/6] Checking R..." -ForegroundColor Yellow
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
    Write-Host "[2/6] Skipping R check (-SkipR)" -ForegroundColor DarkGray
}

# 3. Create output directories
Write-Host "`n[3/6] Creating output directories..." -ForegroundColor Yellow
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
Write-Host "`n[4/6] Initializing passport..." -ForegroundColor Yellow
$passportPath = Join-Path $ProjectRoot "MSRA\passport\passport.json"
if (-not (Test-Path $passportPath)) {
    $passport = @{
        passport_id = "msra-$(Get-Date -Format 'yyyyMMdd')-001"
        passport_schema_version = "1"
        pipeline_version = "0.8.0"
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
Write-Host "`n[5/6] Initializing calibration database..." -ForegroundColor Yellow
$calibPath = Join-Path $ProjectRoot "MSRA\calibration\calibration_db.json"
if (-not (Test-Path $calibPath)) {
    $calibDb = @()  # CalibrationDatabase expects a JSON array of entries
    $calibDb = $calibDb | ConvertTo-Json -Depth 5
    Set-Content -Path $calibPath -Value $calibDb
    Write-Host "  Created: calibration_db.json" -ForegroundColor Green
} else {
    Write-Host "  Exists:  calibration_db.json" -ForegroundColor DarkGray
}

# 6. Verify ARS shared dependencies (Paper Track readiness)
Write-Host "`n[6/6] Verifying ARS shared dependencies..." -ForegroundColor Yellow
$arsCheckFiles = @(
    "shared\handoff_schemas.md",
    "shared\contracts\passport\claim_audit_result.schema.json",
    "shared\contracts\reviewer\full.json",
    "shared\contracts\writer\full.json",
    "shared\references\intent_clarification_protocol.md",
    "shared\.claude\CLAUDE.md",
    "shared\collaboration_depth_rubric.md",
    "shared\style_calibration_protocol.md",
    "shared\mode_spectrum.md",
    "shared\compliance_checkpoint_protocol.md"
)
$missing = @()
foreach ($f in $arsCheckFiles) {
    $fullPath = Join-Path $ProjectRoot $f
    if (-not (Test-Path $fullPath)) { $missing += $f }
}
if ($missing.Count -gt 0) {
    Write-Host "  WARNING: ARS shared files missing (Paper Track will not work):" -ForegroundColor DarkYellow
    foreach ($m in $missing) { Write-Host "    - $m" -ForegroundColor DarkYellow }
    Write-Host "  These files should be merged from upstream ARS (academic-research-skills)." -ForegroundColor DarkYellow
    Write-Host "  See docs/superpowers/specs/2026-06-17-msra-ars-integration-design.md Task 1." -ForegroundColor DarkYellow
} else {
    Write-Host "  All ARS shared dependencies present." -ForegroundColor Green
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
