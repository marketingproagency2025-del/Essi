# =============================================================================
#  lib-chrome.ps1 - shared language tables and header-nav builder
#  Dot-sourced by fix-nav.ps1, port-lang.ps1 and verify-langs.ps1.
#  No side effects: defines constants and functions only.
#
#  The repo is UTF-8 with LF line endings. Every string this file emits is
#  joined with "`n" explicitly so a CRLF-saved .ps1 cannot leak CRLF into HTML.
# =============================================================================

$SITE = 'https://www.marketingpro-agency.com'

# The 37 page slugs, identical in every language tree. 'index' is the tree root.
$PAGES = @(
  'index', 'services', 'portfolio', 'about', 'contact', 'blog',
  'blog-social-media', 'blog-advertising', 'blog-website', 'blog-seo',
  'blog-sales-funnel', 'blog-photo-video', 'blog-renders', 'blog-catalogues',
  'blog-milano',
  'blog-roma', 'blog-lugano', 'blog-ticino',
  'blog-boost-or-campaign', 'blog-lead-quality', 'blog-in-house-or-agency', 'blog-showrooms',
  'blog-windows-and-doors', 'blog-stoves-and-heating', 'blog-builders', 'blog-restaurants', 'blog-ai-search',
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
  'blog-renders' = '0.7'; 'blog-catalogues' = '0.7'; 'blog-milano' = '0.7'
  'blog-roma' = '0.7'; 'blog-lugano' = '0.7'; 'blog-ticino' = '0.7'
  'blog-boost-or-campaign' = '0.7'; 'blog-lead-quality' = '0.7'; 'blog-in-house-or-agency' = '0.7'; 'blog-showrooms' = '0.7'
  'blog-windows-and-doors' = '0.7'; 'blog-stoves-and-heating' = '0.7'; 'blog-builders' = '0.7'; 'blog-restaurants' = '0.7'; 'blog-ai-search' = '0.7'
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
# The switcher lists EVERY live language, in the HTML, as real links.
#
# It used to emit only the current one, on the reasoning that main.js rebuilds
# the menu from the page's hreflang tags so the markup never has to change when
# a language is added. That was true for users and false for crawlers, and it
# cost the site its whole multilingual half: with no cross-language <a href>
# anywhere in the raw HTML, the four trees were four disconnected islands.
# Measured 2026-08-25 by BFS over the real link graph: 28 pages reachable from
# the English homepage, 84 unreachable. /it/, /es/ and /sq/ each had 108 inbound
# links and every single one came from inside its own tree. Google saw those 84
# only in the sitemap, which is the textbook profile of "Discovered - currently
# not indexed", and it was reporting 96 of 112 pages unindexed.
#
# It compounded with the .reveal blank-render bug (fixed f0bad2a): the content
# and the language links depended on the same script, so one failed render lost
# both at once.
#
# main.js can keep rebuilding the menu. It now finds the links already there.
# Get-LiveLangs is the same source the hreflang block uses, so a held language
# is never linked and the two can never disagree.
function New-NavBlock([string]$slug, [string]$lang) {
  $L      = $LANGS[$lang]
  $active = Get-ActiveNav $slug

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
  foreach ($code in (Get-LiveLangs $slug)) {
    $href  = Get-PageUrl $slug $code
    $label = $LANGS[$code].label
    if ($code -eq $lang) {
      $lines += "              <li role=""none""><a class=""lang__item is-active"" role=""menuitem"" aria-current=""true"" href=""$href"">$label</a></li>"
    } else {
      $lines += "              <li role=""none""><a class=""lang__item"" role=""menuitem"" hreflang=""$code"" href=""$href"">$label</a></li>"
    }
  }
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
# The pages were serving v=18 while this constant still said 17, so running
# fix-head.ps1 would have DOWNGRADED every page and served a week of stale CSS
# (_headers gives /assets/css/* a max-age of 604800). Bumped past the drift.
$CSS_VERSION = 19
$JS_VERSION  = 20

# -----------------------------------------------------------------------------
# Staged rollout
# -----------------------------------------------------------------------------
# Spanish and Albanian pages are generated long before they are translated. An
# untranslated page is a duplicate of the English one, so until a translator has
# finished it the page is deliberately invisible: noindex, absent from the
# sitemap, and absent from every hreflang set. That keeps the site safe to
# deploy at any point mid-project instead of only at cut-over.
#
# English is always live: it is the source tree, so it can never be a
# duplicate of itself. EVERY other tree, Italian included, is driven by
# translation-status.json, page by page.
#
# Italian used to be hard-coded live here alongside English, which was true
# for as long as the slug list was frozen at 16. It stopped being true the
# moment the eight service slugs were added: it/ inherited English copy and
# eight duplicate pages went live and into the sitemap. A tree being live and
# a PAGE being ready are different facts, and the second one has to be checked
# per page or adding a slug silently publishes it untranslated.
$STATUS = Get-Content (Join-Path $PSScriptRoot 'translation-status.json') -Raw | ConvertFrom-Json

# Translated: the copy is finished. Turns ON the quality checks.
# Live:       the tree is published. Turns OFF noindex, and puts the page into
#             sitemap.xml, the hreflang sets and the language switcher.
# These are different facts. A finished translation waiting on a native
# proofread is translated but not live, and that is the normal state here.
function Test-PageTranslated([string]$slug, [string]$lang) {
  if ($lang -eq 'en') { return $true }
  $done = $STATUS.translated.$lang
  if (-not $done) { return $false }
  return ([string[]]$done -contains $slug)
}

# Held back despite being finished: the page is translated and its tree is live,
# but the copy is model-produced and has not been read by a native speaker.
# .claude/rules/writing.md forbids shipping that, and without this list the act
# of finishing a translation inside a live tree would publish it the same
# instant, which is exactly the trap Italian fell into once already.
function Test-PageHeldBack([string]$slug, [string]$lang) {
  $held = $STATUS.holdback.$lang
  if (-not $held) { return $false }
  return ([string[]]$held -contains $slug)
}

function Test-PageLive([string]$slug, [string]$lang) {
  if ($lang -eq 'en') { return $true }
  if (([string[]]$STATUS.live) -notcontains $lang) { return $false }
  if (Test-PageHeldBack $slug $lang) { return $false }
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
          cfButton = 'Request a quote'; cfPlaceholder = 'Your email address'
          waHref = 'https://wa.me/355696085288?text=Hi%20MarketingPro%2C%20I%20run%20a%20business%20and%20I%27d%20like%20a%20quote%20for%20marketing%20work.'
          nlNote = "Thanks! We'll be in touch."; rights = 'All rights reserved.'
          lbZoom = 'Enlarge image'; lbClose = 'Close'
          lbPrev = 'Previous image'; lbNext = 'Next image' }
  it = @{ skip = 'Vai al contenuto'; contact = 'Contatti'
          nlHead = 'Ricevi la nostra newsletter'; nlLabel = 'Inserisci il tuo indirizzo email'
          nlPlaceholder = 'La tua email per gli aggiornamenti'; nlButton = 'Cresci con noi'
          cfButton = 'Richiedi un preventivo'; cfPlaceholder = 'Il tuo indirizzo email'
          waHref = 'https://wa.me/355696085288?text=Ciao%20MarketingPro%2C%20ho%20un%27azienda%20e%20vorrei%20un%20preventivo%20per%20il%20marketing.'
          nlNote = 'Grazie! Ti contatteremo presto.'; rights = 'Tutti i diritti riservati.'
          lbZoom = "Ingrandisci l'immagine"; lbClose = 'Chiudi'
          lbPrev = 'Immagine precedente'; lbNext = 'Immagine successiva' }
  es = @{ skip = 'Saltar al contenido'; contact = 'Contacto'
          nlHead = 'Recibe nuestra newsletter'; nlLabel = 'Escribe tu correo electrónico'
          nlPlaceholder = 'Tu correo para novedades'; nlButton = 'Crece con nosotros'
          cfButton = 'Solicita un presupuesto'; cfPlaceholder = 'Tu correo electrónico'
          waHref = 'https://wa.me/355696085288?text=Hola%20MarketingPro%2C%20tengo%20un%20negocio%20y%20quisiera%20un%20presupuesto%20de%20marketing.'
          nlNote = '¡Gracias! Nos pondremos en contacto.'; rights = 'Todos los derechos reservados.'
          lbZoom = 'Ampliar imagen'; lbClose = 'Cerrar'
          lbPrev = 'Imagen anterior'; lbNext = 'Imagen siguiente' }
  sq = @{ skip = 'Kaloni te përmbajtja kryesore'; contact = 'Kontakt'
          nlHead = 'Merrni newsletter-in tonë'; nlLabel = 'Shkruani adresën tuaj email'
          nlPlaceholder = 'Email-i juaj për përditësimet'; nlButton = 'Rrituni bashkë me ne'
          cfButton = 'Kërkoni një ofertë'; cfPlaceholder = 'Adresa juaj email'
          waHref = 'https://wa.me/355696085288?text=P%C3%ABrsh%C3%ABndetje%20MarketingPro%2C%20kam%20nj%C3%AB%20biznes%20dhe%20dua%20nj%C3%AB%20ofert%C3%AB%20p%C3%ABr%20marketingun.'
          nlNote = "Faleminderit! Do t'ju kontaktojmë së shpejti."
          rights = 'Të gjitha të drejtat e rezervuara.'
          lbZoom = 'Zmadhoni imazhin'; lbClose = 'Mbyllni'
          lbPrev = 'Imazhi i mëparshëm'; lbNext = 'Imazhi tjetër' }
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
    # ANCHORED, deliberately. These two rules used to match on the button tag and
    # on `placeholder=... autocomplete="email"` alone, and [regex]::Replace hits
    # EVERY match in the document. contact.html has two of each - the newsletter
    # in the footer and the contact form in <main> - so the newsletter strings
    # overwrote the contact form's, in all four languages, on every build. The
    # contact form's submit button therefore read "Join us for growth" and its
    # email field "Your email for updates": the site was inviting job seekers on
    # the exact form meant for clients. Anchoring on the two ids keeps them apart.
    @{ rx = '(<input class="newsletter__input"[^>]*>\s*<button class="btn btn--green" type="submit">)[^<]*(</button>)'; val = $C.nlButton },
    @{ rx = '(<p class="newsletter__note" data-newsletter-note hidden>)[^<]*(</p>)';        val = $C.nlNote },
    @{ rx = '(id="news-email"[^>]*placeholder=")[^"]*(")';                                  val = $C.nlPlaceholder },
    @{ rx = '(<div class="contact-form-card__actions">\s*<button class="btn btn--green" type="submit">)[^<]*(</button>)'; val = $C.cfButton },
    @{ rx = '(id="cf-email"[^>]*placeholder=")[^"]*(")';                                    val = $C.cfPlaceholder },
    # The footer WhatsApp button is the most discoverable contact path on the
    # site - raw HTML, all 112 pages - and it opened a BLANK chat, so the one
    # surface a stranger is most likely to use carried no intent signal at all.
    # Now it prefills the same client-intent message the floating button does.
    @{ rx = '(<a class="btn btn--whatsapp" href=")[^"]*(")';                                 val = $C.waHref },
    @{ rx = '(<span data-year>[^<]*</span>\. )[^<]*(</p>)';                                 val = $C.rights },
    # The gallery and lightbox controls live OUTSIDE <main>, which is why they
    # were missed here: they read as page content but behave as chrome. That
    # gap cost the three trees their translations the first time portfolio.html
    # was re-ported with -Force, because the porter rebuilds from English and
    # nothing put these back. Generating them means it cannot happen again.
    @{ rx = '(<button class="gallery__item" type="button" aria-label=")[^"]*(")';            val = $C.lbZoom },
    @{ rx = '(data-lightbox-close aria-label=")[^"]*(")';                                    val = $C.lbClose },
    @{ rx = '(data-lightbox-prev aria-label=")[^"]*(")';                                     val = $C.lbPrev },
    @{ rx = '(data-lightbox-next aria-label=")[^"]*(")';                                     val = $C.lbNext }
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
