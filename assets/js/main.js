/* =========================================================
   MarketingPro — site interactions
   Vanilla JS, no dependencies. JS only toggles classes;
   all motion lives in CSS (and respects prefers-reduced-motion).
   ========================================================= */
(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- Locale ----------
     One resolver for the whole file. Reads <html lang> first and falls back to
     the URL prefix, so a page with a missing or wrong lang attribute still
     picks the right strings. Anything unrecognised lands on English. */
  var LANGS = ["en", "it", "es", "sq"];

  var lang = (function () {
    var attr = (document.documentElement.lang || "").toLowerCase().slice(0, 2);
    if (LANGS.indexOf(attr) > -1) return attr;
    var m = window.location.pathname.match(/^\/(it|es|sq)(\/|$)/);
    return m ? m[1] : "en";
  })();

  /* Every user-visible string the scripts produce, in one table.
     Adding a language means adding one block here, nothing else. */
  var STRINGS = {
    en: {
      name: "English",
      waPrefill: "Hi MarketingPro, I run a business and I'd like a quote for marketing work.",
      waLabel: "Chat with us",
      waAria: "Chat with us on WhatsApp",
      menuOpen: "Open menu",
      menuClose: "Close menu",
      mailSubject: "New enquiry",
      mailFrom: " from ",
      fName: "Name", fEmail: "Email", fPhone: "Phone", fMessage: "Message",
      mailStatus: "Opening your email app to send the message…",
      vidPlay: "Play video", vidUnmute: "Turn on sound", vidMute: "Turn off sound"
    },
    it: {
      name: "Italiano",
      waPrefill: "Ciao MarketingPro, ho un'azienda e vorrei un preventivo per il marketing.",
      waLabel: "Scrivici",
      waAria: "Scrivici su WhatsApp",
      menuOpen: "Apri menu",
      menuClose: "Chiudi menu",
      mailSubject: "Nuova richiesta",
      mailFrom: " da ",
      fName: "Nome", fEmail: "Email", fPhone: "Telefono", fMessage: "Messaggio",
      mailStatus: "Apertura dell'app email per inviare il messaggio…",
      vidPlay: "Riproduci il video", vidUnmute: "Attiva l'audio", vidMute: "Disattiva l'audio"
    },
    es: {
      name: "Español",
      waPrefill: "Hola MarketingPro, tengo un negocio y quisiera un presupuesto de marketing.",
      waLabel: "Escríbenos",
      waAria: "Escríbenos por WhatsApp",
      menuOpen: "Abrir menú",
      menuClose: "Cerrar menú",
      mailSubject: "Nueva consulta",
      mailFrom: " de ",
      fName: "Nombre", fEmail: "Email", fPhone: "Teléfono", fMessage: "Mensaje",
      mailStatus: "Abriendo tu aplicación de correo para enviar el mensaje…",
      vidPlay: "Reproducir el vídeo", vidUnmute: "Activar el sonido", vidMute: "Desactivar el sonido"
    },
    sq: {
      name: "Shqip",
      waPrefill: "Përshëndetje MarketingPro, kam një biznes dhe dua një ofertë për marketingun.",
      waLabel: "Na shkruani",
      waAria: "Na shkruani në WhatsApp",
      menuOpen: "Hapni menunë",
      menuClose: "Mbyllni menunë",
      mailSubject: "Kërkesë e re",
      mailFrom: " nga ",
      fName: "Emri", fEmail: "Email", fPhone: "Telefoni", fMessage: "Mesazhi",
      mailStatus: "Po hapet aplikacioni i email-it për të dërguar mesazhin…",
      vidPlay: "Luani videon", vidUnmute: "Aktivizoni zërin", vidMute: "Çaktivizoni zërin"
    }
  };

  var t = STRINGS[lang] || STRINGS.en;

  /* ---------- Hero video, loaded only when it is wanted ----------
     The markup ships no <source>, so the 3.7 MB file is never fetched by
     default. It used to autoplay and loop for everyone, including visitors who
     had asked their OS for reduced motion: a WCAG 2.2.2 problem, not merely a
     weight one, since nothing on the page could pause it. It was also the
     single heaviest object on a phone.

     Attaching the source here means reduced-motion and small-screen visitors
     pay nothing at all. They still see the poster, which is preloaded anyway
     and is the LCP element. */
  (function () {
    var hero = document.querySelector("[data-hero-video]");
    if (!hero) return;
    var wide = window.matchMedia("(min-width: 861px)").matches;
    if (reduceMotion || !wide) return;

    var source = document.createElement("source");
    source.src = hero.getAttribute("data-hero-video");
    source.type = "video/mp4";
    hero.appendChild(source);
    hero.load();
    var started = hero.play();
    // Autoplay can still be refused (battery saver, data saver). The poster
    // stays visible, so a rejection needs no handling beyond not throwing.
    if (started && started.catch) { started.catch(function () {}); }
  })();

  /* ---------- Case-study video ----------
     Deliberately not reusing the hero block above. That one is
     querySelector - singular - so a second [data-hero-video] anywhere would be
     silently ignored, and the two have different jobs anyway: the hero is
     decorative, this is the evidence a portfolio page exists to show.

     Which means the hero's rule cannot simply be copied. The hero withholds
     itself from phones and from reduced-motion visitors and that costs them
     nothing, because it is wallpaper. Doing the same here would hide client
     work from every phone visitor. So the gate changes what the control means
     rather than whether the content is reachable:

       wide screen, motion allowed   autoplay muted, button offers sound
       anything else                 poster only, button offers play

     Either way nothing is fetched until it is wanted, and a tap that starts
     playback is a user gesture, so it is allowed to bring sound with it. */
  (function () {
    var frame = document.querySelector("[data-case-video]");
    if (!frame) return;
    var video = frame.querySelector("video");
    var button = frame.querySelector("[data-case-sound]");
    if (!video || !button) return;

    var src = video.getAttribute("data-src");
    var loaded = false;

    function attach() {
      if (loaded) return;
      var source = document.createElement("source");
      source.src = src;
      source.type = "video/mp4";
      video.appendChild(source);
      video.load();
      loaded = true;
    }

    function setState(state) {
      button.setAttribute("data-state", state);
      button.setAttribute("aria-label",
        state === "play" ? t.vidPlay : state === "muted" ? t.vidUnmute : t.vidMute);
    }

    function play() {
      var started = video.play();
      // Refusal is normal (battery saver, data saver, autoplay policy). The
      // poster is underneath, so there is nothing to repair beyond not throwing.
      if (started && started.catch) { started.catch(function () {}); }
    }

    var wide = window.matchMedia("(min-width: 861px)").matches;
    if (!reduceMotion && wide) {
      /* Not on load. This video is the third case study, roughly three screens
         down, and fetching it immediately cost every desktop visitor 3.8 MB
         whether or not they ever scrolled to it - measured: 4434 KB with it,
         579 KB without. So it waits until it is nearly in view, which is the
         same IntersectionObserver pattern the reveal animations already use.
         rootMargin starts the fetch 300px early so it is playing by the time it
         is actually looked at.

         No IntersectionObserver (old browser) means load it as before: worse to
         show a dead poster than to spend the bytes. */
      var start = function () {
        attach();
        video.muted = true;
        play();
        setState("muted");
      };
      if ("IntersectionObserver" in window) {
        setState("muted");
        var vio = new IntersectionObserver(function (entries, obs) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) { obs.unobserve(entry.target); start(); }
          });
        }, { rootMargin: "300px 0px" });
        vio.observe(frame);
      } else {
        start();
      }
    } else {
      setState("play");
    }

    button.addEventListener("click", function () {
      if (!loaded) {
        // First tap on a phone: load, unmute and play in one gesture.
        attach();
        video.muted = false;
        play();
        setState("sound");
        return;
      }
      video.muted = !video.muted;
      setState(video.muted ? "muted" : "sound");
    });
  })();

  /* ---------- Sticky header state on scroll ---------- */
  var header = document.querySelector("[data-header]");
  if (header) {
    var onScroll = function () {
      header.classList.toggle("is-scrolled", window.scrollY > 20);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ---------- Scroll progress bar ---------- */
  if (!reduceMotion) {
    var progress = document.createElement("div");
    progress.className = "scroll-progress";
    progress.setAttribute("aria-hidden", "true");
    document.body.appendChild(progress);
    var onProgress = function () {
      var max = document.documentElement.scrollHeight - window.innerHeight;
      var p = max > 0 ? window.scrollY / max : 0;
      progress.style.transform = "scaleX(" + Math.min(Math.max(p, 0), 1) + ")";
    };
    onProgress();
    window.addEventListener("scroll", onProgress, { passive: true });
    window.addEventListener("resize", onProgress, { passive: true });
  }

  /* ---------- Floating WhatsApp button ---------- */
  (function () {
    var wa = document.createElement("a");
    wa.className = "wa-float";
    wa.href = "https://wa.me/355696085288?text=" + encodeURIComponent(t.waPrefill);
    wa.target = "_blank";
    wa.rel = "noopener";
    wa.setAttribute("aria-label", t.waAria);
    wa.innerHTML =
      '<span class="wa-float__label">' + t.waLabel + '</span>' +
      '<svg class="wa-float__icon" viewBox="0 0 32 32" width="30" height="30" aria-hidden="true">' +
      '<path fill="currentColor" d="M16 3C9 3 3.3 8.7 3.3 15.7c0 2.4.7 4.7 1.9 6.7L3 29l6.8-2.1c1.9 1 4 1.6 6.2 1.6 7 0 12.7-5.7 12.7-12.7S23 3 16 3zm0 23c-1.9 0-3.8-.5-5.4-1.5l-.4-.2-4 1.2 1.2-3.9-.3-.4a10.4 10.4 0 01-1.6-5.5c0-5.8 4.7-10.5 10.5-10.5S26.5 9.9 26.5 15.7 21.8 26 16 26zm5.9-7.8c-.3-.2-1.9-1-2.2-1.1-.3-.1-.5-.2-.7.2-.2.3-.8 1-1 1.2-.2.2-.4.2-.7.1-1.7-.9-2.9-1.6-4-3.5-.3-.5.3-.5.8-1.6.1-.2 0-.4 0-.5-.1-.2-.7-1.7-1-2.3-.3-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.2.2 2.1 3.3 5.2 4.6 2 .8 2.7.9 3.7.8.6-.1 1.9-.8 2.2-1.5.3-.8.3-1.4.2-1.5-.1-.2-.3-.2-.6-.4z"/>' +
      '</svg>';
    document.body.appendChild(wa);
  })();

  /* ---------- Card spotlight (desktop pointers only) ---------- */
  if (!reduceMotion && window.matchMedia("(hover: hover) and (pointer: fine)").matches) {
    document.querySelectorAll(".feature-card, .client-card").forEach(function (card) {
      card.addEventListener("pointermove", function (e) {
        var r = card.getBoundingClientRect();
        card.style.setProperty("--mx", (e.clientX - r.left) + "px");
        card.style.setProperty("--my", (e.clientY - r.top) + "px");
      });
    });
  }

  /* ---------- Mobile navigation ---------- */
  var toggle = document.querySelector("[data-nav-toggle]");
  var menu = document.querySelector("[data-nav-menu]");
  if (toggle && menu) {
    var setMenu = function (open) {
      menu.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? t.menuClose : t.menuOpen);
    };
    toggle.addEventListener("click", function () {
      setMenu(!menu.classList.contains("is-open"));
    });
    // Close when a link is tapped
    menu.addEventListener("click", function (e) {
      if (e.target.closest(".nav__link")) setMenu(false);
    });
    // Close on Escape
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") setMenu(false);
    });
    // Reset when resizing up to desktop
    window.addEventListener("resize", function () {
      if (window.innerWidth > 860) setMenu(false);
    });
  }

  /* ---------- Language switcher ----------
     The menu is built from the page's own <link rel="alternate" hreflang>
     tags, which are the single source of truth for what translations exist.
     The markup ships only the current language as a no-JS fallback, so adding
     a language is two <link> tags plus one entry in STRINGS, never an edit to
     64 HTML files.

     hreflang hrefs are absolute. We navigate by pathname so the switcher keeps
     working on localhost instead of jumping to the production domain.

     That pathname must be parsed out of the href, NOT read off the element.
     This used to be `alts[i].pathname || "/"`, which looks right and is not:
     .pathname comes from HTMLHyperlinkElementUtils, which <a> and <area>
     implement and <link> does not. So it was undefined on every iteration, the
     || fallback fired every time, and every entry in the menu pointed at "/".
     The switcher was live in that state: whatever page you were reading, in
     whatever language, choosing another language sent you to the homepage. It
     looked completely correct in the markup, because the labels were right and
     only the hrefs were wrong. */
  var langMenu = document.querySelector("[data-lang-menu]");
  if (langMenu) {
    var alts = document.querySelectorAll('link[rel="alternate"][hreflang]');
    var items = [];
    var sawCurrent = false;

    for (var i = 0; i < alts.length; i++) {
      var code = (alts[i].getAttribute("hreflang") || "").toLowerCase();
      if (code === "x-default" || !STRINGS[code]) continue;
      if (code === lang) sawCurrent = true;
      var raw = alts[i].getAttribute("href") || "/";
      var path;
      try {
        path = new URL(raw, window.location.href).pathname;
      } catch (e) {
        path = raw;                     // relative already, or unparseable
      }
      items.push({ code: code, href: path });
    }

    // A page can legitimately be absent from its own hreflang set: translations
    // that are finished but not yet published are held back that way. Without
    // this the built menu would drop the language the reader is actually on and
    // nothing would be marked current, so keep the page itself at the front.
    if (items.length && !sawCurrent) {
      items.unshift({ code: lang, href: window.location.pathname });
    }

    if (items.length) {
      var html = "";
      for (var j = 0; j < items.length; j++) {
        var isCurrent = items[j].code === lang;
        html +=
          '<li role="none"><a class="lang__item' + (isCurrent ? " is-active" : "") + '"' +
          ' role="menuitem"' + (isCurrent ? ' aria-current="true"' : "") +
          ' hreflang="' + items[j].code + '"' +
          ' href="' + items[j].href + '">' + STRINGS[items[j].code].name + "</a></li>";
      }
      langMenu.innerHTML = html;
    }
  }

  /* ---------- Language switcher dropdown ---------- */
  var langSwitch = document.querySelector("[data-lang-switch]");
  if (langSwitch) {
    var langToggle = langSwitch.querySelector("[data-lang-toggle]");
    if (langToggle) {
      var setLang = function (open) {
        langSwitch.classList.toggle("is-open", open);
        langToggle.setAttribute("aria-expanded", String(open));
      };
      langToggle.addEventListener("click", function (e) {
        e.stopPropagation();
        setLang(!langSwitch.classList.contains("is-open"));
      });
      document.addEventListener("click", function (e) {
        if (!langSwitch.contains(e.target)) setLang(false);
      });
      document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") setLang(false);
      });
    }
  }

  /* ---------- Scroll reveal ---------- */
  var revealEls = document.querySelectorAll("[data-reveal]");
  // Apply stagger delay from data attribute
  revealEls.forEach(function (el) {
    var d = el.getAttribute("data-reveal-delay");
    if (d) el.style.setProperty("--reveal-delay", d);
  });

  if (reduceMotion || !("IntersectionObserver" in window)) {
    revealEls.forEach(function (el) { el.classList.add("in-view"); });
  } else {
    var io = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("in-view");
          obs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15, rootMargin: "0px 0px -8% 0px" });
    revealEls.forEach(function (el) { io.observe(el); });
  }

  /* ---------- Newsletter (front-end only for now) ---------- */
  var form = document.querySelector("[data-newsletter]");
  if (form) {
    var note = form.querySelector("[data-newsletter-note]");
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var email = form.querySelector('input[type="email"]');
      if (email && !email.checkValidity()) { email.reportValidity(); return; }
      if (note) { note.hidden = false; }
      form.reset();
    });
  }

  /* ---------- Footer year ---------- */
  var year = document.querySelector("[data-year]");
  if (year) year.textContent = new Date().getFullYear();

  /* ---------- Gallery lightbox (portfolio) ---------- */
  var gallery = document.querySelector("[data-gallery]");
  var lightbox = document.querySelector("[data-lightbox]");
  if (gallery && lightbox) {
    var lbImg = lightbox.querySelector("[data-lightbox-img]");
    var closeBtn = lightbox.querySelector("[data-lightbox-close]");
    var items = Array.prototype.slice.call(gallery.querySelectorAll(".gallery__item"));
    var current = 0;
    var lastFocused = null;

    var show = function (i) {
      current = (i + items.length) % items.length;
      var img = items[current].querySelector("img");
      if (!img) return;
      lbImg.src = img.currentSrc || img.src;
      lbImg.alt = img.alt || "";
    };

    var open = function (i) {
      lastFocused = document.activeElement;
      show(i);
      lightbox.classList.add("is-open");
      lightbox.setAttribute("aria-hidden", "false");
      document.body.style.overflow = "hidden";
      if (closeBtn) closeBtn.focus();
    };

    var close = function () {
      lightbox.classList.remove("is-open");
      lightbox.setAttribute("aria-hidden", "true");
      document.body.style.overflow = "";
      // removeAttribute, not src = "": an empty src resolves against the
      // document URL, so the browser can re-request the page as an image.
      lbImg.removeAttribute("src");
      if (lastFocused && lastFocused.focus) lastFocused.focus();
    };

    items.forEach(function (item, i) {
      item.addEventListener("click", function () { open(i); });
    });
    lightbox.querySelectorAll("[data-lightbox-close]").forEach(function (el) {
      el.addEventListener("click", close);
    });
    var nextEl = lightbox.querySelector("[data-lightbox-next]");
    var prevEl = lightbox.querySelector("[data-lightbox-prev]");
    if (nextEl) nextEl.addEventListener("click", function () { show(current + 1); });
    if (prevEl) prevEl.addEventListener("click", function () { show(current - 1); });

    document.addEventListener("keydown", function (e) {
      if (!lightbox.classList.contains("is-open")) return;
      if (e.key === "Escape") close();
      else if (e.key === "ArrowRight") show(current + 1);
      else if (e.key === "ArrowLeft") show(current - 1);
    });
  }

  /* ---------- Contact form (mailto) ---------- */
  var contactForm = document.querySelector("[data-contact-form]");
  if (contactForm) {
    var cfNote = contactForm.querySelector("[data-form-note]");
    var setNote = function (msg, ok) {
      if (!cfNote) return;
      cfNote.textContent = msg;
      cfNote.hidden = false;
      cfNote.classList.toggle("is-ok", !!ok);
      cfNote.classList.toggle("is-error", !ok);
    };
    contactForm.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!contactForm.checkValidity()) { contactForm.reportValidity(); return; }
      var val = function (n) {
        var el = contactForm.querySelector('[name="' + n + '"]');
        return el ? el.value.trim() : "";
      };
      var name = val("name"), email = val("email"), phone = val("phone"), message = val("message");
      var subject = t.mailSubject + (name ? t.mailFrom + name : "") + " - MarketingPro";
      var body =
        t.fName + ": " + (name || "-") + "\n" +
        t.fEmail + ": " + (email || "-") + "\n" +
        t.fPhone + ": " + (phone || "-") + "\n\n" +
        t.fMessage + ":\n" + message + "\n";
      var href = "mailto:commerciale@marketingpro-agency.com" +
        "?subject=" + encodeURIComponent(subject) +
        "&body=" + encodeURIComponent(body);
      window.location.href = href;
      setNote(t.mailStatus, true);
    });
  }
})();
