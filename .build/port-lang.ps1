# =============================================================================
#  port-lang.ps1 - generate a language tree from the English source
#
#  Produces structurally correct <lang>/*.html carrying the English copy, ready
#  for a translator to work through. Everything mechanical is done here so no
#  translation agent ever has to reason about paths, canonicals or schema ids.
#
#  Per page it rewrites:
#    - <html lang>
#    - relative asset paths        assets/...        -> ../assets/...
#    - internal links              href="/services"  -> href="/es/services"
#    - canonical, og:url, and every language-dependent JSON-LD @id / url / item
#    - hreflang block, og:locale set, JSON-LD language fields
#    - header nav + language switcher
#    - cache-busting query strings
#
#  SAFETY: existing files are skipped unless -Force is given, so re-running
#  after translation has started cannot clobber translated copy.
#
#    pwsh .build/port-lang.ps1 -Trees es,sq -DryRun
#    pwsh .build/port-lang.ps1 -Trees es,sq
#    pwsh .build/port-lang.ps1 -Trees es -Only index,services -Force
# =============================================================================
[CmdletBinding()]
param(
  [switch]$DryRun,
  [switch]$Force,
  [string[]]$Trees = @('es', 'sq'),
  [string[]]$Only
)

$ErrorActionPreference = 'Stop'
. "$PSScriptRoot/lib-chrome.ps1"

$root = Split-Path -Parent $PSScriptRoot

# The Organization and WebSite nodes describe the business, not the page, and
# are deliberately shared across every language: the Italian tree already keeps
# them anchored at the English root. These literals are verified present exactly
# once in all 16 English pages, so protecting them by value is safe.
#
# ORDER MATTERS. The first entry consumes the WebSite node's own declaration
# while its @id is still intact; the bare "$SITE/#website" further down then
# catches every *reference* to it ("isPartOf": { "@id": ... }), which the
# Italian tree also keeps anchored to the English root.
#
# 'required' anchors must appear on every page; a missing one means the source
# drifted and the port would silently produce wrong schema, so it throws.
# The author anchor only appears on about and the article pages.
$SHARED = @(
  @{ required = $true;  text = "`"@id`": `"$SITE/#website`",`n        `"url`": `"$SITE/`"," },
  @{ required = $true;  text = "`"alternateName`": `"MarketingPro Digital Marketing Agency`",`n        `"url`": `"$SITE/`"," },
  # The Person node's own url stays on the English about page, same as its @id.
  # Must be matched before #organization is tokenised, or the anchor is gone.
  @{ required = $false; text = "`"worksFor`": { `"@id`": `"$SITE/#organization`" },`n        `"url`": `"$SITE/about`"," },
  @{ required = $true;  text = "$SITE/#organization" },
  @{ required = $true;  text = "$SITE/#logo" },
  @{ required = $true;  text = "$SITE/#website" },
  # The founder is one real person, not a per-language entity. The Italian tree
  # anchors all 21 references and the Person node itself at /about#author.
  @{ required = $false; text = "$SITE/about#author" },
  @{ required = $true;  text = "$SITE/assets/" }
)

function Convert-Page([string]$html, [string]$slug, [string]$lang) {
  $prefix = $LANGS[$lang].prefix          # e.g. /es

  # --- 1. park the language-independent JSON-LD so the sweep cannot touch it
  $tokens = @{}
  for ($i = 0; $i -lt $SHARED.Count; $i++) {
    $anchor = $SHARED[$i]
    if (-not $html.Contains($anchor.text)) {
      if ($anchor.required) { throw "required shared JSON-LD anchor $i missing ($slug)" }
      continue
    }
    $tok = "%%SHARED$i%%"
    $tokens[$tok] = $anchor.text
    $html = $html.Replace($anchor.text, $tok)
  }

  # --- 2. every remaining absolute site URL belongs to this page, so it moves
  #        into the language tree. Runs before the hreflang block is rebuilt,
  #        which is why mangling those links here does not matter.
  $html = $html.Replace("$SITE/", "$SITE$prefix/")

  # --- 3. restore
  foreach ($tok in $tokens.Keys) { $html = $html.Replace($tok, $tokens[$tok]) }

  # --- 4. internal root-absolute links. Every one of these in the English tree
  #        is an internal page link; there are no root-absolute asset paths.
  $html = [regex]::Replace($html, '(?<=\b(?:href)=")/', "$prefix/")

  # --- 5. relative asset paths: English sits at the root, every other tree is
  #        one directory deep. href, src and poster are the only attributes in
  #        this codebase that carry a relative asset path (there is no srcset).
  $ap = Get-AssetPrefix $lang
  $html = [regex]::Replace($html, '(?<=\b(?:href|src|poster|data-hero-video|data-src|srcset)=")(assets/)', "$ap`$1")
  $html = [regex]::Replace($html, '(?<=\b(?:href)=")(site\.webmanifest)', "$ap`$1")

  # --- 6. document language
  $html = [regex]::Replace($html, '<html lang="[^"]*"', "<html lang=""$lang""")

  # --- 7. head metadata and chrome, all rebuilt from the language tables
  $html = Set-HreflangBlock  $html $slug
  $html = Set-OgLocale       $html $lang $slug
  $html = Set-LanguageArrays $html $lang
  $html = Set-NavBlock       $html $slug $lang
  $html = Set-LandmarkLabels $html $lang
  $html = Set-ChromeStrings   $html $lang
  $html = Set-FooterNav       $html $lang
  $html = Set-RobotsMeta     $html $slug $lang
  $html = Set-AssetVersions  $html

  return $html
}

$slugs   = if ($Only) { $Only } else { $PAGES }
$written = 0; $skipped = 0

foreach ($lang in $Trees) {
  if ($lang -eq 'en') { throw 'en is the source tree, not a port target' }
  $dir = Join-Path $root $LANGS[$lang].dir
  if (-not (Test-Path $dir)) {
    if ($DryRun) { Write-Host "would create directory: $($LANGS[$lang].dir)/" -ForegroundColor Yellow }
    else { New-Item -ItemType Directory -Path $dir | Out-Null }
  }

  foreach ($slug in $slugs) {
    $src = Join-Path $root "$slug.html"
    if (-not (Test-Path $src)) { throw "English source missing: $slug.html" }
    $rel  = Get-PagePath $slug $lang
    $dest = Join-Path $root $rel

    if ((Test-Path $dest) -and -not $Force) {
      Write-Host "  skip (exists): $rel" -ForegroundColor DarkGray
      $skipped++
      continue
    }

    $out = Convert-Page (Read-HtmlFile $src) $slug $lang
    $written++
    if ($DryRun) {
      Write-Host "would write: $rel" -ForegroundColor Yellow
    } else {
      Write-HtmlFile $dest $out
      Write-Host "wrote: $rel" -ForegroundColor Green
    }
  }
}

Write-Host ''
Write-Host "written: $written   skipped (already exist): $skipped"
if ($DryRun) { Write-Host '(dry run - nothing written)' -ForegroundColor Yellow }
