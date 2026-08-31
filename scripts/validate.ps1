[CmdletBinding()]
param()
. (Join-Path $PSScriptRoot 'common.ps1')
$repoRoot = Split-Path $PSScriptRoot -Parent
Test-StudioSource $repoRoot
foreach ($file in @('README.md','NOTICE.md','VERSION','studio-manifest.json','INSTALL_WINDOWS.cmd','REPAIR_WINDOWS.cmd','UNINSTALL_WINDOWS.cmd')) {
    if (-not (Test-Path -LiteralPath (Join-Path $repoRoot $file) -PathType Leaf)) { throw "Missing file: $file" }
}
foreach ($script in Get-ChildItem -LiteralPath $PSScriptRoot -Filter '*.ps1') {
    $tokens = $null
    $parseErrors = $null
    $null = [Management.Automation.Language.Parser]::ParseFile($script.FullName, [ref]$tokens, [ref]$parseErrors)
    if ($parseErrors.Count) { throw "PowerShell syntax error: $($script.Name): $parseErrors" }
}
Write-Output "PASS: $($StudioSkills.Count) Skills, manifest, required files, UI metadata and PowerShell syntax."
