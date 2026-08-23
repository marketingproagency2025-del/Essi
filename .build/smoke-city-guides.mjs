/**
 * Browser smoke test for the three new city guides, in all four trees, plus the four blog
 * indexes that now link to them.
 *
 * verify-langs.ps1 reads the HTML as text. It cannot tell you that a page 404s under
 * Cloudflare's extensionless routing, that the CSP blocks a script the page needs, that a card
 * headline disagrees with the H1 it points at, or that the layout overflows on a phone. That is
 * what this is for, and every one of those has actually bitten this site before.
 *
 * Serve first, in another shell:
 *     python .build/serve.py 8787
 *
 * Then:
 *     node smoke_cities.mjs [port]
 *
 * Checks, per page: HTTP 200, zero console errors, zero failed requests, no horizontal overflow
 * at 1366 and at 390, an <h1> present, and the hero image actually decoded rather than 404ing
 * into a broken box. Per index: every new card's headline equals the H1 of the page it links to,
 * exactly one card image carries fetchpriority, and every other card image is loading="lazy".
 */
import { createRequire } from "module";

const require = createRequire(
  "c:/Users/aceto/OneDrive/Desktop/web and apps/Minafy/package.json"
);
const { chromium } = require("playwright");

const PORT = process.argv[2] || "8787";
const BASE = `http://127.0.0.1:${PORT}`;
const TREES = ["", "/it", "/es", "/sq"];
const SLUGS = ["blog-roma", "blog-lugano", "blog-ticino"];

let pass = 0;
let fail = 0;
const failures = [];

function check(ok, label) {
  if (ok) {
    pass++;
  } else {
    fail++;
    failures.push(label);
  }
  return ok;
}

/** Console errors and failed requests, collected per navigation. */
function watch(page) {
  const errs = [];
  const dead = [];
  page.on("console", (m) => {
    if (m.type() === "error") errs.push(m.text());
  });
  page.on("pageerror", (e) => errs.push(String(e)));
  page.on("requestfailed", (r) => dead.push(`${r.url()} ${r.failure()?.errorText}`));
  page.on("response", (r) => {
    if (r.status() >= 400) dead.push(`${r.status()} ${r.url()}`);
  });
  return { errs, dead };
}

async function overflow(page, width) {
  await page.setViewportSize({ width, height: 900 });
  await page.waitForTimeout(120);
  return page.evaluate(() => ({
    scroll: document.documentElement.scrollWidth,
    client: document.documentElement.clientWidth,
  }));
}

const browser = await chromium.launch();

// ---------------------------------------------------------------- the 12 new pages
const h1s = new Map(); // url -> h1 text, reused by the index check below

for (const tree of TREES) {
  for (const slug of SLUGS) {
    const url = `${BASE}${tree}/${slug}`;
    const page = await browser.newPage();
    const { errs, dead } = watch(page);
    const res = await page.goto(url, { waitUntil: "networkidle" });

    const label = `${tree || "/en"}/${slug}`;
    check(res && res.status() === 200, `${label} HTTP ${res && res.status()}`);

    const h1 = (await page.textContent("h1").catch(() => null))?.trim() || "";
    check(h1.length > 0, `${label} has an h1`);
    h1s.set(`${tree}/${slug}`, h1);

    // the hero must actually have decoded; a 404 image still yields an <img> element
    const heroOk = await page.evaluate(() => {
      const i = document.querySelector(".article-hero__media img");
      return !!i && i.complete && i.naturalWidth > 0;
    });
    check(heroOk, `${label} hero image decoded`);

    for (const w of [1366, 390]) {
      const { scroll, client } = await overflow(page, w);
      check(scroll <= client + 1, `${label} no h-overflow at ${w} (${scroll} vs ${client})`);
    }

    check(errs.length === 0, `${label} console errors: ${errs.slice(0, 2).join(" | ")}`);
    check(dead.length === 0, `${label} failed requests: ${dead.slice(0, 2).join(" | ")}`);

    await page.close();
  }
}

// ---------------------------------------------------------------- the 4 blog indexes
for (const tree of TREES) {
  const url = `${BASE}${tree}/blog`;
  const page = await browser.newPage();
  const { errs, dead } = watch(page);
  const res = await page.goto(url, { waitUntil: "networkidle" });
  const label = `${tree || "/en"}/blog`;

  check(res && res.status() === 200, `${label} HTTP ${res && res.status()}`);
  check(errs.length === 0, `${label} console errors: ${errs.slice(0, 2).join(" | ")}`);
  check(dead.length === 0, `${label} failed requests: ${dead.slice(0, 2).join(" | ")}`);

  for (const w of [1366, 390]) {
    const { scroll, client } = await overflow(page, w);
    check(scroll <= client + 1, `${label} no h-overflow at ${w} (${scroll} vs ${client})`);
  }

  // card headline must equal the H1 of the page it points at
  for (const slug of SLUGS) {
    const href = `${tree}/${slug}`;
    const cardTitle = await page.evaluate((h) => {
      const a = document.querySelector(`.article-card__link[href="${h}"]`);
      return a ? a.querySelector(".article-card__title")?.textContent.trim() : null;
    }, href);
    check(cardTitle !== null, `${label} has a card for ${slug}`);
    if (cardTitle !== null) {
      check(
        cardTitle === h1s.get(href),
        `${label} card headline matches H1 for ${slug}\n      card: ${cardTitle}\n      h1:   ${h1s.get(href)}`
      );
    }
  }

  // the LCP rule: exactly one fetchpriority, and it is the first card; the rest are lazy
  const imgs = await page.evaluate(() =>
    [...document.querySelectorAll(".articles--blog .article-card__media img")].map((i) => ({
      fp: i.getAttribute("fetchpriority"),
      loading: i.getAttribute("loading"),
    }))
  );
  check(imgs.length > 0, `${label} has card images`);
  check(
    imgs.filter((i) => i.fp === "high").length === 1 && imgs[0].fp === "high",
    `${label} exactly one fetchpriority, on the first card`
  );
  check(
    imgs.slice(1).every((i) => i.loading === "lazy"),
    `${label} every card after the first is loading="lazy"`
  );
  check(!imgs[0].loading, `${label} first card omits loading`);

  await page.close();
}

await browser.close();

console.log(`\n  ${pass} passed, ${fail} failed`);
if (fail) {
  console.log("\n  FAILURES:");
  for (const f of failures) console.log(`    - ${f}`);
  process.exit(1);
}
console.log("  all green");
