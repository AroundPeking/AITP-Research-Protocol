# ==============================================================================
# Multi-AI Tools Unified Sync Script
# ==============================================================================
# Canonical shared skill source: repo-local skills-shared/
# Default targets: repo-local .codex-home/skills, .opencode/skills, and .kimi/skills
# Optional global targets: %USERPROFILE%\.codex\skills, %USERPROFILE%\.claude\skills, and %USERPROFILE%\.kimi\skills
# Usage:
#   powershell -ExecutionPolicy Bypass -File scripts\multi-ai-sync.ps1
#   powershell -ExecutionPolicy Bypass -File scripts\multi-ai-sync.ps1 -IncludeGlobal
# ==============================================================================

param(
    [switch]$IncludeGlobal
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$sourceMemory = Join-Path $repoRoot "CLAUDE.md"
$sourceSkills = Join-Path $repoRoot "skills-shared"
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"

Write-Host ">> Syncing AI project config: $repoRoot" -ForegroundColor Cyan

function Ensure-ParentDirectory {
    param([string]$Path)

    $parent = Split-Path -Parent $Path
    if ($parent -and -not (Test-Path $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
        Write-Host "  - Created parent directory: $parent" -ForegroundColor DarkGray
    }
}

function Move-ToBackup {
    param([string]$Path)

    $backupPath = "$Path.backup-$timestamp"
    Move-Item -Path $Path -Destination $backupPath -Force
    Write-Host "  - Backup: moved existing path to $backupPath" -ForegroundColor Yellow
}

function Sync-HardLink {
    param(
        [string]$Path,
        [string]$Target
    )

    if (-not (Test-Path $Target)) {
        Write-Host "[!] Source file missing: $Target" -ForegroundColor Yellow
        return $false
    }

    Ensure-ParentDirectory -Path $Path

    if (Test-Path $Path) {
        $existing = Get-Item -Force $Path
        if ($existing.PSIsContainer) {
            Move-ToBackup -Path $Path
        } elseif ((Get-Content -Raw -Encoding UTF8 $Path) -eq (Get-Content -Raw -Encoding UTF8 $Target)) {
            Remove-Item -Force $Path
        } else {
            Move-ToBackup -Path $Path
        }
    }

    try {
        New-Item -ItemType HardLink -Path $Path -Target $Target -ErrorAction Stop | Out-Null
        Write-Host "[OK] $Path (HardLink -> $Target) created" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "[X] $Path hard link creation failed: $_" -ForegroundColor Red
        return $false
    }
}

function Sync-Junction {
    param(
        [string]$Path,
        [string]$Target
    )

    if (-not (Test-Path $Target)) {
        Write-Host "[!] Source directory missing: $Target" -ForegroundColor Yellow
        return $false
    }

    Ensure-ParentDirectory -Path $Path

    if (Test-Path $Path) {
        $existing = Get-Item -Force $Path
        $currentTargets = @($existing.Target | Where-Object { $_ })

        if ($existing.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            if ($currentTargets -contains $Target) {
                Write-Host "[OK] $Path already points to $Target" -ForegroundColor Green
                return $true
            }

            Remove-Item -Recurse -Force $Path
            Write-Host "  - Cleanup: removed old junction/link $Path" -ForegroundColor Yellow
        } else {
            Move-ToBackup -Path $Path
        }
    }

    try {
        New-Item -ItemType Junction -Path $Path -Target $Target -ErrorAction Stop | Out-Null
        Write-Host "[OK] $Path (Junction -> $Target) synced" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "[X] $Path junction creation failed: $_" -ForegroundColor Red
        return $false
    }
}

$successCount = 0
$failCount = 0

if (Sync-HardLink -Path (Join-Path $repoRoot "AGENTS.md") -Target $sourceMemory) {
    $successCount++
} else {
    $failCount++
}

$skillTargets = @(
    (Join-Path $repoRoot ".codex-home\skills"),
    (Join-Path $repoRoot ".opencode\skills"),
    (Join-Path $repoRoot ".kimi\skills")
)

if ($IncludeGlobal) {
    $skillTargets += @(
        (Join-Path $env:USERPROFILE ".codex\skills"),
        (Join-Path $env:USERPROFILE ".claude\skills"),
        (Join-Path $env:USERPROFILE ".kimi\skills")
    )
}

foreach ($target in $skillTargets) {
    if (Sync-Junction -Path $target -Target $sourceSkills) {
        $successCount++
    } else {
        $failCount++
    }
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Sync complete" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Stats: Success $successCount, Failed $failCount" -ForegroundColor Cyan
Write-Host ""
Write-Host "- Source of truth" -ForegroundColor Yellow
Write-Host "  1. CLAUDE.md for project memory/instructions" -ForegroundColor White
Write-Host "  2. skills-shared\\ for shared skills" -ForegroundColor White
Write-Host "  3. Restart Codex/OpenCode/Claude/Kimi after rewiring skills" -ForegroundColor White
