/* =============================================================================
   site.js — shared behaviour. Loaded on every page.
   Two jobs: the mobile nav, and the list filter used by Publications,
   Awards and Service (same widget, different lists).
   ============================================================================= */
(function () {
  "use strict";

  /* ---------------------------------------------------------- mobile nav */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("primary-nav");
  if (toggle && nav) {
    var sync = function () {
      var small = window.matchMedia("(max-width: 760px)").matches;
      nav.hidden = small && toggle.getAttribute("aria-expanded") !== "true";
    };
    toggle.addEventListener("click", function () {
      var open = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!open));
      sync();
    });
    window.addEventListener("resize", sync);
    sync();
  }

  /* ------------------------------------------------------- list filtering
     Any element with [data-filterable] becomes filterable. Its rows carry
     data-facet-* attributes and a data-search string; chips carry
     data-kind (matching the facet name) and data-val. Year headings with
     [data-group] hide automatically when every row under them is hidden. */
  document.querySelectorAll("[data-filterable]").forEach(function (root) {
    var rows   = Array.prototype.slice.call(root.querySelectorAll("[data-row]"));
    var groups = Array.prototype.slice.call(root.querySelectorAll("[data-group]"));
    var chips  = Array.prototype.slice.call(document.querySelectorAll('.chip[data-scope="' + root.id + '"]'));
    var input  = document.querySelector('[data-search-for="' + root.id + '"]');
    var count  = document.querySelector('[data-count-for="' + root.id + '"]');
    var noun   = root.dataset.noun || "item";
    var state  = {};

    function matches(row) {
      for (var k in state) {
        // keys prefixed __ are internal (the search term), not data facets
        if (k.slice(0, 2) === "__") continue;
        if (state[k] !== "all" && row.dataset["facet" + cap(k)] !== state[k]) return false;
      }
      if (state.__q && (row.dataset.search || "").indexOf(state.__q) === -1) return false;
      return true;
    }
    function cap(s) { return s.charAt(0).toUpperCase() + s.slice(1); }

    function apply() {
      var n = 0;
      rows.forEach(function (r) {
        var ok = matches(r);
        r.hidden = !ok;
        if (ok) n++;
      });
      // a year heading with nothing under it is noise
      groups.forEach(function (g) {
        var any = false, el = g.nextElementSibling;
        while (el && !el.hasAttribute("data-group")) {
          if (el.hasAttribute("data-row") && !el.hidden) { any = true; break; }
          var inner = el.querySelectorAll ? el.querySelectorAll("[data-row]:not([hidden])") : [];
          if (inner.length) { any = true; break; }
          el = el.nextElementSibling;
        }
        g.hidden = !any;
      });
      if (count) count.textContent = n + " " + (n === 1 ? noun : noun + "s");
      var empty = root.querySelector("[data-empty]");
      if (empty) empty.hidden = n > 0;
    }

    chips.forEach(function (chip) {
      if (!(chip.dataset.kind in state)) state[chip.dataset.kind] = "all";
      chip.addEventListener("click", function () {
        state[chip.dataset.kind] = chip.dataset.val;
        chips.forEach(function (c) {
          if (c.dataset.kind === chip.dataset.kind) {
            c.setAttribute("aria-pressed", String(c === chip));
          }
        });
        apply();
      });
    });

    if (input) {
      var t;
      input.addEventListener("input", function (e) {
        clearTimeout(t);
        var v = e.target.value;
        t = setTimeout(function () { state.__q = v.trim().toLowerCase(); apply(); }, 130);
      });
    }

    var clear = document.querySelector('[data-clear-for="' + root.id + '"]');
    if (clear) {
      clear.addEventListener("click", function () {
        for (var k in state) { if (k.slice(0, 2) !== "__") state[k] = "all"; }
        state.__q = "";
        if (input) input.value = "";
        chips.forEach(function (c) { c.setAttribute("aria-pressed", String(c.dataset.val === "all")); });
        apply();
      });
    }

    apply();
  });

  /* ------------------------------------------------------- email reveal
     Contact's address ships as data-user/data-domain, not a plain mailto:
     link -- most address-harvesting bots scrape static HTML and don't
     execute JS, so this keeps a real address out of the page source
     while real visitors see it assembled instantly on load. */
  document.querySelectorAll(".email-link[data-user][data-domain]").forEach(function (el) {
    var addr = el.dataset.user + "@" + el.dataset.domain;
    el.textContent = addr;
    el.href = "mailto:" + addr;
    el.removeAttribute("rel");
  });
})();
