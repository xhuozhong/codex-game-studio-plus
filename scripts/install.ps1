[CmdletBinding()]
param(
    [ValidateSet('User','Project')][string]$Scope = 'User',
    [string]$ProjectRoot,
    [switch]$Force
)
. (Join-Path $PSScriptRoot 'common.ps1')
$repoRoot = Split-Path $PSScriptRoot -Parent
Test-StudioSource $repoRoot
$paths = Get-StudioPaths $Scope $ProjectRoot
$sourceRoot = Join-Path $repoRoot 'skills'
$destRoot = $paths.Skills
$sourceFull = [IO.Path]::GetFullPath($sourceRoot).TrimEnd('\','/') + [IO.Path]::DirectorySeparatorChar
$destFull = [IO.Path]::GetFullPath($destRoot).TrimEnd('\','/') + [IO.Path]::DirectorySeparatorChar
if ($sourceFull.StartsWith($destFull,[StringComparison]::OrdinalIgnoreCase) -or $destFull.StartsWith($sourceFull,[StringComparison]::OrdinalIgnoreCase)) { throw 'Source and target trees must not overlap.' }

# Preflight all conflicts before changing any existing Skill.
foreach ($name in $StudioSkills) {
    $dest = Get-SafeChild $destRoot $name
    Assert-NoLink $dest
    if (Test-Path -LiteralPath $dest) {
        if (-not (Test-Path -LiteralPath $dest -PathType Container)) { throw "Skill destination is not a directory: $name" }
        if (-not $Force) { throw "Already exists: $name. Review it, then use REPAIR_WINDOWS.cmd or -Force to back up and update." }
    }
    # Copy-Item and Get-FileHash in Windows PowerShell 5.1 still have ordinary
    # path limits. Backups use extended paths, but validate every copy target
    # before creating any directory or moving an existing installation.
    $sourceFolder = Get-SafeChild $sourceRoot $name
    foreach ($file in @(Get-StudioFiles $sourceFolder)) {
        $relative = $file.FullName.Substring($sourceFolder.Length).TrimStart('\','/')
        $targetFile = Get-SafeChild $dest $relative
        if ($file.FullName.Length -ge 260 -or $targetFile.Length -ge 260 -or [IO.Path]::GetDirectoryName($targetFile).Length -ge 248) {
            throw 'Install path is too long for Windows PowerShell 5.1 copy/verification. Use a shorter package or project path; no Skills have been changed.'
        }
    }
}
New-Item -ItemType Directory -Path $destRoot -Force | Out-Null
$backup = New-StudioBackup $paths.Backups
$moved = [Collections.Generic.List[string]]::new()
$started = [Collections.Generic.List[string]]::new()
try {
    foreach ($name in $StudioSkills) {
        $dest = Get-SafeChild $destRoot $name
        if (Test-Path -LiteralPath $dest) {
            Move-StudioDirectory $dest (Get-SafeChild $backup $name)
            $moved.Add($name)
        }
        $started.Add($name)
        Copy-Item -LiteralPath (Get-SafeChild $sourceRoot $name) -Destination $dest -Recurse
        $marker = @{ package = $StudioPackage; version = $StudioVersion; skill = $name }
        $marker | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $dest $StudioMarker) -Encoding UTF8
        foreach ($file in Get-StudioFiles (Join-Path $sourceRoot $name)) {
            $relative = $file.FullName.Substring((Join-Path $sourceRoot $name).Length).TrimStart('\','/')
            if ((Get-FileHash -LiteralPath $file.FullName).Hash -ne (Get-FileHash -LiteralPath (Join-Path $dest $relative)).Hash) {
                throw "Copy verification failed: $name/$relative"
            }
        }
    }
} catch {
    $failure = $_
    foreach ($name in $started) {
        $dest = Get-SafeChild $destRoot $name
        try {
            if (Test-Path -LiteralPath $dest) { Move-StudioDirectory $dest (Get-SafeChild $backup ('failed-' + $name)) }
            if ($moved.Contains($name)) { Move-StudioDirectory (Get-SafeChild $backup $name) $dest }
        } catch { Write-Warning "Automatic recovery failed for $name. Inspect backup: $backup" }
    }
    throw $failure
}
Write-Output "Installed and verified $($StudioSkills.Count) Skills ($StudioPackage $StudioVersion): $destRoot"
Write-Output "Backup location (empty on a fresh install): $backup"
Write-Output 'If Skills do not appear, restart Codex. Invoke $game-studio-director in your game project.'
