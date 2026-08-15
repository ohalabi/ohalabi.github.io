/* =============================================================================
   research.js — filtering + detail drawer for the Research page.

   Progressive enhancement, deliberately:
   build.py renders all 27 project cards AND a full <article> of detail for each
   into the static HTML. Without JS you get every project and every image, and
   a card click jumps to that project's detail section further down the page —
   which is also what a crawler indexes. With JS, the detail sections are
   hidden and reused as the drawer's contents, so nothing is duplicated between
   the markup and a JS data blob.
   ============================================================================= */
(function () {
  "use strict";

  var grid    = document.getElementById("project-grid");
  var details = document.getElementById("project-details");
  var drawer  = document.getElementById("drawer");
  var scrim   = document.getElementById("scrim");
  if (!grid || !details || !drawer) return;

  // Signal to CSS that the detail sections can be hidden — only once we know
  // the drawer script actually ran.
  document.documentElement.classList.add("js-drawer");

  var cards   = Array.prototype.slice.call(grid.querySelectorAll(".pcard"));
  var count   = document.getElementById("result-count");
  var qInput  = document.getElementById("q");
  var dScroll = document.getElementById("drawer-scroll");
  var dKicker = document.getElementById("drawer-kicker");

  var state   = { theme: "all", cat: "all", q: "" };
  var visible = [];      // slugs currently shown, in DOM order
  var openId  = null;
  var lastFocus = null;

  /* ---------------------------------------------------------------- filter */
  function matches(card) {
    if (state.theme !== "all" && card.dataset.theme !== state.theme) return false;
    if (state.cat   !== "all" && card.dataset.cat   !== state.cat)   return false;
    if (state.q && card.dataset.search.indexOf(state.q) === -1)      return false;
    return true;
  }

  function render() {
    visible = [];
    cards.forEach(function (c) {
      var ok = matches(c);
      c.hidden = !ok;
      if (ok) visible.push(c.dataset.id);
    });

    var empty = document.getElementById("empty-state");
    if (empty) empty.hidden = visible.length > 0;

    if (count) {
      var bits = [visible.length + (visible.length === 1 ? " project" : " projects")];
      if (state.theme !== "all") bits.push(labelOf("theme", state.theme));
      if (state.cat   !== "all") bits.push(labelOf("cat", state.cat));
      if (state.q)               bits.push("“" + state.q + "”");
      count.textContent = bits.join(" · ");
    }
  }

  function labelOf(kind, val) {
    var chip = document.querySelector('.chip[data-kind="' + kind + '"][data-val="' + val + '"]');
    if (!chip) return val;
    return chip.textContent.replace(/\s*\d+\s*$/, "").trim();
  }

  /* ---------------------------------------------------------------- drawer */
  function pagerButton(dir, slug) {
    var src = slug ? details.querySelector('[data-id="' + slug + '"] h2') : null;
    var title = src ? src.textContent : "—";
    return '<button class="' + (dir === "next" ? "nx" : "pv") + '"' +
      (slug ? ' data-go="' + slug + '"' : " disabled") + '>' +
      "<span>" + (dir === "next" ? "Next" : "Previous") + "</span>" +
      "<strong>" + title + "</strong></button>";
  }

  function open(id, push) {
    var src = details.querySelector('[data-id="' + id + '"]');
    if (!src) return;
    if (push !== false) push = true;

    openId = id;
    lastFocus = document.activeElement;

    var i = visible.indexOf(id);
    var prev = i > 0 ? visible[i - 1] : null;
    var next = i > -1 && i < visible.length - 1 ? visible[i + 1] : null;

    drawer.setAttribute("data-theme", src.dataset.theme || "");
    if (dKicker) dKicker.innerHTML =
      '<span class="tag">' + (src.dataset.themeLabel || "") + "</span>";

    dScroll.innerHTML =
      '<div class="drawer-body">' + src.innerHTML +
      '<div class="pager">' + pagerButton("prev", prev) + pagerButton("next", next) + "</div>" +
      "</div>";
    dScroll.scrollTop = 0;

    drawer.classList.add("open");
    scrim.classList.add("open");
    document.body.classList.add("is-locked");
    drawer.focus();

    if (push && location.hash !== "#" + id) history.pushState({ id: id }, "", "#" + id);
    document.title = (src.querySelector("h2") ? src.querySelector("h2").textContent + " — " : "") +
      "Research — Osama Halabi";
  }

  function close(push) {
    if (push !== false) push = true;
    openId = null;
    drawer.classList.remove("open");
    scrim.classList.remove("open");
    document.body.classList.remove("is-locked");
    if (push && location.hash) history.pushState({}, "", location.pathname + location.search);
    document.title = "Research — Osama Halabi";
    if (lastFocus && lastFocus.isConnected) lastFocus.focus();
  }

  /* ---------------------------------------------------------------- events */
  document.addEventListener("click", function (e) {
    var chip = e.target.closest(".chip");
    if (chip) {
      state[chip.dataset.kind] = chip.dataset.val;
      chip.parentElement.querySelectorAll(".chip").forEach(function (c) {
        c.setAttribute("aria-pressed", String(c === chip));
      });
      render();
      return;
    }

    if (e.target.closest("#clear-filters")) {
      state.theme = state.cat = "all"; state.q = "";
      if (qInput) qInput.value = "";
      document.querySelectorAll(".chip").forEach(function (c) {
        c.setAttribute("aria-pressed", String(c.dataset.val === "all"));
      });
      render();
      return;
    }

    // plain left-click opens the drawer; modified clicks keep the real anchor
    var link = e.target.closest(".pcard h3 a");
    if (link && e.button === 0 && !e.metaKey && !e.ctrlKey && !e.shiftKey && !e.altKey) {
      e.preventDefault();
      open(link.closest(".pcard").dataset.id);
      return;
    }

    var go = e.target.closest("[data-go]");
    if (go) { open(go.dataset.go); return; }

    if (e.target.closest("#drawer-close") || e.target === scrim) { close(); return; }

    if (e.target.closest("#drawer-copy")) {
      var btn = document.getElementById("drawer-copy");
      if (navigator.clipboard) {
        navigator.clipboard.writeText(location.origin + location.pathname + "#" + openId);
      }
      btn.classList.add("copied");
      setTimeout(function () { btn.classList.remove("copied"); }, 1100);
    }
  });

  if (qInput) {
    var t;
    qInput.addEventListener("input", function (e) {
      clearTimeout(t);
      var v = e.target.value;
      t = setTimeout(function () { state.q = v.trim().toLowerCase(); render(); }, 130);
    });
  }

  document.addEventListener("keydown", function (e) {
    if (!openId) return;
    if (e.key === "Escape") close();
    if (e.key === "ArrowRight") { var n = drawer.querySelector(".nx[data-go]"); if (n) open(n.dataset.go); }
    if (e.key === "ArrowLeft")  { var p = drawer.querySelector(".pv[data-go]"); if (p) open(p.dataset.go); }
  });

  // keep Tab inside the drawer while it is open
  drawer.addEventListener("keydown", function (e) {
    if (e.key !== "Tab" || !openId) return;
    var f = drawer.querySelectorAll('a[href],button:not([disabled]),input,[tabindex]:not([tabindex="-1"])');
    if (!f.length) return;
    var first = f[0], last = f[f.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  });

  window.addEventListener("popstate", function () {
    var id = location.hash.slice(1);
    if (id && details.querySelector('[data-id="' + id + '"]')) open(id, false);
    else if (openId) close(false);
  });

  /* ------------------------------------------------------------------ init */
  render();
  if (location.hash) {
    var id0 = location.hash.slice(1);
    if (details.querySelector('[data-id="' + id0 + '"]')) open(id0, false);
  }
})();
