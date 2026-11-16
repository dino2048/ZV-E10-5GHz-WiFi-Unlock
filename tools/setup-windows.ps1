# Prepare this project with the companion zv-e10-toolkit checkout.
# This script never opens a camera.
param(
    [string]$Toolkit,
    [string]$Python = 'py',
    [string]$Proxy = ''
)
$ErrorActionPreference = 'Stop'
$project = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
if (-not $Toolkit) {
    $Toolkit = Join-Path (Split-Path $project) 'zv-e10-toolkit'
}
$Toolkit = (Resolve-Path -LiteralPath $Toolkit).Path
$setup = Join-Path $Toolkit 'linux/scripts/setup-windows.ps1'
if (-not (Test-Path -LiteralPath $setup)) {
    throw 'The companion toolkit lacks linux/scripts/setup-windows.ps1; use the matching Windows-capable toolkit checkout'
}

$setupArgs = @{ Python = $Python }
if ($Proxy) { $setupArgs.Proxy = $Proxy }
& $setup @setupArgs
if (-not $?) { throw 'Toolkit Windows setup failed' }
$wifiPython = Join-Path $Toolkit 'linux/.venv/Scripts/python.exe'
$env:ZVE10_TOOLKIT = $Toolkit
& $wifiPython -B (Join-Path $project 'tools/wifi.py') --help
if ($LASTEXITCODE -ne 0) { throw 'Wi-Fi tool import check failed' }

Write-Host "ZVE10_TOOLKIT=$Toolkit"
Write-Host "WIFI_PYTHON=$wifiPython"
