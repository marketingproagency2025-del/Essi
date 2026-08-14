# =============================================================================
#  verify-langs.ps1 - the gate
#
#  Re-derives everything it checks from the files on disk rather than trusting
#  the porter that wrote them, so a bug in port-lang.ps1 cannot talk this into
#  passing. Nothing is committed unless this ends ALL PASSES CLEAN.
#
#    pwsh .build/verify-langs.ps1
#
#  Exit code 0 = clean, 1 = at least one failure.
# =============================================================================
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
. "$PSScriptRoot/lib-chrome.ps1"

$root     = Split-Path -Parent $PSScriptRoot
$failures = @()
$checkNo  = 0

function Start-Check([string]$name) {
  $script:checkNo++
  Write-Host ("[{0,2}] {1}" -f $script:checkNo, $name) -ForegroundColor Cyan
}
function Add-Failure([string]$msg) {
  $script:failures += $msg
  Write-Host "     FAIL  $msg" -ForegroundColor Red
}
function Write-Ok([string]$msg) { Write-Host "     ok    $msg" -ForegroundColor DarkGray }

# Real pixel dimensions for every image under assets/, keyed by repo-relative
# path. Produced by .build/imgsize.py, which uses Pillow.
#
# An earlier version parsed PNG IHDR and JPEG SOF markers in PowerShell and was
# simply wrong - logo.png came back 119x77 against a real 375x77, and the
# article heroes 176x208 against 1200x720. Shelling out to the thing that gets
# it right beats debugging byte-walking in a shell language, and it still
# re-derives from the files rather than trusting a checked-in manifest.
$script:ImgDims = @{}
$dimOut = & python (Join-Path $PSScriptRoot 'imgsize.py') 2>&1
if ($LASTEXITCODE -ne 0) {
  Write-Host "     WARN  could not read image dimensions: $dimOut" -ForegroundColor Yellow
} else {
  foreach ($line in $dimOut) {
    $parts = "$line" -split "`t"
    if ($parts.Count -eq 3) {
      $script:ImgDims[$parts[0]] = @{ W = [int]$parts[1]; H = [int]$parts[2] }
    }
  }
}

function Get-ImageSize([string]$repoRelative) {
  $key = $repoRelative -replace '\\', '/'
  if ($script:ImgDims.ContainsKey($key)) { return $script:ImgDims[$key] }
  return $null
}

# Map an absolute site URL back to the file that serves it.
function Convert-UrlToPath([string]$url) {
  if (-not $url.StartsWith($SITE)) { return $null }
  $p = $url.Substring($SITE.Length)
  $p = ($p -split '[#?]')[0]
  if ($p -eq '' -or $p -eq '/') { return 'index.html' }
  $p = $p.TrimStart('/')
  if ($p.EndsWith('/')) { return ($p + 'index.html') }
  return "$p.html"
}

# Load every page once. Named $docs, not $pages: PowerShell variable names are
# case-insensitive, so $pages would shadow the $PAGES slug list from the library.
$docs = @{}
foreach ($lang in $LANGS.Keys) {
  foreach ($slug in $PAGES) {
    $rel  = Get-PagePath $slug $lang
    $full = Join-Path $root $rel
    if (Test-Path $full) {
      $docs[$rel] = @{ Lang = $lang; Slug = $slug; Rel = $rel; Full = $full
                        Html = [System.IO.File]::ReadAllText($full) }
    }
  }
}

$status = Get-Content (Join-Path $PSScriptRoot 'translation-status.json') -Raw | ConvertFrom-Json

# -----------------------------------------------------------------------------
Start-Check "Parity: $($PAGES.Count) slugs x $($LANGS.Count) trees, no orphans"
$expected = @()
foreach ($lang in $LANGS.Keys) { foreach ($slug in $PAGES) { $expected += (Get-PagePath $slug $lang) } }
foreach ($rel in $expected) {
  if (-not $docs.ContainsKey($rel)) { Add-Failure "missing page: $rel" }
}
$onDisk = @()
foreach ($lang in $LANGS.Keys) {
  $dir = if ($LANGS[$lang].dir -eq '') { $root } else { Join-Path $root $LANGS[$lang].dir }
  if (Test-Path $dir) {
    Get-ChildItem -Path $dir -Filter '*.html' -File | ForEach-Object {
      $r = if ($LANGS[$lang].dir -eq '') { $_.Name } else { "$($LANGS[$lang].dir)/$($_.Name)" }
      $onDisk += $r
    }
  }
}
foreach ($r in ($onDisk | Sort-Object -Unique)) {
  if ($expected -notcontains $r) { Add-Failure "orphan page not in the slug list: $r" }
}
Write-Ok "$($expected.Count) expected, $($docs.Count) found"

# -----------------------------------------------------------------------------
Start-Check 'hreflang: live languages only, reciprocal, resolving to real files'
$altRx = [regex]'<link\s+rel="alternate"\s+hreflang="([\w-]+)"\s+href="([^"]+)"'
$altSets = @{}
foreach ($p in $docs.Values) {
  $set = [ordered]@{}
  foreach ($m in $altRx.Matches($p.Html)) { $set[$m.Groups[1].Value] = $m.Groups[2].Value }
  $altSets[$p.Rel] = $set
  # An untranslated page is not advertised anywhere, so the set lists only the
  # languages actually translated for this slug (en and it are always live).
  $want = @(Get-LiveLangs $p.Slug) + 'x-default'
  if (($set.Keys -join ',') -ne ($want -join ',')) {
    Add-Failure "$($p.Rel): alternates are [$($set.Keys -join ',')], expected [$($want -join ',')]"
  }
}
foreach ($p in $docs.Values) {
  foreach ($code in $altSets[$p.Rel].Keys) {
    $target = Convert-UrlToPath $altSets[$p.Rel][$code]
    if (-not $target) { Add-Failure "$($p.Rel): off-site hreflang target $($altSets[$p.Rel][$code])"; continue }
    if (-not $docs.ContainsKey($target)) { Add-Failure "$($p.Rel): hreflang $code points at missing $target"; continue }
    # Reciprocity: the page it points at must declare the identical set.
    $a = ($altSets[$p.Rel].GetEnumerator()  | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join '|'
    $b = ($altSets[$target].GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join '|'
    if ($a -ne $b) { Add-Failure "$($p.Rel): hreflang set differs from its $code alternate $target" }
  }
}
$altTotal = ($docs.Values | ForEach-Object { $altSets[$_.Rel].Count } | Measure-Object -Sum).Sum
Write-Ok "$($docs.Count) pages, $altTotal alternate links checked both ways"

# -----------------------------------------------------------------------------
Start-Check 'Staged rollout: untranslated pages are noindex and out of the sitemap'
$sitemapXml = Read-HtmlFile (Join-Path $root 'sitemap.xml')
$held = 0; $live = 0
foreach ($p in $docs.Values) {
  $isLive  = Test-PageLive $p.Slug $p.Lang
  $m       = [regex]::Match($p.Html, '<meta name="robots" content="([^"]+)"')
  if (-not $m.Success) { Add-Failure "$($p.Rel): no robots meta"; continue }
  $robots  = $m.Groups[1].Value
  $inMap   = $sitemapXml.Contains("<loc>$SITE$(Get-PageUrl $p.Slug $p.Lang)</loc>")

  if ($isLive) {
    $live++
    if ($robots -ne $ROBOTS_LIVE) { Add-Failure "$($p.Rel): live page but robots is '$robots'" }
    if (-not $inMap)              { Add-Failure "$($p.Rel): live page missing from sitemap.xml" }
  } else {
    $held++
    if ($robots -ne $ROBOTS_HELD) { Add-Failure "$($p.Rel): untranslated but robots is '$robots', expected '$ROBOTS_HELD'" }
    if ($inMap)                   { Add-Failure "$($p.Rel): untranslated but listed in sitemap.xml" }
    # Nothing may advertise a page that is not ready.
    foreach ($q in $docs.Values) {
      if ($altSets[$q.Rel].Values -contains "$SITE$(Get-PageUrl $p.Slug $p.Lang)") {
        Add-Failure "$($q.Rel): hreflang advertises the untranslated $($p.Rel)"
      }
    }
  }
}
Write-Ok "$live live, $held held back as noindex"

# -----------------------------------------------------------------------------
Start-Check 'Canonical: every page self-canonicalises'
foreach ($p in $docs.Values) {
  $m = [regex]::Match($p.Html, '<link rel="canonical" href="([^"]+)"')
  if (-not $m.Success) { Add-Failure "$($p.Rel): no canonical"; continue }
  $want = "$SITE$(Get-PageUrl $p.Slug $p.Lang)"
  if ($m.Groups[1].Value -ne $want) {
    Add-Failure "$($p.Rel): canonical is $($m.Groups[1].Value), expected $want"
  }
}
Write-Ok 'all canonicals point at their own URL'

# -----------------------------------------------------------------------------
Start-Check 'lang attribute matches the directory'
foreach ($p in $docs.Values) {
  $m = [regex]::Match($p.Html, '<html lang="([^"]+)"')
  if (-not $m.Success) { Add-Failure "$($p.Rel): no <html lang>"; continue }
  if ($m.Groups[1].Value -ne $p.Lang) {
    Add-Failure "$($p.Rel): lang is '$($m.Groups[1].Value)', expected '$($p.Lang)'"
  }
}
Write-Ok 'all <html lang> values correct'

# -----------------------------------------------------------------------------
Start-Check 'Local asset references resolve on disk'
$refRx = [regex]'(?:href|src|poster|data-hero-video|data-src|srcset)="([^":#][^":]*)"'
$missing = @{}
foreach ($p in $docs.Values) {
  $baseDir = Split-Path -Parent $p.Full
  foreach ($m in $refRx.Matches($p.Html)) {
    $v = $m.Groups[1].Value
    if ($v -match '^(https?:|mailto:|tel:|//|data:)') { continue }
    if ($v.StartsWith('/')) { continue }   # internal page links, checked below
    $clean  = ($v -split '[#?]')[0]
    if ($clean -eq '') { continue }
    $target = [System.IO.Path]::GetFullPath((Join-Path $baseDir $clean))
    if (-not (Test-Path $target)) { $missing["$($p.Rel) -> $v"] = $true }
  }
}
foreach ($k in $missing.Keys) { Add-Failure "unresolved asset: $k" }
Write-Ok 'every relative href/src/poster/srcset resolves'

# -----------------------------------------------------------------------------
Start-Check 'Internal root-absolute links stay inside their own language tree'
$linkRx = [regex]'href="(/[^"]*)"'
foreach ($p in $docs.Values) {
  $prefix = $LANGS[$p.Lang].prefix
  foreach ($m in $linkRx.Matches($p.Html)) {
    $href   = ($m.Groups[1].Value -split '#')[0]
    if ($href -eq '') { continue }
    $expect = if ($prefix -eq '') { '/' } else { "$prefix/" }
    if (-not $href.StartsWith($expect)) {
      Add-Failure "$($p.Rel): link $($m.Groups[1].Value) leaves the $($p.Lang) tree"
      continue
    }
    $target = Convert-UrlToPath "$SITE$href"
    if ($target -and -not $docs.ContainsKey($target)) {
      Add-Failure "$($p.Rel): link $($m.Groups[1].Value) has no page ($target)"
    }
  }
}
Write-Ok 'all internal links resolve within their tree'

# -----------------------------------------------------------------------------
Start-Check 'og:locale is the page locale, with the other three as alternates'
foreach ($p in $docs.Values) {
  $m = [regex]::Match($p.Html, '<meta property="og:locale" content="([^"]+)"')
  if (-not $m.Success) { Add-Failure "$($p.Rel): no og:locale"; continue }
  if ($m.Groups[1].Value -ne $LANGS[$p.Lang].locale) {
    Add-Failure "$($p.Rel): og:locale $($m.Groups[1].Value), expected $($LANGS[$p.Lang].locale)"
  }
  $alts = [regex]::Matches($p.Html, '<meta property="og:locale:alternate" content="([^"]+)"') |
          ForEach-Object { $_.Groups[1].Value }
  # Must agree with the hreflang set: only languages actually live for this slug.
  $want = @(Get-LiveLangs $p.Slug | Where-Object { $_ -ne $p.Lang } | ForEach-Object { $LANGS[$_].locale })
  if (($alts -join ',') -ne ($want -join ',')) {
    Add-Failure "$($p.Rel): og:locale:alternate [$($alts -join ',')], expected [$($want -join ',')]"
  }
}
Write-Ok 'og:locale sets correct'

# -----------------------------------------------------------------------------
Start-Check 'JSON-LD parses, declares four languages, and namespaces ids correctly'
$siteLangs = '["' + ((Get-LiveSiteLangs) -join '", "') + '"]'   # site is published in
$teamLangs = '["' + (($LANGS.Keys) -join '", "') + '"]'         # team converses in
foreach ($p in $docs.Values) {
  $blocks = [regex]::Matches($p.Html, '(?s)<script type="application/ld\+json">(.*?)</script>')
  if ($blocks.Count -eq 0) { Add-Failure "$($p.Rel): no JSON-LD"; continue }
  foreach ($b in $blocks) {
    try { $null = $b.Groups[1].Value | ConvertFrom-Json }
    catch { Add-Failure "$($p.Rel): JSON-LD does not parse - $($_.Exception.Message)" }
  }
  foreach ($m in [regex]::Matches($p.Html, '"inLanguage":\s*(\[[^\]]*\])')) {
    if ($m.Groups[1].Value -ne $siteLangs) {
      Add-Failure "$($p.Rel): WebSite inLanguage is $($m.Groups[1].Value), expected $siteLangs"
    }
  }
  foreach ($m in [regex]::Matches($p.Html, '"availableLanguage":\s*(\[[^\]]*\])')) {
    if ($m.Groups[1].Value -ne $teamLangs) {
      Add-Failure "$($p.Rel): availableLanguage is $($m.Groups[1].Value), expected $teamLangs"
    }
  }
  foreach ($m in [regex]::Matches($p.Html, '"inLanguage":\s*"([a-z-]+)"')) {
    if ($m.Groups[1].Value -ne $p.Lang) {
      Add-Failure "$($p.Rel): WebPage inLanguage '$($m.Groups[1].Value)', expected '$($p.Lang)'"
    }
  }
  # The page's own WebPage/CollectionPage/etc node must live in its own tree.
  foreach ($m in [regex]::Matches($p.Html, '"@id":\s*"([^"]*#webpage)"')) {
    $want = "$SITE$(Get-PageUrl $p.Slug $p.Lang)#webpage"
    if ($m.Groups[1].Value -ne $want) {
      Add-Failure "$($p.Rel): #webpage id is $($m.Groups[1].Value), expected $want"
    }
  }
  # Shared real-world entities stay anchored to the English root in every tree,
  # matching what the Italian tree has always done.
  foreach ($shared in @('#organization', '#logo', '#website')) {
    foreach ($m in [regex]::Matches($p.Html, "`"@id`":\s*`"([^`"]*$shared)`"")) {
      if ($m.Groups[1].Value -ne "$SITE/$shared") {
        Add-Failure "$($p.Rel): shared entity $shared is $($m.Groups[1].Value), expected $SITE/$shared"
      }
    }
  }
}
Write-Ok 'JSON-LD valid and correctly scoped'

# -----------------------------------------------------------------------------
Start-Check 'FAQ text agrees between JSON-LD and the visible <details>'
foreach ($p in $docs.Values) {
  $q = [regex]::Matches($p.Html, '"@type":\s*"Question"').Count
  $d = [regex]::Matches($p.Html, '<details').Count
  if ($q -ne $d) {
    Add-Failure "$($p.Rel): $q JSON-LD Questions but $d <details> blocks"
  }
}
Write-Ok 'every FAQ answer exists in both places'

# -----------------------------------------------------------------------------
Start-Check 'No em dashes, no debug suffixes, no stale language claim'
foreach ($p in $docs.Values) {
  foreach ($bad in @([char]0x2014, '&mdash;', '&#8212;')) {
    if ($p.Html.Contains($bad)) { Add-Failure "$($p.Rel): contains an em dash ($bad)" }
  }
  foreach ($m in [regex]::Matches($p.Html, '\((EN|IT|ES|SQ)\)')) {
    Add-Failure "$($p.Rel): debug language suffix $($m.Value)"
  }
}
Write-Ok 'prose rules hold'

# -----------------------------------------------------------------------------
Start-Check 'Translated pages carry no leftover English boilerplate'
$stock = @('Skip to content', 'Frequently Asked Questions', 'All rights reserved',
           'Receive our newsletter', 'Read more', 'Keep Reading', 'Back to Blog')
$scanned = 0
foreach ($lang in @('es', 'sq')) {
  foreach ($slug in @($status.translated.$lang)) {
    $rel = Get-PagePath $slug $lang
    if (-not $docs.ContainsKey($rel)) { Add-Failure "translation-status lists a missing page: $rel"; continue }
    $scanned++
    foreach ($s in $stock) {
      if ($docs[$rel].Html.Contains($s)) { Add-Failure "$rel : untranslated English string '$s'" }
    }
  }
}
if ($scanned -eq 0) {
  Write-Ok 'no pages marked translated yet (skeletons carry English by design)'
} else {
  Write-Ok "$scanned translated pages scanned"
}

# -----------------------------------------------------------------------------
Start-Check 'Blog index headlines match the article H1 they point at'
# One page-per-agent translation makes cross-page drift the likely failure, and a
# blog index advertising a different title from the article it links to is the
# most visible form of it. Matched by the BlogPosting's own url, not by array
# order, so a reordered index cannot produce a false pass.
function Get-PlainText([string]$fragment) {
  $t = [regex]::Replace($fragment, '<[^>]+>', '')
  $t = [System.Net.WebUtility]::HtmlDecode($t)
  return ([regex]::Replace($t, '\s+', ' ')).Trim()
}
$checkedTitles = 0
foreach ($lang in $LANGS.Keys) {
  $idxRel = Get-PagePath 'blog' $lang
  if (-not $docs.ContainsKey($idxRel)) { continue }
  $idxHtml = $docs[$idxRel].Html

  foreach ($m in [regex]::Matches($idxHtml,
      '"@type":\s*"BlogPosting",\s*"headline":\s*"([^"]+)",\s*"url":\s*"([^"]+)"')) {
    $headline = [System.Net.WebUtility]::HtmlDecode($m.Groups[1].Value)
    $target   = Convert-UrlToPath $m.Groups[2].Value
    if (-not $target -or -not $docs.ContainsKey($target)) {
      Add-Failure "$idxRel : BlogPosting url has no page ($($m.Groups[2].Value))"
      continue
    }
    # Only meaningful once BOTH pages are translated: a finished index legitimately
    # points at articles still carrying English placeholder copy mid-project.
    if (-not (Test-PageTranslated $docs[$target].Slug $docs[$target].Lang)) { continue }
    if (-not (Test-PageTranslated 'blog' $lang)) { continue }

    $h1m = [regex]::Match($docs[$target].Html, '(?s)<h1[^>]*>(.*?)</h1>')
    if (-not $h1m.Success) { Add-Failure "$target : no <h1>"; continue }
    $h1 = Get-PlainText $h1m.Groups[1].Value
    $checkedTitles++
    if ($h1 -ne $headline) {
      Add-Failure "$idxRel advertises '$headline' but $target has H1 '$h1'"
    }
  }
}
Write-Ok "$checkedTitles blog titles agree with the articles they link to"

# The og meta and the JSON-LD say the same thing about a page's section, so they
# must not drift apart. A translation sweep that updates one and not the other
# leaves a page describing itself two ways; that is exactly what happened to the
# Albanian tree, on five pages, and nothing caught it.
$checkedSections = 0
foreach ($p in $docs.Values) {
  $metaM = [regex]::Match($p.Html, 'property="article:section" content="([^"]*)"')
  $jsonM = [regex]::Match($p.Html, '"articleSection":\s*"([^"]+)"')
  if (-not $metaM.Success -or -not $jsonM.Success) { continue }
  $checkedSections++
  $meta = [System.Net.WebUtility]::HtmlDecode($metaM.Groups[1].Value)
  $json = [System.Net.WebUtility]::HtmlDecode($jsonM.Groups[1].Value)
  if ($meta -ne $json) {
    Add-Failure "$($p.Rel): article:section meta is '$meta' but JSON-LD articleSection is '$json'"
  }
}
Write-Ok "$checkedSections article:section values agree with their JSON-LD"

# -----------------------------------------------------------------------------
Start-Check 'Titles fit the SERP and descriptions fit the snippet'
# Applied to ALL FOUR trees, not just English. Translating from an over-length
# English source is exactly how Spanish and Albanian ended up with 16/16
# over-length descriptions while English read fine.
$TITLE_MAX = 60
$DESC_MIN  = 120
$DESC_MAX  = 155
$longestTitle = 0
foreach ($p in $docs.Values) {
  $tm = [regex]::Match($p.Html, '(?s)<title>(.*?)</title>')
  if (-not $tm.Success) { Add-Failure "$($p.Rel): no <title>"; continue }
  $title = [System.Net.WebUtility]::HtmlDecode($tm.Groups[1].Value).Trim()
  if ($title.Length -gt $TITLE_MAX) {
    Add-Failure "$($p.Rel): title is $($title.Length) chars, max $TITLE_MAX"
  }
  if ($title.Length -gt $longestTitle) { $longestTitle = $title.Length }

  $dm = [regex]::Match($p.Html, '<meta name="description" content="([^"]*)"')
  if (-not $dm.Success) { Add-Failure "$($p.Rel): no meta description"; continue }
  $desc = [System.Net.WebUtility]::HtmlDecode($dm.Groups[1].Value).Trim()
  if ($desc.Length -lt $DESC_MIN -or $desc.Length -gt $DESC_MAX) {
    Add-Failure "$($p.Rel): description is $($desc.Length) chars, want $DESC_MIN-$DESC_MAX"
  }
}
Write-Ok "$($docs.Count) pages, longest title $longestTitle chars"

# -----------------------------------------------------------------------------
Start-Check 'Every <img> declares its real dimensions'
# Missing width/height is CLS exposure. Declaring the WRONG ones is worse: the
# browser reserves a box of the wrong shape and may be told to upscale, which is
# what 44 blog heroes were doing with width="1200" height="500" against
# 1080x1258 portrait sources.
$imgRx  = [regex]'<img\b[^>]*>'
$attrRx = [regex]'(\w+)="([^"]*)"'
$imgTotal = 0; $imgBad = @{}
foreach ($p in $docs.Values) {
  $baseDir = Split-Path -Parent $p.Full
  foreach ($m in $imgRx.Matches($p.Html)) {
    $tag = $m.Value
    $a = @{}
    foreach ($am in $attrRx.Matches($tag)) { $a[$am.Groups[1].Value] = $am.Groups[2].Value }
    # the lightbox placeholder has no src by design; main.js fills it
    if (-not $a.ContainsKey('src') -or $a['src'] -eq '') { continue }
    $imgTotal++
    if (-not $a.ContainsKey('width') -or -not $a.ContainsKey('height')) {
      $imgBad["$($p.Rel) -> $($a['src']) : no width/height"] = $true
      continue
    }
    $srcPath = ($a['src'] -split '[#?]')[0]
    if ($srcPath -match '^(https?:|//|data:)') { continue }
    # resolve the page-relative src back to a repo-relative key
    $full = [System.IO.Path]::GetFullPath((Join-Path $baseDir $srcPath))
    $rel  = $full.Substring($root.Length).TrimStart('\', '/')
    $size = Get-ImageSize $rel
    if ($null -eq $size) { continue }   # not an image Pillow could read
    if ([int]$a['width'] -ne $size.W -or [int]$a['height'] -ne $size.H) {
      $imgBad["$($p.Rel) -> $srcPath : declares $($a['width'])x$($a['height']), file is $($size.W)x$($size.H)"] = $true
    }
  }
}
foreach ($k in ($imgBad.Keys | Sort-Object)) { Add-Failure $k }
Write-Ok "$imgTotal images checked against their own file headers"

# -----------------------------------------------------------------------------
Start-Check 'No orphan pages: every page has an inbound editorial link'
# Nav and footer links do not count. A page reachable only from boilerplate is
# one nothing on the site actually recommends, which is how portfolio.html ended
# up with 113 words and no reason for anyone to visit it.
# Strip only the site chrome. NOT every <header>: section__head blocks are
# ordinary content and carry real editorial links, so stripping them made
# index.html's link to the portfolio invisible to this check.
$navRx = [regex]'(?s)<nav\b.*?</nav>|<footer\b.*?</footer>|<header class="site-header".*?</header>'
$inbound = @{}
foreach ($p in $docs.Values) { $inbound[$p.Rel] = 0 }
foreach ($p in $docs.Values) {
  $editorial = $navRx.Replace($p.Html, '')
  foreach ($m in [regex]::Matches($editorial, 'href="(/[^"]*)"')) {
    $target = Convert-UrlToPath "$SITE$($m.Groups[1].Value)"
    if ($target -and $inbound.ContainsKey($target) -and $target -ne $p.Rel) {
      $inbound[$target]++
    }
  }
}
foreach ($rel in ($inbound.Keys | Sort-Object)) {
  # the tree root is reached from the logo and nav by design, never editorially
  if ($rel -match '(^|/)index\.html$') { continue }
  if ($inbound[$rel] -eq 0) { Add-Failure "$rel : orphan, no editorial inbound link" }
}
Write-Ok "$($inbound.Count) pages checked for inbound editorial links"

# -----------------------------------------------------------------------------
Start-Check 'Encoding: UTF-8, no BOM, no mojibake, no diacritic entities'
foreach ($p in $docs.Values) {
  $bytes = [System.IO.File]::ReadAllBytes($p.Full)
  if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
    Add-Failure "$($p.Rel): has a UTF-8 BOM"
  }
  try { $null = [System.Text.UTF8Encoding]::new($false, $true).GetString($bytes) }
  catch { Add-Failure "$($p.Rel): not valid UTF-8" }
  if ($p.Html.Contains([char]0xFFFD)) { Add-Failure "$($p.Rel): contains U+FFFD (mojibake)" }
  # The workspace corpus is split on this; Essi is entity-free and stays that way.
  foreach ($e in @('&euml;', '&ccedil;', '&egrave;', '&agrave;', '&ugrave;', '&ograve;')) {
    if ($p.Html.Contains($e)) { Add-Failure "$($p.Rel): HTML entity $e - use the literal character" }
  }
}
Write-Ok 'all pages are clean UTF-8'

# -----------------------------------------------------------------------------
Start-Check 'sitemap.xml agrees with the pages'
& (Join-Path $PSScriptRoot 'gen-sitemap.ps1') -Check | Out-Null
if ($LASTEXITCODE -ne 0) { Add-Failure 'sitemap.xml is stale - run .build/gen-sitemap.ps1' }
else { Write-Ok "$([regex]::Matches($sitemapXml, '<loc>').Count) urls derived from the pages themselves" }

# -----------------------------------------------------------------------------
Start-Check 'llms.txt lists every live page and no held one'
# Re-derived from $docs rather than by re-running gen-llms.py, which would only
# prove the generator agrees with itself. The risk being checked is a held page
# leaking: llms.txt is read by assistants that do not honour noindex, so an
# untranslated English duplicate listed here is published in the only sense that
# matters, whatever the robots meta says.
$llmsPath = Join-Path $root 'llms.txt'
if (-not (Test-Path $llmsPath)) {
  Add-Failure 'llms.txt is missing - run python .build/gen-llms.py'
} else {
  $llms   = [System.IO.File]::ReadAllText($llmsPath)
  $listed = @([regex]::Matches($llms, '\]\((https://www\.marketingpro-agency\.com[^)]*)\)') |
              ForEach-Object { $_.Groups[1].Value })

  # Every URL must resolve to a page that exists AND is live.
  foreach ($u in ($listed | Sort-Object -Unique)) {
    $rel = $u -replace '^https://www\.marketingpro-agency\.com', ''
    $rel = if ($rel -eq '' -or $rel -eq '/') { 'index.html' }
           elseif ($rel.EndsWith('/'))       { $rel.TrimStart('/') + 'index.html' }
           else                              { $rel.TrimStart('/') + '.html' }
    $doc = $docs.Values | Where-Object { $_.Rel -eq $rel }
    if (-not $doc) { Add-Failure "llms.txt links $u, which is not a page"; continue }
    if (-not (Test-PageLive $doc.Slug $doc.Lang)) {
      Add-Failure "llms.txt links $u, which is held back as noindex"
    }
  }

  # And every live English page must be listed, so adding a page cannot silently
  # skip it. Other trees are summarised by a single link, not enumerated.
  foreach ($slug in $PAGES) {
    $want = if ($slug -eq 'index') { 'https://www.marketingpro-agency.com/' }
            else { "https://www.marketingpro-agency.com/$slug" }
    if ($listed -notcontains $want) {
      Add-Failure "llms.txt does not list /$slug - run python .build/gen-llms.py"
    }
  }
  if ($failures.Count -eq 0) { Write-Ok "$($listed.Count) links, all live, all $($PAGES.Count) English pages present" }
}

# -----------------------------------------------------------------------------
Start-Check 'Hero preload names the file the browser will actually fetch'
# A preload that names the wrong file is worse than none: it spends a
# high-priority connection on an image that is never displayed AND leaves the
# real LCP undiscovered. Both failure modes shipped here - eight generated pages
# inherited their shell's preload, and every <picture> hero preloaded the JPEG
# fallback rather than the WebP the browser resolves to.
#
# index and contact are exempt by design: index preloads its hero VIDEO poster,
# contact preloads a CSS background. Neither has a <picture> hero to agree with.
$heroChecked = 0
foreach ($p in $docs.Values) {
  if ($p.Slug -in @('index', 'contact')) { continue }
  $pre = [regex]::Match($p.Html, '<link rel="preload"[^>]*as="image"[^>]*>')
  if (-not $pre.Success) { continue }
  $mainStart = $p.Html.IndexOf('<main')
  $mainEnd   = $p.Html.IndexOf('</main>')
  if ($mainStart -lt 0 -or $mainEnd -lt 0) { continue }
  $main = $p.Html.Substring($mainStart, $mainEnd - $mainStart)
  $pic  = [regex]::Match($main, '(?s)<picture>.*?</picture>')
  if (-not $pic.Success) {
    Add-Failure "$($p.Rel): preloads an image but has no <picture> hero"; continue
  }
  $srcset = [regex]::Match($pic.Value, 'srcset="([^"]*)"')
  if (-not $srcset.Success) { continue }
  $heroChecked++

  $want = ($srcset.Groups[1].Value -split '/')[-1]
  $href = [regex]::Match($pre.Value, 'href="([^"]*)"')
  $got  = if ($href.Success) { ($href.Groups[1].Value -split '/')[-1] } else { '(none)' }
  if ($got -ne $want) {
    Add-Failure "$($p.Rel): preloads $got but <picture> resolves to $want"
  }
  if ($pre.Value -notmatch 'type="image/webp"') {
    Add-Failure "$($p.Rel): hero preload has no type=""image/webp"", so browsers without WebP fetch a file they cannot decode"
  }
}
Write-Ok "$heroChecked hero preloads agree with their <picture>"

# -----------------------------------------------------------------------------
Start-Check 'Service pages share one set of boilerplate strings per language'
# The eight service pages are generated from one template and differ only in
# subject matter. Everything structural - the breadcrumb stem, the section
# headings, the CTA, the back link, the shared pricing paragraph - is the same
# sentence eight times, and in English it always was.
#
# Translation is where that breaks, because eight pages is too many for one pass
# and parallel translators cannot see each other's word choices. It broke twice
# here: Spanish shipped two wordings of the pricing paragraph, four pages each,
# differing in "una tarifa" vs "una tarifa fija"; Albanian shipped four pages
# whose breadcrumb still read Home / Services in English. Both are invisible on
# any single page and obvious the moment the eight are put side by side, which
# is what this does.
$svc = @($PAGES | Where-Object { $_ -like 'services-*' })
foreach ($lang in $LANGS.Keys) {
  $seen = @{}
  foreach ($slug in $svc) {
    $rel = Get-PagePath $slug $lang
    if (-not $docs.ContainsKey($rel)) { continue }
    $html = $docs[$rel].Html
    $mi = $html.IndexOf('<main'); $mj = $html.IndexOf('</main>')
    if ($mi -lt 0 -or $mj -lt 0) { continue }
    $main = $html.Substring($mi, $mj - $mi)

    $crumbs = [regex]::Matches([regex]::Match($main, '(?s)<nav class="breadcrumb".*?</nav>').Value, '(?s)<li>(.*?)</li>')
    $h2s    = [regex]::Matches($main, '(?s)<h2>(.*?)</h2>')
    $fields = @{}
    if ($crumbs.Count -ge 2) {
      $fields['breadcrumb 1'] = Get-PlainText $crumbs[0].Groups[1].Value
      $fields['breadcrumb 2'] = Get-PlainText $crumbs[1].Groups[1].Value
    }
    if ($h2s.Count -ge 4) {
      $fields['first heading']   = Get-PlainText $h2s[0].Groups[1].Value
      $fields['who-suits head']  = Get-PlainText $h2s[$h2s.Count - 3].Groups[1].Value
      $fields['pricing head']    = Get-PlainText $h2s[$h2s.Count - 2].Groups[1].Value
      $fields['faq head']        = Get-PlainText $h2s[$h2s.Count - 1].Groups[1].Value
    }
    $cta = [regex]::Match($main, '(?s)btn--green[^>]*>(.*?)</a>')
    if ($cta.Success) { $fields['cta'] = Get-PlainText $cta.Groups[1].Value }
    $back = [regex]::Match($main, '(?s)article__back".*?</a>')
    if ($back.Success) { $fields['back link'] = Get-PlainText $back.Value }
    $lv = [regex]::Match($main, '(?s)post-service"><strong>(.*?)</strong>')
    if ($lv.Success) { $fields['long-version label'] = Get-PlainText $lv.Groups[1].Value }
    $ph = [regex]::Match($main, '(?s)<h2>' + [regex]::Escape($fields['pricing head']) + '</h2>\s*<p>(.*?)</p>')
    if ($ph.Success) { $fields['pricing paragraph'] = Get-PlainText $ph.Groups[1].Value }

    foreach ($k in $fields.Keys) {
      if (-not $seen.ContainsKey($k)) { $seen[$k] = @{} }
      $v = $fields[$k]
      if (-not $seen[$k].ContainsKey($v)) { $seen[$k][$v] = @() }
      $seen[$k][$v] += $slug
    }
  }
  foreach ($k in $seen.Keys) {
    if ($seen[$k].Count -le 1) { continue }
    $variants = ($seen[$k].Keys | ForEach-Object {
      $short = if ($_.Length -gt 60) { $_.Substring(0, 60) + '...' } else { $_ }
      "`"$short`" on $($seen[$k][$_].Count)"
    }) -join ' vs '
    Add-Failure "$lang/: service pages disagree on '$k' - $variants"
  }
}
Write-Ok "$($svc.Count) service pages x $($LANGS.Count) trees share one boilerplate set"

# -----------------------------------------------------------------------------
Start-Check 'Nothing deployable is oversized, and the root holds only what it should'
# Two failures this session that nothing would have caught before deploy time.
#
# SIZE. Cloudflare Workers Assets rejects any single file over 25 MiB. A 122.6
# MiB camera master sat in this repo and would not have made the deploy slow, it
# would have made it fail, with the first sign being a wrangler error. 20 MiB
# leaves headroom to notice before the ceiling.
#
# ROOT. wrangler.jsonc sets assets.directory ".", so the repo root IS the public
# asset set, and .assetsignore filters by path rather than by git status.
# Untracked does not mean unpublished: three stray files sat in the root and
# would have been served from https://.../005.mp4 on the next deploy. So the
# root is an allowlist, and anything new has to be named here deliberately.
$MAX_MB = 20
$rootAllow = @(
  '_headers', 'llms.txt', 'robots.txt', 'site.webmanifest', 'sitemap.xml', 'wrangler.jsonc'
)
$dirAllow = @('assets', 'it', 'es', 'sq', '.build', 'originals', '.git')

$oversize = 0
Get-ChildItem -Path $root -Recurse -File -Force |
  Where-Object { $_.FullName -notmatch '[\\/](\.git|\.build|originals)[\\/]' } |
  ForEach-Object {
    if ($_.Length -gt ($MAX_MB * 1MB)) {
      $oversize++
      $mb = [math]::Round($_.Length / 1MB, 1)
      Add-Failure "$($_.Name) is $mb MB - over the $MAX_MB MB guard, and Cloudflare rejects anything above 25 MiB"
    }
  }

foreach ($item in (Get-ChildItem -Path $root -Force)) {
  if ($item.PSIsContainer) {
    if ($dirAllow -notcontains $item.Name) {
      Add-Failure "unexpected directory in the repo root: $($item.Name)/ - it would be served publicly"
    }
    continue
  }
  if ($item.Name -like '.*') { continue }          # dotfiles are config, not assets
  if ($item.Name -like '*.html') { continue }      # page files are checked by parity
  if ($rootAllow -notcontains $item.Name) {
    Add-Failure "unexpected file in the repo root: $($item.Name) - it would be served at https://.../$($item.Name)"
  }
}
if ($oversize -eq 0) {
  $biggest = Get-ChildItem -Path $root -Recurse -File -Force |
             Where-Object { $_.FullName -notmatch '[\\/](\.git|\.build|originals)[\\/]' } |
             Sort-Object Length -Descending | Select-Object -First 1
  Write-Ok "largest deployable file is $($biggest.Name), $([math]::Round($biggest.Length/1MB,2)) MB; root is clean"
}

# -----------------------------------------------------------------------------
Start-Check 'Every <video> reserves its own space'
# The <img> check exists because an image without width/height causes layout
# shift. A <video> in normal flow does exactly the same, and had no check at
# all. The hero escapes only because CSS pins it to 100svh; the case-study
# video sits in the document flow and would shift the page under the reader.
$videos = 0
foreach ($p in $docs.Values) {
  foreach ($m in [regex]::Matches($p.Html, '<video\b[^>]*>')) {
    $tag = $m.Value
    if ($tag -match 'class="hero__video"') { continue }   # sized by CSS to the viewport
    $videos++
    if ($tag -notmatch '\bwidth="\d+"' -or $tag -notmatch '\bheight="\d+"') {
      Add-Failure "$($p.Rel): <video> has no width/height, so it reserves no space and shifts the page"
    }
  }
}
Write-Ok "$videos in-flow videos declare their dimensions"

# -----------------------------------------------------------------------------
Write-Host ''
if ($failures.Count -eq 0) {
  Write-Host 'RESULT: ALL PASSES CLEAN' -ForegroundColor Green
  exit 0
}
Write-Host "RESULT: $($failures.Count) FAILURE(S)" -ForegroundColor Red
exit 1
