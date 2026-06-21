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
Write-Host "[1/4] Removing junction links..." -ForegroundColor Yellow

# Remove project-local .claude/commands/ and .claude/skills/ (junctions created by install)
$projectCommands = Join-Path $ProjectRoot ".claude\commands"
$projectSkills = Join-Path $ProjectRoot ".claude\skills"

if (Test-Path $projectCommands) {
    if ((Get-Item $projectCommands).Attributes -band [IO.FileAttributes]::ReparsePoint) {
        Remove-Item $projectCommands -Force
        Write-Host "  Removed junction: .claude/commands/" -ForegroundColor Green
    }
}

if (Test-Path $projectSkills) {
    # Remove individual skill junctions inside .claude/skills/
    $msraSkills = @(
        "pipeline", "data-prep", "analysis-plan", "analysis-exec",
        "report", "calibration", "deep-research", "academic-paper-reviewer"
    )
    foreach ($skill in $msraSkills) {
        $skillPath = Join-Path $projectSkills $skill
        if (Test-Path $skillPath) {
            if ((Get-Item $skillPath).Attributes -band [IO.FileAttributes]::ReparsePoint) {
                Remove-Item $skillPath -Force
                Write-Host "  Removed junction: .claude/skills/$skill" -ForegroundColor Green
            }
        }
    }
}

# Also clean up legacy global Claude config junctions (if present)
$claudeSkillsDir = "$env:USERPROFILE\.claude\skills"
$claudeCommandsDir = "$env:USERPROFILE\.claude\commands"

$legacySkills = @(
    "msra-pipeline", "msra-data-prep", "msra-analysis-plan", "msra-analysis-exec",
    "msra-report", "msra-calibration", "msra-academic-paper-reviewer", "msra-deep-research"
)
foreach ($skill in $legacySkills) {
    $skillPath = Join-Path $claudeSkillsDir $skill
    if (Test-Path $skillPath) {
        if ((Get-Item $skillPath).Attributes -band [IO.FileAttributes]::ReparsePoint) {
            Remove-Item $skillPath -Force
            Write-Host "  Removed legacy junction: $skill" -ForegroundColor Green
        }
    }
}

$legacyCommands = @(
    "msra.md", "msra-data.md", "msra-plan.md", "msra-exec.md", "msra-report.md",
    "msra-calibrate.md", "msra-paper.md", "msra-write.md", "msra-full.md", "msra-reviewer.md"
)
foreach ($cmd in $legacyCommands) {
    $cmdPath = Join-Path $claudeCommandsDir $cmd
    if (Test-Path $cmdPath) {
        if ((Get-Item $cmdPath).Attributes -band [IO.FileAttributes]::ReparsePoint) {
            Remove-Item $cmdPath -Force
            Write-Host "  Removed legacy junction: $cmd" -ForegroundColor Green
        }
    }
}

# 2. Remove output directories (unless -KeepData)
if (-not $KeepData) {
    Write-Host "`n[2/4] Removing output directories..." -ForegroundColor Yellow
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
    Write-Host "`n[2/4] Keeping data directories (-KeepData)" -ForegroundColor DarkGray
}

# 3. Remove Python virtual environment (if exists)
Write-Host "`n[3/4] Checking for virtual environment..." -ForegroundColor Yellow
$venvDir = Join-Path $ProjectRoot ".venv"
if (Test-Path $venvDir) {
    Remove-Item $venvDir -Recurse -Force
    Write-Host "  Removed: .venv" -ForegroundColor Green
} else {
    Write-Host "  No .venv found." -ForegroundColor DarkGray
}

# 4. Remove runtime cache
Write-Host "`n[4/4] Removing runtime cache..." -ForegroundColor Yellow
$cacheDirs = @(".msra", "__pycache__", ".pytest_cache")
foreach ($cache in $cacheDirs) {
    $cachePath = Join-Path $ProjectRoot $cache
    if (Test-Path $cachePath) {
        Remove-Item $cachePath -Recurse -Force
        Write-Host "  Removed: $cache" -ForegroundColor Green
    }
}

Write-Host "`n=== MSRA Uninstallation Complete ===" -ForegroundColor Cyan
Write-Host "To completely remove the plugin, delete the project directory:" -ForegroundColor White
Write-Host "  Remove-Item -Recurse -Force '$ProjectRoot'" -ForegroundColor White
