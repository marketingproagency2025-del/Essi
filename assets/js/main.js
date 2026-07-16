/* =========================================================
   MarketingPro — homepage interactions
   Vanilla JS, no dependencies. JS only toggles classes;
   all motion lives in CSS (and respects prefers-reduced-motion).
   ========================================================= */
(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

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
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
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
      lbImg.src = "";
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
      var isIT = document.documentElement.lang === "it";
      var subject = (isIT ? "Nuova richiesta" : "New enquiry") +
        (name ? (isIT ? " da " : " from ") + name : "") + " - MarketingPro";
      var body = isIT
        ? ("Nome: " + (name || "-") + "\n" +
           "Email: " + (email || "-") + "\n" +
           "Telefono: " + (phone || "-") + "\n\n" +
           "Messaggio:\n" + message + "\n")
        : ("Name: " + (name || "-") + "\n" +
           "Email: " + (email || "-") + "\n" +
           "Phone: " + (phone || "-") + "\n\n" +
           "Message:\n" + message + "\n");
      var href = "mailto:commerciale@marketingpro-agency.com" +
        "?subject=" + encodeURIComponent(subject) +
        "&body=" + encodeURIComponent(body);
      window.location.href = href;
      setNote(isIT
        ? "Apertura dell'app email per inviare il messaggio…"
        : "Opening your email app to send the message…", true);
    });
  }
})();
