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
    Write-Host "[1/5] Checking Python..." -ForegroundColor Yellow
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
    Write-Host "[1/5] Skipping Python check (-SkipR)" -ForegroundColor DarkGray
}

# 2. Check R
if (-not $SkipR) {
    Write-Host "`n[2/5] Checking R..." -ForegroundColor Yellow
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
    Write-Host "[2/5] Skipping R check (-SkipR)" -ForegroundColor DarkGray
}

# 3. Create output directories
Write-Host "`n[3/5] Creating output directories..." -ForegroundColor Yellow
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
Write-Host "`n[4/5] Initializing passport..." -ForegroundColor Yellow
$passportPath = Join-Path $ProjectRoot "MSRA\passport\passport.json"
if (-not (Test-Path $passportPath)) {
    $passport = @{
        version = "0.6.0"
        created_at = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
        artifacts = @{}
        stages = @{
            "data-prep" = "not_started"
            "analysis-plan" = "not_started"
            "analysis-exec" = "not_started"
            "report" = "not_started"
        }
        gates = @{
            "data-quality" = "pending"
            "sap-quality" = "pending"
            "results-quality" = "pending"
        }
    } | ConvertTo-Json -Depth 5
    Set-Content -Path $passportPath -Value $passport
    Write-Host "  Created: passport.json" -ForegroundColor Green
} else {
    Write-Host "  Exists:  passport.json" -ForegroundColor DarkGray
}

# 5. Initialize calibration_db.json
Write-Host "`n[5/5] Initializing calibration database..." -ForegroundColor Yellow
$calibPath = Join-Path $ProjectRoot "MSRA\calibration\calibration_db.json"
if (-not (Test-Path $calibPath)) {
    $calibDb = @{
        version = "0.6.0"
        created_at = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
        records = @()
        summary = @{
            total_comparisons = 0
            method_match_rate = 0
            conclusion_accuracy = 0
        }
    } | ConvertTo-Json -Depth 5
    Set-Content -Path $calibPath -Value $calibDb
    Write-Host "  Created: calibration_db.json" -ForegroundColor Green
} else {
    Write-Host "  Exists:  calibration_db.json" -ForegroundColor DarkGray
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
Write-Host "  3. Or:  /msra-calibrate --status to check calibration" -ForegroundColor White
