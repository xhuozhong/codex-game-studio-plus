[CmdletBinding()]
param(
    [string]$RepoRoot,
    [Parameter(Mandatory = $true)][string]$ScratchParent
)

# Run with Windows PowerShell 5.1. All installs use Project scope in a new
# GUID directory beneath ScratchParent. Evidence is retained; nothing is deleted.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if (-not $RepoRoot) { $RepoRoot = Split-Path $PSScriptRoot -Parent }
$repo = (Resolve-Path -LiteralPath $RepoRoot).ProviderPath
if (-not (Test-Path -LiteralPath $ScratchParent -PathType Container)) {
    throw 'ScratchParent must be an existing filesystem directory.'
}
$scratch = (Resolve-Path -LiteralPath $ScratchParent).ProviderPath
$runRoot = Join-Path $scratch ('phaser-test-installer-' + [Guid]::NewGuid().ToString('N'))
$runRoot = [IO.Path]::GetFullPath($runRoot)
$scratchPrefix = [IO.Path]::GetFullPath($scratch).TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
if (-not $runRoot.StartsWith($scratchPrefix, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Test run directory must remain inside ScratchParent.'
}
$repoPrefix = [IO.Path]::GetFullPath($repo).TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
if ($runRoot.StartsWith($repoPrefix, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'ScratchParent must be outside the source repository to prevent recursive fixture copies.'
}
New-Item -ItemType Directory -Path $runRoot | Out-Null
$logRoot = Join-Path $runRoot 'logs'
New-Item -ItemType Directory -Path $logRoot | Out-Null
$windowsPowerShell = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
if (-not (Test-Path -LiteralPath $windowsPowerShell -PathType Leaf)) {
    throw 'These tests require Windows PowerShell 5.1.'
}
$manifest = Get-Content -LiteralPath (Join-Path $repo 'studio-manifest.json') -Raw | ConvertFrom-Json
$names = @($manifest.skills)
if ($names.Count -ne 15) { throw 'This release test expects the full 15-Skill Plus package.' }
$script:results = [Collections.Generic.List[object]]::new()
$script:invocationNumber = 0

function Assert-True([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw $Message }
}

function New-TestDirectory([string]$Relative) {
    $target = [IO.Path]::GetFullPath((Join-Path $runRoot $Relative))
    $prefix = $runRoot.TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
    Assert-True ($target.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) 'Test path escaped the run directory.'
    New-Item -ItemType Directory -Path $target -Force | Out-Null
    return $target
}

function ConvertTo-TestExtendedPath([string]$Path) {
    $full = [IO.Path]::GetFullPath($Path)
    if ($full.StartsWith('\\?\')) { return $full }
    if ($full.StartsWith('\\')) { return '\\?\UNC\' + $full.Substring(2) }
    return '\\?\' + $full
}

function ConvertFrom-TestExtendedPath([string]$Path) {
    if ($Path.StartsWith('\\?\UNC\')) { return '\\' + $Path.Substring(8) }
    if ($Path.StartsWith('\\?\')) { return $Path.Substring(4) }
    return $Path
}

function Get-TestHash([string]$File) {
    $stream = [IO.File]::OpenRead((ConvertTo-TestExtendedPath $File))
    $hasher = [Security.Cryptography.SHA256]::Create()
    try { return [BitConverter]::ToString($hasher.ComputeHash($stream)).Replace('-', '') }
    finally { $stream.Dispose(); $hasher.Dispose() }
}

function Get-TestEntries([string]$Folder) {
    # Native extended paths let the test inspect long backup paths on PS 5.1.
    # Reparse points are recorded without following them.
    $directory = New-Object IO.DirectoryInfo (ConvertTo-TestExtendedPath $Folder)
    foreach ($raw in @($directory.GetFileSystemInfos())) {
        $item = [pscustomobject]@{
            FullName = ConvertFrom-TestExtendedPath $raw.FullName
            Name = $raw.Name
            Attributes = $raw.Attributes
            PSIsContainer = ($raw -is [IO.DirectoryInfo])
        }
        $item
        if ($item.PSIsContainer -and -not ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
            Get-TestEntries $item.FullName
        }
    }
}

function Get-TreeSnapshot([string]$Folder) {
    if (-not [IO.Directory]::Exists((ConvertTo-TestExtendedPath $Folder))) { return '<missing>' }
    $prefixLength = $Folder.TrimEnd('\', '/').Length + 1
    $rows = foreach ($item in @(Get-TestEntries $Folder)) {
        $relative = $item.FullName.Substring($prefixLength)
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            'LINK|' + $relative + '|' + $item.Attributes
        } elseif ($item.PSIsContainer) {
            'DIR|' + $relative
        } else {
            'FILE|' + $relative + '|' + (Get-TestHash $item.FullName)
        }
    }
    return (@($rows | Sort-Object) -join "`n")
}

function Get-ContentMultiset([string]$Folder) {
    $rows = foreach ($item in @(Get-TestEntries $Folder)) {
        if (-not $item.PSIsContainer -and -not ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
            Get-TestHash $item.FullName
        }
    }
    return (@($rows | Sort-Object) -join "`n")
}

function Invoke-TestInstaller([string]$Package, [string]$Project, [string]$Operation, [switch]$Force) {
    Assert-True ($Operation -in @('install', 'uninstall')) 'Unsupported test operation.'
    $scriptPath = Join-Path $Package ('scripts\' + $Operation + '.ps1')
    Assert-True (-not $scriptPath.Contains('"') -and -not $Project.Contains('"')) 'Invalid quoted test path.'
    $arguments = '-NoProfile -NonInteractive -ExecutionPolicy Bypass -File "' + $scriptPath + '" -Scope Project -ProjectRoot "' + $Project + '"'
    if ($Force) { $arguments += ' -Force' }
    $start = New-Object Diagnostics.ProcessStartInfo
    $start.FileName = $windowsPowerShell
    $start.Arguments = $arguments
    $start.UseShellExecute = $false
    $start.CreateNoWindow = $true
    $start.RedirectStandardOutput = $true
    $start.RedirectStandardError = $true
    $process = New-Object Diagnostics.Process
    $process.StartInfo = $start
    $null = $process.Start()
    $stdout = $process.StandardOutput.ReadToEndAsync()
    $stderr = $process.StandardError.ReadToEndAsync()
    if (-not $process.WaitForExit(60000)) {
        $process.Kill()
        throw 'Installer test exceeded 60 seconds; only its child process was stopped.'
    }
    $output = $stdout.Result + $stderr.Result
    $exitCode = $process.ExitCode
    $process.Dispose()
    $script:invocationNumber++
    $log = Join-Path $logRoot ('{0:D2}-{1}.txt' -f $script:invocationNumber, $Operation)
    [IO.File]::WriteAllText($log, $output)
    return [pscustomobject]@{ ExitCode = $exitCode; Output = $output; Log = $log }
}

function Assert-Installed([string]$Package, [string]$Project) {
    foreach ($name in $names) {
        $source = Join-Path (Join-Path $Package 'skills') $name
        $target = Join-Path (Join-Path $Project '.agents\skills') $name
        Assert-True (Test-Path -LiteralPath $target -PathType Container) ('Skill was not installed: ' + $name)
        $marker = Get-Content -LiteralPath (Join-Path $target '.codex-game-studio.json') -Raw | ConvertFrom-Json
        Assert-True ($marker.package -ceq $manifest.package -and $marker.skill -ceq $name -and $marker.version -ceq $manifest.version) ('Incorrect ownership marker: ' + $name)
        foreach ($file in @(Get-TestEntries $source | Where-Object { -not $_.PSIsContainer })) {
            $relative = $file.FullName.Substring($source.Length + 1)
            $installedFile = Join-Path $target $relative
            Assert-True (Test-Path -LiteralPath $installedFile -PathType Leaf) ('Missing installed resource: ' + $name + '/' + $relative)
            Assert-True ((Get-TestHash $file.FullName) -ceq (Get-TestHash $installedFile)) ('Installed content differs: ' + $name + '/' + $relative)
        }
    }
}

function Copy-TestPackage([string]$Name) {
    $container = New-TestDirectory $Name
    $copy = Join-Path $container 'package'
    Copy-Item -LiteralPath $repo -Destination $copy -Recurse
    return $copy
}

function Test-Case([string]$Name, [scriptblock]$Body) {
    try {
        & $Body
        $script:results.Add([pscustomobject]@{ name = $Name; status = 'passed' })
        Write-Output ('PASS: ' + $Name)
    } catch {
        $script:results.Add([pscustomobject]@{ name = $Name; status = 'failed'; error = $_.Exception.Message })
        Write-Output ('FAIL: ' + $Name + ': ' + $_.Exception.Message)
    }
}

Test-Case 'all-15-install-conflict-repair-uninstall' {
    $project = New-TestDirectory 'lifecycle\project'
    $unrelated = New-TestDirectory 'lifecycle\project\.agents\skills\unrelated-skill'
    $unrelatedFile = Join-Path $unrelated 'keep.txt'
    [IO.File]::WriteAllText($unrelatedFile, 'unrelated skill must survive all operations')
    $install = Invoke-TestInstaller $repo $project 'install'
    Assert-True ($install.ExitCode -eq 0) ('Fresh install failed: ' + $install.Output)
    Assert-Installed $repo $project
    $beforeConflict = Get-TreeSnapshot $project
    $conflict = Invoke-TestInstaller $repo $project 'install'
    Assert-True ($conflict.ExitCode -ne 0) 'Default installation should refuse existing Skills.'
    Assert-True ((Get-TreeSnapshot $project) -ceq $beforeConflict) 'Conflict rejection changed project files or directories.'

    $custom = Join-Path (Join-Path (Join-Path $project '.agents\skills') $names[0]) 'custom-user-note.txt'
    [IO.File]::WriteAllText($custom, 'custom local content must be preserved in a backup')
    $customHash = Get-TestHash $custom
    $repair = Invoke-TestInstaller $repo $project 'install' -Force
    Assert-True ($repair.ExitCode -eq 0) ('Force repair failed: ' + $repair.Output)
    Assert-Installed $repo $project
    $backups = Join-Path $project ('.agents\skill-backups\' + $manifest.package)
    $savedCustom = @(Get-TestEntries $backups | Where-Object { -not $_.PSIsContainer -and $_.Name -eq 'custom-user-note.txt' })
    Assert-True ($savedCustom.Count -eq 1) 'Force repair did not retain the custom file once in backup.'
    Assert-True ((Get-TestHash $savedCustom[0].FullName) -ceq $customHash) 'Backed-up custom content was modified.'
    Assert-True (-not (Test-Path -LiteralPath $custom)) 'Freshly installed skill unexpectedly contains the old custom file.'

    $contentBeforeUninstall = Get-ContentMultiset $project
    $uninstall = Invoke-TestInstaller $repo $project 'uninstall'
    Assert-True ($uninstall.ExitCode -eq 0) ('Uninstall failed: ' + $uninstall.Output)
    foreach ($name in $names) {
        Assert-True (-not (Test-Path -LiteralPath (Join-Path (Join-Path $project '.agents\skills') $name))) ('Uninstall left a managed Skill active: ' + $name)
    }
    Assert-True ((Get-ContentMultiset $project) -ceq $contentBeforeUninstall) 'Uninstall deleted, duplicated or changed file content instead of moving it.'
    Assert-True ([IO.File]::ReadAllText($unrelatedFile) -ceq 'unrelated skill must survive all operations') 'An unrelated Skill was changed.'
}

Test-Case 'wrong-marker-prevents-all-moves' {
    $project = New-TestDirectory 'wrong-marker\project'
    $install = Invoke-TestInstaller $repo $project 'install'
    Assert-True ($install.ExitCode -eq 0) ('Fixture installation failed: ' + $install.Output)
    # Tamper with the last entry, after many otherwise valid candidates.
    $markerPath = Join-Path (Join-Path (Join-Path $project '.agents\skills') $names[-1]) '.codex-game-studio.json'
    $marker = Get-Content -LiteralPath $markerPath -Raw | ConvertFrom-Json
    $marker.package = 'different-package-owner'
    $marker | ConvertTo-Json | Set-Content -LiteralPath $markerPath -Encoding UTF8
    $before = Get-TreeSnapshot $project
    $uninstall = Invoke-TestInstaller $repo $project 'uninstall'
    Assert-True ($uninstall.ExitCode -ne 0) 'Uninstall accepted a wrong package owner.'
    Assert-True ((Get-TreeSnapshot $project) -ceq $before) 'A wrong marker did not prevent all moves.'
}

Test-Case 'unmarked-skill-prevents-all-moves' {
    $project = New-TestDirectory 'unmarked\project'
    $install = Invoke-TestInstaller $repo $project 'install'
    Assert-True ($install.ExitCode -eq 0) ('Fixture installation failed: ' + $install.Output)
    $skill = Join-Path (Join-Path $project '.agents\skills') $names[-1]
    # Rename inside this verified disposable project, rather than deleting.
    $markerPath = Join-Path $skill '.codex-game-studio.json'
    Move-Item -LiteralPath $markerPath -Destination (Join-Path $skill 'saved-marker.json')
    $before = Get-TreeSnapshot $project
    $uninstall = Invoke-TestInstaller $repo $project 'uninstall'
    Assert-True ($uninstall.ExitCode -ne 0) 'Uninstall accepted an unmarked Skill.'
    Assert-True ((Get-TreeSnapshot $project) -ceq $before) 'An unmarked Skill did not prevent all moves.'
}

Test-Case 'nonexistent-project-is-not-created' {
    $container = New-TestDirectory 'missing-project'
    $missing = Join-Path $container 'does-not-exist'
    $before = Get-TreeSnapshot $container
    $install = Invoke-TestInstaller $repo $missing 'install'
    Assert-True ($install.ExitCode -ne 0) 'Installer accepted a nonexistent project.'
    Assert-True ((Get-TreeSnapshot $container) -ceq $before) 'Nonexistent-project rejection created paths.'
}

foreach ($badCase in @('traversal', 'absolute', 'duplicate', 'non-string')) {
    Test-Case ('manifest-rejects-' + $badCase) {
        $copy = Copy-TestPackage ('manifest-' + $badCase)
        $manifestPath = Join-Path $copy 'studio-manifest.json'
        $badManifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
        switch ($badCase) {
            'traversal' { $badManifest.skills[1] = '../escape' }
            'absolute' { $badManifest.skills[1] = 'C:\outside-skill' }
            'duplicate' { $badManifest.skills[1] = $badManifest.skills[0] }
            'non-string' { $badManifest.skills[1] = 42 }
        }
        $badManifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $manifestPath -Encoding UTF8
        $project = New-TestDirectory ('manifest-' + $badCase + '\project')
        $beforeProject = Get-TreeSnapshot $project
        $beforePackage = Get-TreeSnapshot $copy
        $install = Invoke-TestInstaller $copy $project 'install'
        Assert-True ($install.ExitCode -ne 0) ('Installer accepted invalid manifest: ' + $badCase)
        Assert-True ((Get-TreeSnapshot $project) -ceq $beforeProject) 'Invalid manifest changed the installation target.'
        Assert-True ((Get-TreeSnapshot $copy) -ceq $beforePackage) 'Invalid manifest changed the source package.'
    }
}

Test-Case 'unlisted-source-directory-is-rejected' {
    $copy = Copy-TestPackage 'extra-source'
    New-Item -ItemType Directory -Path (Join-Path $copy 'skills\unlisted-expert') | Out-Null
    $project = New-TestDirectory 'extra-source\project'
    $before = Get-TreeSnapshot $project
    $install = Invoke-TestInstaller $copy $project 'install'
    Assert-True ($install.ExitCode -ne 0) 'Installer accepted an unlisted source directory.'
    Assert-True ((Get-TreeSnapshot $project) -ceq $before) 'Extra source directory caused target changes.'
}

Test-Case 'source-descendant-junction-is-rejected' {
    $copy = Copy-TestPackage 'source-junction'
    $external = New-TestDirectory 'source-junction\external-data'
    [IO.File]::WriteAllText((Join-Path $external 'keep.txt'), 'external data remains untouched')
    $junction = Join-Path (Join-Path (Join-Path $copy 'skills') $names[0]) 'external-link'
    New-Item -ItemType Junction -Path $junction -Target $external | Out-Null
    $project = New-TestDirectory 'source-junction\project'
    $beforeTarget = Get-TreeSnapshot $project
    $beforeExternal = Get-TreeSnapshot $external
    $install = Invoke-TestInstaller $copy $project 'install'
    Assert-True ($install.ExitCode -ne 0) 'Installer followed a junction in the source Skill.'
    Assert-True ((Get-TreeSnapshot $project) -ceq $beforeTarget) 'Source junction caused target writes.'
    Assert-True ((Get-TreeSnapshot $external) -ceq $beforeExternal) 'Source junction changed its target.'
}

Test-Case 'project-ancestor-junction-is-rejected' {
    $container = New-TestDirectory 'project-junction'
    $realParent = New-TestDirectory 'project-junction\real-parent'
    $realProject = New-TestDirectory 'project-junction\real-parent\project'
    $alias = Join-Path $container 'alias'
    New-Item -ItemType Junction -Path $alias -Target $realParent | Out-Null
    $projectThroughLink = Join-Path $alias 'project'
    $before = Get-TreeSnapshot $realParent
    $install = Invoke-TestInstaller $repo $projectThroughLink 'install'
    Assert-True ($install.ExitCode -ne 0) 'Installer accepted a project reached through a junction ancestor.'
    Assert-True ((Get-TreeSnapshot $realParent) -ceq $before) 'Project ancestor junction caused installation writes.'
}

Test-Case 'overlong-installed-file-path-is-rejected-before-writes' {
    $container = New-TestDirectory 'long-destination'
    $paddingLength = 215 - $container.Length - 1
    Assert-True ($paddingLength -gt 0 -and $paddingLength -lt 240) 'Scratch path does not fit the long-path test fixture.'
    $project = Join-Path $container ('p' * $paddingLength)
    [void][IO.Directory]::CreateDirectory((ConvertTo-TestExtendedPath $project))
    $before = Get-TreeSnapshot $project
    $install = Invoke-TestInstaller $repo $project 'install'
    Assert-True ($install.ExitCode -ne 0) 'Installer accepted destination resources beyond its documented path limit.'
    Assert-True ((Get-TreeSnapshot $project) -ceq $before) 'Long-path rejection happened after modifying the project.'
}

Test-Case 'force-rejects-nondirectory-skill-conflict-before-writes' {
    $project = New-TestDirectory 'file-conflict\project'
    $skills = New-TestDirectory 'file-conflict\project\.agents\skills'
    [IO.File]::WriteAllText((Join-Path $skills $names[-1]), 'not a skill directory; preserve this file')
    $before = Get-TreeSnapshot $project
    $install = Invoke-TestInstaller $repo $project 'install' -Force
    Assert-True ($install.ExitCode -ne 0) 'Force install accepted a file in place of a Skill directory.'
    Assert-True ((Get-TreeSnapshot $project) -ceq $before) 'A file conflict caused project changes.'
}

$report = [pscustomobject]@{
    package = $manifest.package
    version = $manifest.version
    expected_skills = $names.Count
    host_powershell = $PSVersionTable.PSVersion.ToString()
    installer_host = $windowsPowerShell
    scope = 'Project only'
    run_directory = $runRoot
    cases = @($script:results.ToArray())
    passed = @($script:results | Where-Object { $_.status -eq 'passed' }).Count
    failed = @($script:results | Where-Object { $_.status -eq 'failed' }).Count
    limitations = @('No User-scope installation', 'No injected mid-copy or mid-move rollback failure', 'No concurrent filesystem race testing', 'No permanent deletion or cleanup of test evidence')
}
$report | ConvertTo-Json -Depth 7 | Set-Content -LiteralPath (Join-Path $runRoot 'results.json') -Encoding UTF8
Write-Output ('Evidence retained in: ' + $runRoot)
Write-Output ('Results: {0} passed, {1} failed.' -f $report.passed, $report.failed)
if ($report.failed -gt 0) { exit 1 }
