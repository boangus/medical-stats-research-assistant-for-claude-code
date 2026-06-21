# MSRA (Medical Statistics Research Assistant) - Uninstall Script
# Usage: .\uninstall.ps1 [-KeepData]

param(
    [switch]$KeepData = $false
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot

Write-Host "=== MSRA Uninstaller ===" -ForegroundColor Cyan
Write-Host "Project root: $ProjectRoot`n"

# 1. Remove junction links (if created by install)
Write-Host "[1/3] Removing junction links..." -ForegroundColor Yellow

$claudeSkillsDir = "$env:USERPROFILE\.claude\skills"
$claudeCommandsDir = "$env:USERPROFILE\.claude\commands"

$msraSkills = @(
    "msra-pipeline",
    "msra-data-prep",
    "msra-analysis-plan",
    "msra-analysis-exec",
    "msra-report",
    "msra-calibration",
    "msra-academic-paper-reviewer",
    "msra-deep-research"
)

foreach ($skill in $msraSkills) {
    $skillPath = Join-Path $claudeSkillsDir $skill
    if (Test-Path $skillPath) {
        if ((Get-Item $skillPath).Attributes -band [IO.FileAttributes]::ReparsePoint) {
            Remove-Item $skillPath -Force
            Write-Host "  Removed junction: $skill" -ForegroundColor Green
        }
    }
}

$msraCommands = @(
    "msra.md",
    "msra-data.md",
    "msra-plan.md",
    "msra-exec.md",
    "msra-report.md",
    "msra-calibrate.md",
    "msra-paper.md",
    "ars-paper.md",
    "ars-full.md",
    "ars-reviewer.md"
)

foreach ($cmd in $msraCommands) {
    $cmdPath = Join-Path $claudeCommandsDir $cmd
    if (Test-Path $cmdPath) {
        if ((Get-Item $cmdPath).Attributes -band [IO.FileAttributes]::ReparsePoint) {
            Remove-Item $cmdPath -Force
            Write-Host "  Removed junction: $cmd" -ForegroundColor Green
        }
    }
}

# 2. Remove output directories (unless -KeepData)
if (-not $KeepData) {
    Write-Host "`n[2/3] Removing output directories..." -ForegroundColor Yellow
    $outputDirs = @(
        "MSRA\data",
        "MSRA\reports",
        "MSRA\passport",
        "MSRA\calibration"
    )
    foreach ($dir in $outputDirs) {
        $fullPath = Join-Path $ProjectRoot $dir
        if (Test-Path $fullPath) {
            Remove-Item $fullPath -Recurse -Force
            Write-Host "  Removed: $dir" -ForegroundColor Green
        } else {
            Write-Host "  Not found: $dir" -ForegroundColor DarkGray
        }
    }
} else {
    Write-Host "`n[2/3] Keeping data directories (-KeepData)" -ForegroundColor DarkGray
}

# 3. Remove Python virtual environment (if exists)
Write-Host "`n[3/3] Checking for virtual environment..." -ForegroundColor Yellow
$venvDir = Join-Path $ProjectRoot ".venv"
if (Test-Path $venvDir) {
    Remove-Item $venvDir -Recurse -Force
    Write-Host "  Removed: .venv" -ForegroundColor Green
}

Write-Host "`n=== MSRA Uninstallation Complete ===" -ForegroundColor Cyan
Write-Host "To completely remove the plugin, delete the project directory:" -ForegroundColor White
Write-Host "  Remove-Item -Recurse -Force '$ProjectRoot'" -ForegroundColor White
