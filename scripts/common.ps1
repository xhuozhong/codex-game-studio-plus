Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Assert-NoLink([string]$Path) {
    $currentPath = [IO.Path]::GetFullPath($Path)
    while ($currentPath) {
        if (Test-Path -LiteralPath $currentPath) {
            if ((Get-Item -LiteralPath $currentPath -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) {
                throw "Symbolic links/junctions are not supported: $currentPath"
            }
        }
        $parentPath = [IO.Path]::GetDirectoryName($currentPath)
        if ($parentPath -eq $currentPath) { break }
        $currentPath = $parentPath
    }
}

function Get-SafeChild([string]$Root, [string]$Relative) {
    if ([IO.Path]::IsPathRooted($Relative)) { throw "Expected relative path: $Relative" }
    $basePath = [IO.Path]::GetFullPath($Root).TrimEnd('\','/')
    $childPath = [IO.Path]::GetFullPath((Join-Path $basePath $Relative))
    if (-not $childPath.StartsWith($basePath + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Path escapes its allowed root: $Relative"
    }
    return $childPath
}

function Get-StudioFiles([string]$Folder) {
    Assert-NoLink $Folder
    foreach ($item in @(Get-ChildItem -LiteralPath $Folder -Force)) {
        Assert-NoLink $item.FullName
        if ($item.PSIsContainer) { Get-StudioFiles $item.FullName } else { $item }
    }
}

function ConvertTo-StudioExtendedPath([string]$Path) {
    $fullPath = [IO.Path]::GetFullPath($Path)
    if ($fullPath.StartsWith('\\?\') -or $fullPath.StartsWith('\\.\')) { throw 'Device-prefixed input paths are not supported.' }
    if ($fullPath.StartsWith('\\')) { return '\\?\UNC\' + $fullPath.Substring(2) }
    return '\\?\' + $fullPath
}

function Move-StudioDirectory([string]$Source, [string]$Destination) {
    # Callers pass only children validated against the source/target/backup roots.
    # Validate ordinary absolute paths before adding the Windows long-path prefix.
    Assert-NoLink $Source
    Assert-NoLink $Destination
    $sourcePath = ConvertTo-StudioExtendedPath $Source
    $destinationPath = ConvertTo-StudioExtendedPath $Destination
    [IO.Directory]::Move($sourcePath, $destinationPath)
}

function Read-StudioManifest([string]$RepoRoot) {
    $manifestPath = Join-Path $RepoRoot 'studio-manifest.json'
    Assert-NoLink $manifestPath
    $manifest = [IO.File]::ReadAllText($manifestPath) | ConvertFrom-Json
    if ($manifest.schema_version -ne 1 -or $manifest.package -cne 'codex-game-studio-plus') { throw 'Unsupported package manifest.' }
    if ($manifest.version -notmatch '^\d+\.\d+\.\d+$') { throw 'Invalid package version.' }
    if ($manifest.skills -isnot [array] -or $manifest.skills.Count -eq 0) { throw 'Manifest skills must be a nonempty array.' }
    $seen = @{}
    foreach ($name in $manifest.skills) {
        if ($name -isnot [string] -or $name.Length -gt 64 -or $name -cnotmatch '^[a-z0-9]+(?:-[a-z0-9]+)*$') { throw "Unsafe Skill name: $name" }
        if ($seen.ContainsKey($name)) { throw "Duplicate Skill name: $name" }
        $seen[$name] = $true
    }
    if ($manifest.entrypoint -cne 'game-studio-director' -or $manifest.entrypoint -cnotin $manifest.skills) { throw 'Invalid director entrypoint.' }
    $versionPath = Join-Path $RepoRoot 'VERSION'
    Assert-NoLink $versionPath
    if ([IO.File]::ReadAllText($versionPath).Trim() -cne $manifest.version) { throw 'VERSION and manifest do not agree.' }
    return $manifest
}

$StudioRepoRoot = Split-Path $PSScriptRoot -Parent
$StudioManifest = Read-StudioManifest $StudioRepoRoot
$StudioSkills = @($StudioManifest.skills)
$StudioPackage = $StudioManifest.package
$StudioVersion = $StudioManifest.version
# Retain the marker filename so the old installer can detect a different owner.
$StudioMarker = '.codex-game-studio.json'

function Get-StudioPaths([string]$Scope, [string]$ProjectRoot) {
    if ($Scope -eq 'Project') {
        if (-not $ProjectRoot -or -not (Test-Path -LiteralPath $ProjectRoot -PathType Container)) { throw 'Project scope requires an existing -ProjectRoot directory.' }
        Assert-NoLink $ProjectRoot
        $basePath = (Resolve-Path -LiteralPath $ProjectRoot).ProviderPath
    } else {
        $basePath = [Environment]::GetFolderPath('UserProfile')
        if (-not $basePath) { throw 'Cannot determine the user profile directory.' }
    }
    Assert-NoLink $basePath
    $agentsPath = Get-SafeChild $basePath '.agents'
    $skillsPath = Get-SafeChild $agentsPath 'skills'
    $backupsPath = Get-SafeChild $agentsPath 'skill-backups'
    $studioBackupPath = Get-SafeChild $backupsPath $StudioPackage
    foreach ($p in @($agentsPath,$skillsPath,$backupsPath,$studioBackupPath)) { Assert-NoLink $p }
    return @{ Skills = $skillsPath; Backups = $studioBackupPath }
}

function Test-StudioSource([string]$RepoRoot) {
    $manifest = Read-StudioManifest $RepoRoot
    $sourceRoot = Get-SafeChild $RepoRoot 'skills'
    Assert-NoLink $sourceRoot
    $items = @(Get-ChildItem -LiteralPath $sourceRoot -Force)
    if ($items.Count -ne $manifest.skills.Count) { throw "Skill folder count differs from manifest: $($items.Count)." }
    foreach ($item in $items) {
        Assert-NoLink $item.FullName
        if (-not $item.PSIsContainer -or $item.Name -cnotin $manifest.skills) { throw "Unexpected Skill entry: $($item.Name)" }
    }
    foreach ($name in $manifest.skills) {
        $folder = Get-SafeChild $sourceRoot $name
        $null = @(Get-StudioFiles $folder)
        $content = [IO.File]::ReadAllText((Join-Path $folder 'SKILL.md'))
        if ($content -notmatch '(?s)\A---\r?\n(.*?)\r?\n---\r?\n') { throw "Invalid frontmatter: $name" }
        $header = $Matches[1]
        if ($header -cnotmatch ('(?m)^name: ' + [regex]::Escape($name) + '\r?$')) { throw "Name mismatch: $name" }
        if ($header -notmatch '(?m)^description: \S.+\r?$') { throw "Missing description: $name" }
        $metadata = [IO.File]::ReadAllText((Join-Path $folder 'agents\openai.yaml'))
        if ($metadata -notmatch '(?m)^interface:\r?$' -or $metadata -notmatch '(?m)^  short_description: ".+"\r?$') { throw "Invalid UI metadata: $name" }
    }
}

function New-StudioBackup([string]$BackupRoot) {
    Assert-NoLink $BackupRoot
    $id = (Get-Date -Format 'yyyyMMdd-HHmmss-fff') + '-' + [Guid]::NewGuid().ToString('N').Substring(0,8)
    $backup = Get-SafeChild $BackupRoot $id
    New-Item -ItemType Directory -Path $backup -Force | Out-Null
    return $backup
}
