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
  [switch]$Check
)

$ErrorActionPreference = 'Stop'
. "$PSScriptRoot/lib-chrome.ps1"

$root = Split-Path -Parent $PSScriptRoot

# Real per-page modification date, read from the page itself.
#
# THIS USED TO ASK GIT, AND GIT LIED. Not through any fault of its own: two
# site-wide sweeps (a CSS bezel fix touching 114 files, an entity fix touching
# 76) between them covered every HTML file in the repo, so `git log -1` reported
# the same committer date for all 129 of them. The sitemap duly told Google that
# 128 URLs had all changed on the same day, and it would have done so again
# after the next global fix. In a repo whose four-language chrome is generated,
# global fixes are normal, so the git approach was structurally doomed rather
# than unlucky.
#
# Worse, it contradicted the pages. 64 URLs carried a lastmod that disagreed
# with the dateModified the same page published in its own JSON-LD, and
# feed.xml - built from the same <time> elements this now reads - was already
# carrying twelve honest dates while the sitemap carried one.
#
# The page is the authority. Order of preference:
#   1. JSON-LD dateModified, which is the field that actually means this.
#   2. <time datetime>, the visible publication date. For a page never revised
#      since publication, lastmod == datePublished is true, not an approximation.
#   3. Nothing. lastmod is optional, and Google is explicit that an omitted date
#      beats an inaccurate one; a site caught lying about it has the signal
#      discounted everywhere. Twelve slugs publish no date (portfolio, about,
#      contact and the eight service pages) and simply get no lastmod.
function Get-PageDate([string]$html) {
  $m = [regex]::Match($html, '"dateModified":\s*"(\d{4}-\d{2}-\d{2})')
  if ($m.Success) { return $m.Groups[1].Value }
  $m = [regex]::Match($html, '<time datetime="(\d{4}-\d{2}-\d{2})')
  if ($m.Success) { return $m.Groups[1].Value }
  return $null
}

# The blog index is the one exception to rule 3. It publishes no date of its own
# but it genuinely does change whenever a post lands, so it inherits the newest
# date among the posts it lists. That is a fact about the page, not a guess.
$script:BlogIndexDate = @{}
foreach ($lang in $LANGS.Keys) {
  $newest = $null
  foreach ($slug in $PAGES) {
    if ($slug -notmatch '^(blog-|article-)') { continue }
    $p = Join-Path $root (Get-PagePath $slug $lang)
    if (-not (Test-Path $p)) { continue }
    if (-not (Test-PageLive $slug $lang)) { continue }
    $d = Get-PageDate (Read-HtmlFile $p)
    if ($d -and ((-not $newest) -or ($d -gt $newest))) { $newest = $d }
  }
  $script:BlogIndexDate[$lang] = $newest
}

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
$emitted = @()
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
    $lm = if ($slug -eq 'blog') { $script:BlogIndexDate[$lang] } else { Get-PageDate $html }
    if ($lm) { $lines += "    <lastmod>$lm</lastmod>"; $emitted += $lm }
    # changefreq is gone. 128 identical <changefreq>monthly</changefreq> were
    # ignored by Google and false on their face: article-1 has not changed since
    # April. priority stays - also ignored, but at least true.
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
  # lastmod used to be stripped before comparing, because it came from the clock
  # and drifted daily. It now comes from the page content, so it is deterministic
  # and is compared like everything else. That strip is why a sitemap with 128
  # identical dates passed this check for as long as it did.
  if ($current -eq $xml) {
    Write-Host "sitemap.xml agrees with the pages ($count urls)" -ForegroundColor Green
    exit 0
  }
  Write-Host 'sitemap.xml DISAGREES with the pages. Run .build/gen-sitemap.ps1' -ForegroundColor Red
  exit 1
}

Write-HtmlFile $dest $xml
# Counted, not multiplied. This printed $count * 5, which was right only while
# every tree was live for every slug; the first held-back page would have made it
# a confident lie. $dates is wrapped in @() because Sort-Object -Unique returns a
# scalar, not an array, when there is exactly one distinct value.
$alts = @($lines | Where-Object { $_ -match '<xhtml:link' }).Count
$dates = @($emitted | Sort-Object -Unique)
$span = if ($dates.Count) { "$($dates[0]) to $($dates[-1])" } else { 'none' }
$nolm = $count - $emitted.Count
Write-Host "wrote sitemap.xml: $count urls, $alts alternates, $($dates.Count) distinct lastmod dates ($span), $nolm urls with no lastmod" -ForegroundColor Green
