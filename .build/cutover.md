# Cut-over runbook

How to take a translated language tree from held to live. Written after a dry run that
promoted Albanian, broke the gate in 96 places, and got reverted. Follow the order.

## The rule that the dry run existed to find

**Always regenerate all four trees, never only the one you are promoting.**

The hreflang set for a slug is shared by every language version of that page. Promote
Albanian by rewriting only `en, it, sq` and the sixteen Spanish pages keep advertising the
old three-link set, so reciprocity breaks in both directions and the gate fails 96 times.

Both `fix-head.ps1` and `fix-nav.ps1` now default to all four trees precisely so this
cannot be got wrong. Pass `-Trees` only when you have a reason, and then know why.

## Steps

1. **Confirm the tree is actually finished.** Every one of the 16 slugs translated *and*
   reviewed, and the native proofread done. For Albanian that means working through
   `.build/proofread-notes-sq.md`; this is the step the whole staged rollout exists to
   protect, so do not skip it because the gate is green. The gate checks structure, not
   whether the Albanian reads like Albanian.

2. **Mark the tree live** in `.build/translation-status.json` by listing its slugs under
   its language key. Copy from `_slugs` to promote the whole tree at once. Partial
   promotion is supported and safe: unlisted pages simply stay held.

3. **Regenerate, in this order:**
   ```
   pwsh -Command '& "./.build/fix-nav.ps1"'      # all four trees by default
   pwsh -Command '& "./.build/fix-head.ps1"'     # all four trees by default
   pwsh -Command '& "./.build/gen-sitemap.ps1"'
   ```
   Invoke with `-Command '& ...'`, never `pwsh -File`: `-File` collapses an array argument
   like `es,sq` into a single string and every language lookup silently returns null.

4. **Gate.** `pwsh -Command '& "./.build/verify-langs.ps1"'` must end
   `RESULT: ALL PASSES CLEAN`. Fix failures; never loosen a check to make it pass.

5. **What changes automatically**, so do not hand-edit any of it: the promoted pages flip
   from `noindex, follow` to `index, follow, ...`; they enter `sitemap.xml`; they enter
   every page's hreflang set and `og:locale:alternate`; the language switcher starts
   offering them, because it builds itself from those hreflang links; and
   `WebSite.inLanguage` grows to include the new language once **all 16** of its pages are
   live. `ContactPoint.availableLanguage` does not change: it already lists all four,
   because it describes the team rather than the site.

## Still to do by hand at final cut-over

- **`llms.txt`** — it has a `## Italian` section pointing at `/it/`. Add the equivalent for
  Spanish and Albanian, and check the page list and language line still read true.
- **`site.webmanifest`** — currently `"lang": "en"` with `"start_url": "/"`. Fine as a
  single site-wide manifest. Only worth splitting per language if PWA install locale
  matters, which today it does not.
- **`robots.txt`** — no change needed, `Allow: /` already covers the new prefixes.
- **The vault** — `02 Clients/MarketingPro.md` records `languages: ["en","it"]` and every
  page note carries `translation_gap: false`. Both are generated, so a vault rebuild
  updates them. Per the workspace CLAUDE.md the `librarian` agent owns that build; do not
  run it from here. Landing only part of a tree will start flagging `translation_gap` on
  the rest, which is correct behaviour, not a bug.

## Verified end to end, 2026-08-12

The cut-over was simulated in full (`live: ["es","sq"]`, regenerate, gate) and reverted.
It produced a clean gate at 64 live pages, 64 sitemap urls, 320 alternates, and a working
four-language switcher that round-trips EN to IT to ES to SQ and back while staying on
the same page. Clean URLs were served locally with `.build/serve.py`, which mimics
Cloudflare's `html_handling`, and all four trees resolved with the right `<html lang>` and
translated titles; a genuinely missing path returned 404 rather than falling back.

So the procedure below is known to work. What is not yet done is the native proofread.


## Deploy

Routing needs no change: `wrangler.jsonc` serves the repo with
`assets.directory: "."` and Cloudflare's default `html_handling`, so `/es/services` maps
to `es/services.html` exactly as `/it/services` already does.

Three things to check before deploying:

- `wrangler.jsonc` lives **only on the remote branch `origin/cloudflare/workers-autoconfig`**,
  not on `main`, and that branch is behind. Its `.gitignore` also differs from main's by
  seven lines, and since the whole repo is served, that delta decides what actually ships.
  Reconcile the branches first.
- Confirm `originals/` (40 source images) is still excluded after any `.gitignore` merge.
- `not_found_handling` is unset, so there is no 404 page and no language-aware fallback.

Then verify live: `/es/services` and `/sq/services` resolve, the switcher lists four
languages and round-trips EN to IT to ES to SQ and back on the same page, and the floating
WhatsApp button prefills Spanish and Albanian text.
