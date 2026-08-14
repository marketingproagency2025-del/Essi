# Albanian (sq) translation guide — MarketingPro

Derived from the Albanian already shipped in this workspace (Iglisi Watch, 166 pages;
Intimo Bruna; Victoria Boutique), not invented. Where those sites disagree, this file
picks one and that pick is binding, so four translators do not produce four house styles.

## Register: formal `Ju`, everywhere

Measured across the corpus: formal `juaj`/`tuaj` outnumber informal `yt`/`tënd` by about
11 to 1. MarketingPro sells to business owners, which is the strongest case for `Ju`.

- Prose: formal throughout. `shërbimet tuaja`, `biznesi juaj`, `ekipi juaj`.
- **Buttons and CTAs: formal too.** The shops mix in clipped informal labels
  (`Lexo artikullin`, `Shfleto orët`) while their prose stays formal. That inconsistency
  is the weakest seam in those sites. Do not copy it. Use `Lexoni`, `Na kontaktoni`,
  `Kërkoni një ofertë`.
- Never mix `Ju` and `ti` inside one page, let alone one sentence.

## Fixed terms — use exactly these

| English | Albanian |
|---|---|
| Home | Kreu |
| Services | Shërbimet |
| Portfolio | Portfolio |
| Blog | Blog |
| About | Rreth Nesh |
| Contact | Kontakt |
| Frequently Asked Questions | Pyetje të Shpeshta |
| Skip to content | Kaloni te përmbajtja kryesore |
| All rights reserved | Të gjitha të drejtat e rezervuara |
| Open menu / Close menu | Hapni menunë / Mbyllni menunë |
| Change language | Ndryshoni gjuhën |
| Back to Blog | Kthehuni te Blogu |
| Keep Reading | Vazhdoni leximin |
| The Short Version | Shkurtimisht |
| Read more | Lexoni më shumë |
| Send Your Message | Dërgoni mesazhin |
| Your First Name | Emri Juaj |
| Your Email Address | Adresa Email |
| Phone number | Numër Telefoni |
| Your Message | Mesazhi |
| Receive our newsletter | Merrni newsletter-in tonë |
| N min read | N min lexim |
| Get in touch | Na kontaktoni |
| Enlarge image | Zmadhoni imazhin |

> **Every control string above is the formal `Ju` imperative on purpose.** An earlier
> version of this table copied the informal forms used by the shops in this workspace
> (`Kalo`, `Hap`, `Ndrysho`, `Kthehu`) and three reviewers independently flagged the
> clash with the formal rule above. The rule wins: one register, everywhere, including
> `aria-label`s a screen reader speaks aloud.

## The qualify family: `kualifikoj`, and only that

**This is the brand promise, so it gets one word.** English uses `qualify` and its
relatives 89 times across the site and `filter` exactly six, one per page, always
beside a qualify. Albanian mirrors that on most pages and inverted it on two:
`sq/services-advertising.html` ran 10 `filtroj` to 0 `kualifikoj`, and
`sq/services-social-media.html` 8 to 0, on an English page that never says
"filter" at all. Both were live. A reader following a link from the portfolio
went from *we qualify every lead* to *every lead gets filtered*, which is a
different and smaller claim.

- `kualifikoj` / `i kualifikuar` / `kualifikimi` translate the qualify family,
  always.
- `filtroj` appears only where the English itself says "filter" - one bullet on
  the advertising page. **This holds regardless of which reads better in a
  given sentence**, for the same reason `guide-es.md` pins `calificar`: the word
  is a promise, not a stylistic choice, and consistency across 24 pages is worth
  more than the best word in any one of them.

## Loanwords stay English, with Albanian inflection

The corpus keeps `marketing`, `Blog`, `Shop`, `cookie-t`, `COD` in English and inflects
them. Extend that rather than inventing calques. Keep in English:

`marketing`, `SEO`, `social media`, `lead` / `leads`, `funnel`, `render`, `newsletter`,
`brand`, `Meta`, `Google`, `WhatsApp`, `online`, `remote-first`.

Write `marketing dixhital` for "digital marketing". Do **not** invent
`optimizim për motorët e kërkimit` for SEO.

## Mechanics

- **Diacritics.** `ë` and `ç` correct everywhere, including headings, `alt`, `aria-label`
  and meta descriptions. A dropped diacritic reads as illiterate, not as a typo. Write
  literal UTF-8 characters, never `&euml;` or `&ccedil;`. The gate fails on entities.
- **No em dashes.** Not `—`, not `&mdash;`, not `&#8212;`. Use a spaced hyphen, a comma
  or a full stop. The gate fails on these.
- **Dates**: `9 qershor 2026`. Day first, no comma, no ordinal, **month lower-case**
  (Albanian does not capitalise months; Iglisi capitalises them and is wrong).
  Months: janar, shkurt, mars, prill, maj, qershor, korrik, gusht, shtator, tetor,
  nëntor, dhjetor. Leave `datetime="2026-06-09"` untouched.
- **Numbers**: thousands separated by a dot, decimals by a comma. `18.300`, `0,7%`.
- No AI filler. Short sentences, plain verbs, matching the English source's energy.

## The founder's title must stay genderless

Client decision, 2026-08-10: do not assign a grammatical gender to Essi Papajorgji.
English "Founder" is genderless and hides the problem; Albanian, Italian and Spanish
do not. Use **verbs**, which do not inflect for gender in the third person, instead of
agent nouns.

| Do not write | Write |
|---|---|
| Themelues / Themeluese | Në krye të MarketingPro |
| Themeluesi i MarketingPro, i cili drejton... | Themeloi MarketingPro dhe drejton... |
| Njihuni me Themeluesin | Kush e themeloi MarketingPro |

Also avoid the gendered relative pronouns `i cili` / `e cila` when the antecedent is
Essi. Rephrase with a finite verb. The same applies to the JSON-LD Person description.
`"jobTitle": "Founder"` stays in English in every tree and needs no change.

## Never translate

`MarketingPro`, `MarketingPro Digital Marketing Agency`, `Essi Papajorgji`, testimonial
names (`Kristi P.`, `Marco S.`, `Emily Carter`), `commerciale@marketingpro-agency.com`,
`+355694702405`, every URL and `@id`, anchor fragments (`#social-media`, `#seo` …),
`Meta` / `Facebook` / `Instagram` / `Google`, `"contactType": "customer service"`,
JSON-LD `areaServed` country names and `knowsAbout` topics (these stay English in the
Italian tree too, correctly, because they are machine-readable fields).

Two `alt` texts quote words printed inside the photograph: `'Creativity, Express
Yourself'` and `'Happy Designing Folks'`. Translate the frame around them, leave the
quoted English alone. The Italian tree does exactly this.

If you translate a testimonial author's name, change the avatar initials to match.

## Caveat

These translations are model-produced. The workspace rule in `.claude/rules/writing.md`
is explicit: *"Never machine-translate a page and ship it."* A native Albanian speaker
should proofread before cut-over. Nothing here is a substitute for that.
