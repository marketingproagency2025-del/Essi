# =============================================================================
#  lib-chrome.ps1 - shared language tables and header-nav builder
#  Dot-sourced by fix-nav.ps1, port-lang.ps1 and verify-langs.ps1.
#  No side effects: defines constants and functions only.
#
#  The repo is UTF-8 with LF line endings. Every string this file emits is
#  joined with "`n" explicitly so a CRLF-saved .ps1 cannot leak CRLF into HTML.
# =============================================================================

$SITE = 'https://www.marketingpro-agency.com'

# The 16 page slugs, identical in every language tree. 'index' is the tree root.
$PAGES = @(
  'index', 'services', 'portfolio', 'about', 'contact', 'blog',
  'blog-social-media', 'blog-advertising', 'blog-website', 'blog-seo',
  'blog-sales-funnel', 'blog-photo-video', 'blog-renders', 'blog-catalogues',
  'article-1', 'article-2',
  # Commercial landing pages, one per service. Flat slugs on purpose: nesting
  # under services/ would make /services ambiguous between services.html and
  # services/index.html under Cloudflare's auto-trailing-slash.
  'services-social-media', 'services-advertising', 'services-website', 'services-seo',
  'services-sales-funnel', 'services-photo-video', 'services-renders', 'services-catalogues'
)

# Sitemap priority per page, carried over verbatim from the sitemap that
# shipped before this became generated, so the four-language rebuild does not
# silently reweight anything.
$PRIORITY = @{
  'index' = '1.0'; 'services' = '0.9'; 'blog' = '0.9'
  'portfolio' = '0.8'; 'about' = '0.8'; 'contact' = '0.8'
  'blog-social-media' = '0.7'; 'blog-advertising' = '0.7'; 'blog-website' = '0.7'
  'blog-seo' = '0.7'; 'blog-sales-funnel' = '0.7'; 'blog-photo-video' = '0.7'
  'blog-renders' = '0.7'; 'blog-catalogues' = '0.7'
  'article-1' = '0.5'; 'article-2' = '0.5'
  # 0.8: commercial intent, so above the 0.7 guides and below the 0.9 hub.
  'services-social-media' = '0.8'; 'services-advertising' = '0.8'
  'services-website' = '0.8';      'services-seo' = '0.8'
  'services-sales-funnel' = '0.8'; 'services-photo-video' = '0.8'
  'services-renders' = '0.8';      'services-catalogues' = '0.8'
}

# dir    - subdirectory under the repo root ('' for the English tree at root)
# prefix - URL prefix ('' for English)
# Order matters: it is the order hreflang links and og:locale:alternate are
# written in, and the gate compares against it.
$LANGS = [ordered]@{
  en = @{
    dir = ''; prefix = ''; code = 'EN'; label = 'English'; locale = 'en_US'
    aria = 'Change language'
    brandAria = 'MarketingPro home'; navAria = 'Primary'; toggleAria = 'Open menu'
    footAria = 'Footer'; crumbAria = 'Breadcrumb'
    nav = [ordered]@{ home = 'Home'; services = 'Services'; portfolio = 'Portfolio'
                      blog = 'Blog'; about = 'About'; contact = 'Contact' }
  }
  it = @{
    dir = 'it'; prefix = '/it'; code = 'IT'; label = 'Italiano'; locale = 'it_IT'
    aria = 'Cambia lingua'
    brandAria = 'MarketingPro, torna alla home'; navAria = 'Principale'; toggleAria = 'Apri menu'
    footAria = 'Piè di pagina'; crumbAria = 'Percorso di navigazione'
    nav = [ordered]@{ home = 'Home'; services = 'Servizi'; portfolio = 'Portfolio'
                      blog = 'Blog'; about = 'Chi Siamo'; contact = 'Contatti' }
  }
  es = @{
    dir = 'es'; prefix = '/es'; code = 'ES'; label = 'Español'; locale = 'es_ES'
    aria = 'Cambiar idioma'
    brandAria = 'MarketingPro, ir al inicio'; navAria = 'Principal'; toggleAria = 'Abrir menú'
    footAria = 'Pie de página'; crumbAria = 'Ruta de navegación'
    nav = [ordered]@{ home = 'Inicio'; services = 'Servicios'; portfolio = 'Portfolio'
                      blog = 'Blog'; about = 'Quiénes Somos'; contact = 'Contacto' }
  }
  # Albanian labels follow the workspace corpus, not invention:
  #   Kreu        - as used on Iglisi's about/b2b pages (b2b is the closest
  #                 precedent here, being the only B2B prose in the corpus)
  #   Shërbimet   - definite form, as in "Shërbimet Tona"
  #   Portfolio / Blog - kept in English. The corpus keeps marketing, Blog,
  #                 Shop and cookie-t in English with Albanian inflection;
  #                 there is no precedent for an Albanian "portfolio".
  #   Ndrysho gjuhën - the corpus has 13 competing strings for this. One wins.
  sq = @{
    dir = 'sq'; prefix = '/sq'; code = 'SQ'; label = 'Shqip'; locale = 'sq_AL'
    aria = 'Ndryshoni gjuhën'
    brandAria = 'MarketingPro, kthehuni te kreu'; navAria = 'Kryesore'; toggleAria = 'Hapni menunë'
    footAria = 'Fundi i faqes'; crumbAria = 'Gjurma e navigimit'
    nav = [ordered]@{ home = 'Kreu'; services = 'Shërbimet'; portfolio = 'Portfolio'
                      blog = 'Blog'; about = 'Rreth Nesh'; contact = 'Kontakt' }
  }
}

# Which nav item is highlighted on each page. Mirrors what the site already did:
# the two editorial articles highlight Services, every blog post highlights Blog.
function Get-ActiveNav([string]$slug) {
  switch -Regex ($slug) {
    '^index$'                  { return 'home' }
    '^(services|article-\d+)'  { return 'services' }   # also services-seo etc.
    '^portfolio$'              { return 'portfolio' }
    '^about$'                  { return 'about' }
    '^contact$'                { return 'contact' }
    '^blog'                    { return 'blog' }
  }
  return ''
}

# URL of a page within its own language tree, e.g. ('services','it') -> /it/services
function Get-PageUrl([string]$slug, [string]$lang) {
  $p = $LANGS[$lang].prefix
  if ($slug -eq 'index') { return "$p/" }
  return "$p/$slug"
}

# Relative path from a page to a repo-root asset. English sits at the root,
# every other tree is exactly one directory deep.
function Get-AssetPrefix([string]$lang) {
  if ($lang -eq 'en') { return '' }
  return '../'
}

# On-disk path of a page relative to the repo root.
function Get-PagePath([string]$slug, [string]$lang) {
  $d = $LANGS[$lang].dir
  if ($d -eq '') { return "$slug.html" }
  return "$d/$slug.html"
}

# -----------------------------------------------------------------------------
# Header nav + language switcher
# -----------------------------------------------------------------------------
# The switcher lists only the current language. main.js rebuilds the full menu
# from the page's own hreflang links, so this is the no-JS fallback and adding a
# fifth language never touches the HTML again.
function New-NavBlock([string]$slug, [string]$lang) {
  $L      = $LANGS[$lang]
  $active = Get-ActiveNav $slug
  $self   = Get-PageUrl $slug $lang

  $lines = @('        <ul class="nav__menu" id="primary-menu" data-nav-menu>')
  foreach ($key in @('home', 'services', 'portfolio', 'blog', 'about', 'contact')) {
    $slugFor = if ($key -eq 'home') { 'index' } else { $key }
    $href = Get-PageUrl $slugFor $lang
    $cls  = if ($key -eq $active) { 'nav__link is-active' } else { 'nav__link' }
    $lines += "          <li><a class=""$cls"" href=""$href"">$($L.nav[$key])</a></li>"
  }
  $lines += '          <li class="nav__lang" data-lang-switch>'
  $lines += "            <button class=""lang"" type=""button"" aria-haspopup=""true"" aria-expanded=""false"" aria-label=""$($L.aria)"" data-lang-toggle>"
  $lines += "              $($L.code)"
  $lines += '              <svg viewBox="0 0 24 24" width="12" height="12" aria-hidden="true"><path fill="currentColor" d="M7 10l5 5 5-5z"/></svg>'
  $lines += '            </button>'
  $lines += '            <ul class="lang__menu" role="menu" data-lang-menu>'
  $lines += "              <li role=""none""><a class=""lang__item is-active"" role=""menuitem"" aria-current=""true"" href=""$self"">$($L.label)</a></li>"
  $lines += '            </ul>'
  $lines += '          </li>'
  $lines += '        </ul>'
  return ($lines -join "`n")
}

# Replaces the nav block in a full HTML string. Idempotent: the block it writes
# matches the same pattern it consumes, so re-running rebuilds it identically.
# The pattern stops at a </ul> indented by exactly 8 spaces, which closes
# nav__menu; the nested lang__menu closes at 12 spaces and cannot match.
function Set-NavBlock([string]$html, [string]$slug, [string]$lang) {
  $m = [regex]::Match($html, '(?s)        <ul class="nav__menu".*?\n        </ul>')
  if (-not $m.Success) { throw "nav__menu block not found ($lang/$slug)" }
  return $html.Replace($m.Value, (New-NavBlock $slug $lang))
}

# -----------------------------------------------------------------------------
# Head metadata: hreflang, og:locale, schema language arrays, cache busting
# -----------------------------------------------------------------------------

# Bump when assets/css/style.css or assets/js/main.js changes, so returning
# visitors do not run a four-language switcher against a two-language script.
$CSS_VERSION = 13
$JS_VERSION  = 15

# -----------------------------------------------------------------------------
# Staged rollout
# -----------------------------------------------------------------------------
# Spanish and Albanian pages are generated long before they are translated. An
# untranslated page is a duplicate of the English one, so until a translator has
# finished it the page is deliberately invisible: noindex, absent from the
# sitemap, and absent from every hreflang set. That keeps the site safe to
# deploy at any point mid-project instead of only at cut-over.
#
# English and Italian are always live. Everything else is driven by
# translation-status.json, which sessions 2-5 fill in page by page.
$STATUS = Get-Content (Join-Path $PSScriptRoot 'translation-status.json') -Raw | ConvertFrom-Json

# Translated: the copy is finished. Turns ON the quality checks.
# Live:       the tree is published. Turns OFF noindex, and puts the page into
#             sitemap.xml, the hreflang sets and the language switcher.
# These are different facts. A finished translation waiting on a native
# proofread is translated but not live, and that is the normal state here.
function Test-PageTranslated([string]$slug, [string]$lang) {
  if ($lang -eq 'en' -or $lang -eq 'it') { return $true }
  $done = $STATUS.translated.$lang
  if (-not $done) { return $false }
  return ([string[]]$done -contains $slug)
}

function Test-PageLive([string]$slug, [string]$lang) {
  if ($lang -eq 'en' -or $lang -eq 'it') { return $true }
  if (([string[]]$STATUS.live) -notcontains $lang) { return $false }
  return (Test-PageTranslated $slug $lang)
}

# Languages whose version of this page is live, in table order.
function Get-LiveLangs([string]$slug) {
  return @($LANGS.Keys | Where-Object { Test-PageLive $slug $_ })
}

# The hreflang set is identical on every live version of a page, listing the
# live languages plus x-default. x-default points at English, which is the
# primary market and matches the Iglisi Watch precedent for a base tree that
# does not localise its slugs.
function New-HreflangBlock([string]$slug) {
  $lines = @('  <!-- hreflang -->')
  foreach ($code in (Get-LiveLangs $slug)) {
    $url = "$SITE$(Get-PageUrl $slug $code)"
    $lines += "  <link rel=""alternate"" hreflang=""$code"" href=""$url"" />"
  }
  $lines += "  <link rel=""alternate"" hreflang=""x-default"" href=""$SITE$(Get-PageUrl $slug 'en')"" />"
  return ($lines -join "`n")
}

function Set-HreflangBlock([string]$html, [string]$slug) {
  $pattern = '(?m)^  <!-- hreflang -->\r?\n(?:^  <link rel="alternate" hreflang="[^"]*"[^\n]*\r?\n)+'
  $m = [regex]::Match($html, $pattern)
  if (-not $m.Success) { throw "hreflang block not found ($slug)" }
  return $html.Replace($m.Value, (New-HreflangBlock $slug) + "`n")
}

# Landmark and brand aria-labels. These are what a screen reader announces when
# moving between regions, so leaving them English on a translated page is a real
# accessibility defect. The Italian tree shipped "Primary" / "Footer" /
# "Breadcrumb" / "MarketingPro home" in English from the start; this fixes that
# as a side effect of doing it properly for the new trees.
# Anchored on the element class so only the landmark is touched, never the
# translated aria-labels on testimonials, FAQ sections and so on.
function Set-LandmarkLabels([string]$html, [string]$lang) {
  $L = $LANGS[$lang]
  $map = @(
    @{ rx = '(<a class="brand"[^>]*?aria-label=")[^"]*(")';          val = $L.brandAria },
    @{ rx = '(<nav class="nav"[^>]*?aria-label=")[^"]*(")';          val = $L.navAria   },
    @{ rx = '(<nav class="footer__nav"[^>]*?aria-label=")[^"]*(")';  val = $L.footAria  },
    @{ rx = '(<nav class="breadcrumb"[^>]*?aria-label=")[^"]*(")';   val = $L.crumbAria },
    @{ rx = '(<button class="nav__toggle"[^>]*?aria-label=")[^"]*(")'; val = $L.toggleAria }
  )
  foreach ($m in $map) {
    $html = [regex]::Replace($html, $m.rx, "`${1}$($m.val)`${2}")
  }
  return $html
}

# Shared footer and skip-link strings. These appear identically on all 16 pages
# of a tree, which makes them a drift factory: the first Albanian pass produced
# three different newsletter buttons and two different placeholders across six
# pages, because six agents each translated the same footer independently.
# Generating them from one table removes the whole class of problem, for the
# Spanish pass too.
$CHROME = @{
  en = @{ skip = 'Skip to content'; contact = 'Contact'
          nlHead = 'Receive our newsletter'; nlLabel = 'Enter your email address'
          nlPlaceholder = 'Your email for updates'; nlButton = 'Join us for growth'
          nlNote = "Thanks! We'll be in touch."; rights = 'All rights reserved.' }
  it = @{ skip = 'Vai al contenuto'; contact = 'Contatti'
          nlHead = 'Ricevi la nostra newsletter'; nlLabel = 'Inserisci il tuo indirizzo email'
          nlPlaceholder = 'La tua email per gli aggiornamenti'; nlButton = 'Cresci con noi'
          nlNote = 'Grazie! Ti contatteremo presto.'; rights = 'Tutti i diritti riservati.' }
  es = @{ skip = 'Saltar al contenido'; contact = 'Contacto'
          nlHead = 'Recibe nuestra newsletter'; nlLabel = 'Escribe tu correo electrónico'
          nlPlaceholder = 'Tu correo para novedades'; nlButton = 'Crece con nosotros'
          nlNote = '¡Gracias! Nos pondremos en contacto.'; rights = 'Todos los derechos reservados.' }
  sq = @{ skip = 'Kaloni te përmbajtja kryesore'; contact = 'Kontakt'
          nlHead = 'Merrni newsletter-in tonë'; nlLabel = 'Shkruani adresën tuaj email'
          nlPlaceholder = 'Email-i juaj për përditësimet'; nlButton = 'Rrituni bashkë me ne'
          nlNote = "Faleminderit! Do t'ju kontaktojmë së shpejti."
          rights = 'Të gjitha të drejtat e rezervuara.' }
}

# The footer nav repeats the header's six links. It survived four translation
# passes intact, but it was the last piece of chrome still hand-carried, so it
# is generated too. Same label table as the header, so the two can never
# disagree about what a page is called.
function Set-FooterNav([string]$html, [string]$lang) {
  $L = $LANGS[$lang]
  $lines = @("    <nav class=""footer__nav"" aria-label=""$($L.footAria)"">")
  foreach ($key in @('home', 'services', 'portfolio', 'blog', 'about', 'contact')) {
    $slugFor = if ($key -eq 'home') { 'index' } else { $key }
    $href = Get-PageUrl $slugFor $lang
    $lines += "      <a href=""$href"">$($L.nav[$key])</a>"
  }
  $lines += '    </nav>'
  $new = ($lines -join "`n")

  $m = [regex]::Match($html, '(?s)    <nav class="footer__nav".*?\n    </nav>')
  if (-not $m.Success) { throw "footer__nav block not found ($lang)" }
  return $html.Replace($m.Value, $new)
}

function Set-ChromeStrings([string]$html, [string]$lang) {
  $C = $CHROME[$lang]
  $map = @(
    @{ rx = '(<a class="skip-link" href="#main">)[^<]*(</a>)';                              val = $C.skip },
    @{ rx = '(<label class="newsletter__label" for="news-email">)[^<]*(</label>)';          val = $C.nlLabel },
    @{ rx = '(<button class="btn btn--green" type="submit">)[^<]*(</button>)';              val = $C.nlButton },
    @{ rx = '(<p class="newsletter__note" data-newsletter-note hidden>)[^<]*(</p>)';        val = $C.nlNote },
    @{ rx = '(placeholder=")[^"]*(" autocomplete="email" required)';                        val = $C.nlPlaceholder },
    @{ rx = '(<span data-year>[^<]*</span>\. )[^<]*(</p>)';                                 val = $C.rights }
  )
  foreach ($m in $map) { $html = [regex]::Replace($html, $m.rx, "`${1}$($m.val)`${2}") }

  # The two footer headings share a class, so they are matched by position:
  # the contact column comes before the newsletter column in every page.
  $html = [regex]::Replace($html,
    '(<h2 class="footer__heading">)[^<]*(</h2>\s*<ul class="footer__list">)', "`${1}$($C.contact)`${2}")
  $html = [regex]::Replace($html,
    '(<h2 class="footer__heading">)[^<]*(</h2>\s*<form class="newsletter")', "`${1}$($C.nlHead)`${2}")
  return $html
}

$ROBOTS_LIVE = 'index, follow, max-image-preview:large, max-snippet:-1'
$ROBOTS_HELD = 'noindex, follow'

function Set-RobotsMeta([string]$html, [string]$slug, [string]$lang) {
  $content = if (Test-PageLive $slug $lang) { $ROBOTS_LIVE } else { $ROBOTS_HELD }
  $out = [regex]::Replace($html, '<meta name="robots" content="[^"]*" />',
                          "<meta name=""robots"" content=""$content"" />")
  return $out
}

# og:locale is the page's own locale; every other LIVE language becomes an
# alternate. Kept in step with the hreflang set so the two never disagree about
# which translations exist.
function Set-OgLocale([string]$html, [string]$lang, [string]$slug) {
  $lines = @("  <meta property=""og:locale"" content=""$($LANGS[$lang].locale)"" />")
  foreach ($code in (Get-LiveLangs $slug)) {
    if ($code -eq $lang) { continue }
    $lines += "  <meta property=""og:locale:alternate"" content=""$($LANGS[$code].locale)"" />"
  }
  $pattern = '(?m)^  <meta property="og:locale" content="[^"]*" />\r?\n(?:^  <meta property="og:locale:alternate" content="[^"]*" />\r?\n)*'
  $m = [regex]::Match($html, $pattern)
  if (-not $m.Success) { throw "og:locale block not found ($lang)" }
  return $html.Replace($m.Value, ($lines -join "`n") + "`n")
}

# Languages in which the whole site is available. A tree only counts once every
# one of its 16 pages is translated: a half-finished Spanish tree does not make
# the site "available in Spanish".
function Get-LiveSiteLangs {
  return @($LANGS.Keys | Where-Object {
    $l = $_
    @($PAGES | Where-Object { -not (Test-PageLive $_ $l) }).Count -eq 0
  })
}

# JSON-LD language declarations. These are two different claims and must not be
# collapsed into one:
#   WebSite.inLanguage            what the SITE is published in -> live trees only
#   ContactPoint.availableLanguage what the TEAM can converse in -> all four,
#                                 confirmed by the client 2026-08-09, and true
#                                 independently of how much of the site has
#                                 shipped
#   WebPage.inLanguage            this one page's language, a single value
function Set-LanguageArrays([string]$html, [string]$lang) {
  $site = '["' + ((Get-LiveSiteLangs) -join '", "') + '"]'
  $team = '["' + (($LANGS.Keys) -join '", "') + '"]'
  $out = [regex]::Replace($html, '"inLanguage":\s*\[[^\]]*\]',        "`"inLanguage`": $site")
  $out = [regex]::Replace($out,  '"availableLanguage":\s*\[[^\]]*\]', "`"availableLanguage`": $team")
  $out = [regex]::Replace($out,  '"inLanguage":\s*"[a-z-]+"',         "`"inLanguage`": `"$lang`"")
  return $out
}

function Set-AssetVersions([string]$html) {
  $out = [regex]::Replace($html, 'style\.css\?v=\d+', "style.css?v=$CSS_VERSION")
  $out = [regex]::Replace($out,  'main\.js\?v=\d+',   "main.js?v=$JS_VERSION")
  return $out
}

# -----------------------------------------------------------------------------
# File IO - UTF-8 without BOM, exactly how the repo is already encoded.
# -----------------------------------------------------------------------------
function Read-HtmlFile([string]$path) {
  return [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))
}

function Write-HtmlFile([string]$path, [string]$content) {
  [System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
}
