# =============================================================================
#  fix-nav.ps1 - rebuild the header nav + language switcher in every page
#
#  Fixes three shipped bugs at once:
#    1. the "(EN)" / "(IT)" debug suffixes on all 5 nav links
#    2. the Italian nav, which was never translated (Services -> Servizi)
#    3. About missing from the header nav (it was only ever in the footer)
#
#  and replaces the hardcoded 2-item language switcher with a 1-item no-JS
#  fallback that main.js expands from the page's own hreflang links.
#
#  Idempotent. Run with -DryRun to preview without writing.
#
#    pwsh .build/fix-nav.ps1 -DryRun
#    pwsh .build/fix-nav.ps1
# =============================================================================
#  NOTE: do not name a parameter $Langs here. PowerShell variables are
#  case-insensitive, so $Langs would silently shadow the $LANGS table that
#  lib-chrome.ps1 defines, and every lookup would return null.
[CmdletBinding()]
param(
  [switch]$DryRun,
  [string[]]$Trees = @('en', 'it')
)

$ErrorActionPreference = 'Stop'
. "$PSScriptRoot/lib-chrome.ps1"

$root = Split-Path -Parent $PSScriptRoot
$changed = 0
$same    = 0

foreach ($lang in $Trees) {
  foreach ($slug in $PAGES) {
    $rel  = Get-PagePath $slug $lang
    $path = Join-Path $root $rel
    if (-not (Test-Path $path)) { Write-Host "  skip (absent): $rel"; continue }

    $html = Read-HtmlFile $path
    $new  = Set-NavBlock $html $slug $lang

    if ($new -eq $html) {
      $same++
      continue
    }
    $changed++
    if ($DryRun) {
      Write-Host "would update: $rel" -ForegroundColor Yellow
    } else {
      Write-HtmlFile $path $new
      Write-Host "updated: $rel" -ForegroundColor Green
    }
  }
}

Write-Host ''
Write-Host "changed: $changed   already correct: $same"
if ($DryRun) { Write-Host '(dry run - nothing written)' -ForegroundColor Yellow }
