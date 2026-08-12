# Spanish (es) translation guide — MarketingPro

Target: **neutral international Spanish**. The site serves Europe and the United States,
so the copy has to read naturally in Spain, Latin America and to US Hispanic readers.
hreflang is plain `es`, not `es-ES`, and the copy must earn that.

## Register: informal `tú`

Matches the existing Italian, which is informal `tu` throughout (`il tuo team commerciale`,
`Raccontaci il tuo obiettivo`). Spanish marketing copy carries `tú` comfortably.

- Address the reader as `tú`: `tu equipo`, `tu negocio`, `tus clientes`.
- Plural is **`ustedes`, never `vosotros`.** `vosotros` is Spain-only and reads foreign
  to most of the audience.
- Imperatives: `Contáctanos`, `Descubre`, `Escríbenos`. Not `Contáctenos`.

## Neutral vocabulary — avoid region-locked words

| Avoid | Use |
|---|---|
| ordenador (Spain) / computadora (LatAm) | equipo, or rephrase |
| móvil (Spain) / celular (LatAm) | teléfono |
| **coger** (vulgar in much of LatAm) | tomar, conseguir, elegir |
| vosotros, os, vuestro | ustedes, les, su |
| vale, guay, chulo | bien, excelente |
| zumo | jugo, or rephrase |

## Fixed terms — use exactly these

| English | Spanish |
|---|---|
| Home | Inicio |
| Services | Servicios |
| Portfolio | Portfolio |
| Blog | Blog |
| About | Quiénes Somos |
| Contact | Contacto |
| Frequently Asked Questions | Preguntas Frecuentes |
| Skip to content | Saltar al contenido |
| All rights reserved | Todos los derechos reservados |
| Open menu / Close menu | Abrir menú / Cerrar menú |
| Change language | Cambiar idioma |
| Back to Blog | Volver al Blog |
| Keep Reading | Sigue leyendo |
| The Short Version | En resumen |
| Read more | Leer más |
| Send Your Message | Envía tu mensaje |
| Your First Name | Tu nombre |
| Your Email Address | Tu correo electrónico |
| Phone number | Número de teléfono |
| Your Message | Tu mensaje |
| Receive our newsletter | Recibe nuestra newsletter |
| N min read | N min de lectura |
| Get in touch | Escríbenos |
| Enlarge image | Ampliar imagen |
| Close / Previous image / Next image | Cerrar / Imagen anterior / Imagen siguiente |

## Industry vocabulary

Unlike Albanian, Spanish has settled native terms for most of this. Use them:

- social media → **redes sociales**
- sales funnel → **embudo de ventas**
- website → **sitio web**
- advertising campaigns → **campañas publicitarias**
- photo and video editing → **edición de foto y vídeo**
- print catalogues → **catálogos impresos**
- photorealistic renders → **renders fotorrealistas**
- lead generation → **generación de leads**

Keep in English: `marketing`, `SEO`, `lead` / `leads`, `render`, `newsletter`, `Meta`,
`Google`, `WhatsApp`, `Meta Ads`, `Google Ads`, `remote-first`. `marketing digital` is
the normal Spanish form and is what to use for "digital marketing".

## Mechanics

- **Accents and ñ correct everywhere**, including `alt`, `aria-label`, `placeholder`,
  `<title>` and meta descriptions. Literal UTF-8, never `&eacute;` or `&ntilde;`.
  The gate fails on entities.
- **Opening punctuation**: `¿` and `¡` are mandatory. `¿Quieres nuevos clientes?`
- **No em dashes.** Not `—`, not `&mdash;`. Use a comma, a colon or a spaced hyphen.
  The gate fails on these.
- **Dates**: `9 de junio de 2026`. Month lower-case. Months: enero, febrero, marzo,
  abril, mayo, junio, julio, agosto, septiembre, octubre, noviembre, diciembre.
  Leave `datetime="2026-06-09"` untouched.
- **Numbers**: thousands separated by a dot, decimals by a comma. `1.764,61`.
- Spanish runs 15-25% longer than English. Watch the CTA buttons, the longest is
  `Turn your audience into customers` at 33 characters, and `feature-card__title`.
  Prefer the shorter of two good options.

## One word for the brand promise: `calificar`

Qualification is what this agency sells, so the term cannot drift. English uses
qualify / qualified / qualification 28 times. The word "filter" appears six times, but only once in a
position that matters: the hero line "We Call, Filter, and Deliver". Spanish mirrors that split:

- `calificar`, `calificado`, `calificación` render every qualify-family word. **Not**
  `cualificar` (Spain-marked) and **not** `filtrar`.
- `filtrar` appears in exactly one place, the hero, translating "Filter". **This holds
  regardless of what the English does elsewhere.** An earlier version of this guide said
  English used "filter" only once; it uses it six times (about, article-1, blog-advertising,
  blog-renders, index, services-advertising). The rule is a decision about Spanish, not an
  observation about English, so the other five all become `calificar`.
- "raw leads" is `leads sin calificar`.

The first Spanish pass split this three ways across three pages, `filtrados` on the
homepage, `calificados` on services and `cualificado` on about, which is why it is
pinned here.

## The founder's title must stay genderless

Client decision, 2026-08-10: do not assign a grammatical gender to Essi Papajorgji.
English "Founder" is genderless and hides the problem; Spanish does not. Use **verbs**,
which do not inflect for gender in the third person, instead of agent nouns.

| Do not write | Write |
|---|---|
| Fundador / Fundadora | Al frente de MarketingPro |
| Fundador de MarketingPro, que dirige... | Fundó MarketingPro y dirige... |
| Conoce al Fundador | Quién fundó MarketingPro |

Avoid any adjective or participle that would have to agree with Essi. Rephrase with a
finite verb. The same applies to the JSON-LD Person description. `"jobTitle": "Founder"`
stays in English in every tree and needs no change.

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
is explicit: *"Never machine-translate a page and ship it."* A native Spanish speaker
should proofread before cut-over. Nothing here is a substitute for that.
