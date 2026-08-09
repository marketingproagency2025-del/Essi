# =============================================================================
#  fix-head.ps1 - bring every page's head up to four languages
#
#    - hreflang: 3 links -> 5 (en, it, es, sq, x-default)
#    - og:locale + og:locale:alternate: 1 alternate -> 3
#    - JSON-LD inLanguage / availableLanguage: ["en","it"] -> all four
#    - JSON-LD WebPage.inLanguage: set to the page's own language
#    - cache-busting query strings on style.css and main.js
#
#  hreflang has to be reciprocal, so this necessarily edits the 32 existing
#  English and Italian pages, not just the new trees.
#
#  Idempotent. Run with -DryRun to preview without writing.
# =============================================================================
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
    $new  = $html
    $new  = Set-HreflangBlock  $new $slug
    $new  = Set-OgLocale       $new $lang $slug
    $new  = Set-LanguageArrays $new $lang
    $new  = Set-RobotsMeta     $new $slug $lang
    $new  = Set-AssetVersions  $new

    if ($new -eq $html) { $same++; continue }
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
