[CmdletBinding()]
param()
. (Join-Path $PSScriptRoot 'common.ps1')
Write-Output "Package: $StudioPackage $StudioVersion"
Write-Output "Declared Skills: $($StudioSkills.Count)"
Write-Output "PowerShell: $($PSVersionTable.PSVersion)"
$profilePath = [Environment]::GetFolderPath('UserProfile')
foreach ($relative in @('.agents/skills','.codex/skills')) {
    $folder = Join-Path $profilePath $relative
    Write-Output "Checking: $folder"
    if (Test-Path -LiteralPath $folder -PathType Container) {
        Get-ChildItem -LiteralPath $folder -Directory | Where-Object { $_.Name -in $StudioSkills } | Select-Object -ExpandProperty Name
    }
}
Write-Output 'Read-only diagnostic. Review personal paths before sharing its output.'
