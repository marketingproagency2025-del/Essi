# =============================================================================
#  gen-sitemap.ps1 - rebuild sitemap.xml from the pages themselves
#
#  The single source of truth for hreflang alternates is each page's own
#  <link rel="alternate"> tags. A sitemap that derives them cannot disagree with
#  the page it describes, which is the entire class of bug this replaces: with
#  64 pages x 5 alternates, a hand-maintained list is 320 lines nobody can
#  proofread.
#
#  Run with -Check to compare against the committed sitemap without writing.
#
#    pwsh .build/gen-sitemap.ps1
#    pwsh .build/gen-sitemap.ps1 -Check
# =============================================================================
[CmdletBinding()]
param(
  [switch]$Check,
  [string]$LastMod = (Get-Date -Format 'yyyy-MM-dd')
)

$ErrorActionPreference = 'Stop'
. "$PSScriptRoot/lib-chrome.ps1"

$root = Split-Path -Parent $PSScriptRoot

# Harvest a page's own alternates. The attributes are separated by arbitrary
# whitespace and may wrap a line, so this matches \s+ rather than a literal
# space. Order is preserved as authored.
function Get-PageAlternates([string]$html) {
  $rx = [regex]'<link\s+rel="alternate"\s+hreflang="([\w-]+)"\s+href="([^"]+)"'
  $out = @()
  foreach ($m in $rx.Matches($html)) {
    $out += [pscustomobject]@{ Lang = $m.Groups[1].Value; Href = $m.Groups[2].Value }
  }
  return $out
}

$lines = @(
  '<?xml version="1.0" encoding="UTF-8"?>'
  '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"'
  '        xmlns:xhtml="http://www.w3.org/1999/xhtml">'
)

$count = 0
foreach ($slug in $PAGES) {
  foreach ($lang in $LANGS.Keys) {
    $path = Join-Path $root (Get-PagePath $slug $lang)
    if (-not (Test-Path $path)) { continue }
    # Untranslated pages are noindex and stay out of the sitemap until a
    # translator has finished them. See Test-PageLive in lib-chrome.ps1.
    if (-not (Test-PageLive $slug $lang)) { continue }

    $html = Read-HtmlFile $path
    $alts = Get-PageAlternates $html
    if ($alts.Count -eq 0) { throw "no hreflang alternates found in $(Get-PagePath $slug $lang)" }

    $lines += '  <url>'
    $lines += "    <loc>$SITE$(Get-PageUrl $slug $lang)</loc>"
    foreach ($a in $alts) {
      $lines += "    <xhtml:link rel=""alternate"" hreflang=""$($a.Lang)"" href=""$($a.Href)""/>"
    }
    $lines += "    <lastmod>$LastMod</lastmod>"
    $lines += '    <changefreq>monthly</changefreq>'
    $lines += "    <priority>$($PRIORITY[$slug])</priority>"
    $lines += '  </url>'
    $count++
  }
}
$lines += '</urlset>'

$xml  = ($lines -join "`n") + "`n"
$dest = Join-Path $root 'sitemap.xml'

if ($Check) {
  $current = if (Test-Path $dest) { Read-HtmlFile $dest } else { '' }
  # lastmod is a timestamp, not structure: ignore it so the check stays stable
  # from one day to the next while still catching url/alternate drift.
  $strip = { param($s) [regex]::Replace($s, '<lastmod>[^<]*</lastmod>', '<lastmod/>') }
  if ((& $strip $current) -eq (& $strip $xml)) {
    Write-Host "sitemap.xml agrees with the pages ($count urls)" -ForegroundColor Green
    exit 0
  }
  Write-Host 'sitemap.xml DISAGREES with the pages. Run .build/gen-sitemap.ps1' -ForegroundColor Red
  exit 1
}

Write-HtmlFile $dest $xml
Write-Host "wrote sitemap.xml: $count urls, $(($count * 5)) alternates, lastmod $LastMod" -ForegroundColor Green
