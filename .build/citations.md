# NAP for citations — paste these exact strings

A citation only counts if it matches. Google resolves a business by agreeing
strings across sources; a second phone format or a translated city name reads as
a second business and the signals split instead of stacking. These values come
from the site's `#organization` node, so copy them, never retype them.

    Name:     MarketingPro
    Category: Digital marketing agency
    City:     Durrës            <- with the ë, always. Not "Durres", not "Durazzo"
    Country:  Albania
    Phone:    NOT SETTLED       <- the node lists two numbers, +355 69 608 5288 first
                                   (the one the contact page leads with) and
                                   +355 69 470 2405 (the footer's). Listings take ONE,
                                   in international format, once the owner picks it
                                   (decision N1 in _notes/link-targets.md). Until then
                                   no listing is submitted.
    Email:    commerciale@marketingpro-agency.com
    Website:  https://www.marketingpro-agency.com/
    Hours:    Mon-Fri 09:00-17:00
    Founded:  2024

Short description (fits most directory fields, 148 chars):

    Digital marketing agency based in Durrës, Albania. Social media, Meta and
    Google ads, websites, SEO. Every lead called and qualified before handover.

## Where to place them, in order of value

1. **Google Business Profile** — already exists. The highest-value action left is
   not a new listing, it is **reviews on the one you have**. The house GEO doc
   ranks review-platform gravity *above* on-site copy: a weak review profile
   means exclusion from AI answers no matter how good the site is.
   Ask every past client. Fly System, OF Outdoorkitchen, OFYR Italia and Rika are four you can ask today.

   **Nobody has written down how many reviews the profile actually has, or who has
   already been asked.** Record both here with the date the next time you look. The
   identical file for another client said "four clients have never been asked",
   which was read eight days later as "the profile has zero reviews" and repeated
   as fact for a whole session. It had nine. Who was asked and what the profile
   shows are different statements, and neither survives without a date.
2. **Bing Places** — the Bing equivalent, and Bing is what ChatGPT Search reads.
3. **Instagram + Facebook bios** — link the site. Nofollow, but crawled fast, and
   they confirm the entity against `sameAs` in the schema.
4. **Albanian directories** — free, and they build the local entity Google needs
   before it will trust a Durrës address. Checked 2026-11-01 and 2026-11-04, the five
   listed here before are gone: biznes.al (account suspended), alb-biz.com (parked),
   shqiperia.com (a news portal, no directory), gjejbiznes.al (the domain no longer
   resolves) and yellowpages.al (502, nothing archived since 2023). What is left:
   - Durrës chamber of commerce: its pages link every website with a followed link;
     whether it lists a business without membership, and the street address it
     needs, are still open (see _notes/round-2.md)
5. **LinkedIn company page** — if one exists, the website field is a real link.

## The rule

Same name, same phone format, same city spelling, everywhere. If a directory
will not accept `ë`, leave the field blank rather than writing `Durres` — a
missing field costs nothing, a contradicting one costs the match.
