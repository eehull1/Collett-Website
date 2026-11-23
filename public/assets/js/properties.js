/* Collett: property search (filters, URL sync, grid and map views) */
(function () {
  var all = window.COLLETT_PROPERTIES || [];
  var form = document.getElementById("filters");
  var grid = document.getElementById("view-grid");
  var mapWrap = document.getElementById("view-map");
  var mapEl = mapWrap.querySelector("[data-map]");
  var mapList = document.getElementById("map-list");
  var count = document.getElementById("result-count");
  var more = document.getElementById("load-more");
  var clear = document.getElementById("clear-filters");
  var PAGE = 24;
  var shown = PAGE;
  var view = "grid";

  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function initials(n) { var w = n.replace(/[^A-Za-z0-9 ]/g, "").split(/\s+/).filter(Boolean); return ((w[0] || "")[0] + ((w[1] || "")[0] || "")).toUpperCase(); }

  // Most complete listings first (detail page, photo, named center rather than
  // a size/acreage listing, available now), then A–Z
  function score(p) { return (p.pg ? 8 : 0) + (p.img ? 4 : 0) + (/^[A-Za-z]/.test(p.n) && !/acres|^\W|sf\b/i.test(p.n) ? 2 : 0) + (p.a ? 1 : 0); }
  all.sort(function (a, b) { return score(b) - score(a) || a.n.localeCompare(b.n); });

  function state() {
    var f = new FormData(form);
    return {
      q: (f.get("q") || "").trim().toLowerCase(),
      state: f.get("state") || "",
      type: f.get("type") || "",
      avail: f.get("avail") || "",
      dev: f.get("dev") ? "1" : "",
      man: f.get("man") ? "1" : "",
      uc: f.get("uc") ? "1" : ""
    };
  }

  function matches(p, s) {
    if (s.state && p.st !== s.state) return false;
    if (s.type && p.t !== s.type) return false;
    if (s.avail === "any" && !p.a) return false;
    if (s.avail === "lease" && !/lease/i.test(p.a)) return false;
    if (s.avail === "sale" && !/sale/i.test(p.a)) return false;
    if (s.dev && !p.d) return false;
    if (s.man && !p.m) return false;
    if (s.uc && !p.uc) return false;
    if (s.q) {
      var words = s.q.split(/\s+/);
      for (var i = 0; i < words.length; i++) if (p.k.indexOf(words[i]) === -1) return false;
    }
    return true;
  }

  function card(p) {
    var href = p.pg ? "/properties/" + p.s + "/" : "";
    var media = p.img
      ? '<img src="' + esc(p.img) + '" alt="" loading="lazy" decoding="async">'
      : '<div class="ph" aria-hidden="true"><span>' + esc(initials(p.n)) + "</span></div>";
    var title = href ? '<a href="' + href + '">' + esc(p.n) + "</a>" : esc(p.n);
    var tags = "";
    if (p.a) tags += '<span class="tag tag-avail">' + esc(p.a) + "</span>";
    if (p.uc) tags += '<span class="tag tag-uc">Under construction</span>';
    else if (p.d) tags += '<span class="tag tag-dev">Developed by Collett</span>';
    else if (p.m) tags += '<span class="tag tag-man">Managed by Collett</span>';
    return '<article class="p-card"><div class="p-media">' + media + '<span class="p-type">' + esc(p.t) + "</span></div>" +
      '<div class="p-body"><h3>' + title + '</h3><p class="p-loc"><svg class="i i-xs" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 22s7-6.2 7-12a7 7 0 1 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/></svg>' +
      esc(p.c) + ", " + esc(p.st) + '</p><div class="tags">' + tags + "</div></div></article>";
  }

  function syncUrl(s) {
    var params = new URLSearchParams();
    Object.keys(s).forEach(function (k) { if (s[k]) params.set(k, s[k]); });
    if (view === "map") params.set("view", "map");
    var qs = params.toString();
    history.replaceState(null, "", location.pathname + (qs ? "?" + qs : ""));
  }

  function update(resetPage) {
    if (resetPage) shown = PAGE;
    var s = state();
    var list = all.filter(function (p) { return matches(p, s); });
    var active = Object.keys(s).some(function (k) { return s[k]; });
    count.textContent = list.length + (list.length === 1 ? " property" : " properties") + (active ? (list.length === 1 ? " matches" : " match") + " your filters" : "");
    clear.hidden = !active;

    if (view === "grid") {
      grid.innerHTML = list.length
        ? list.slice(0, shown).map(card).join("")
        : '<p class="empty" style="grid-column:1/-1">No properties match those filters. <button type="button" class="link-btn" data-clear>Clear filters</button></p>';
      more.hidden = list.length <= shown;
      more.textContent = "Show more properties (" + (list.length - shown) + " more)";
    } else {
      more.hidden = true;
      window.CollettMap.render(mapEl, list);
      var mapped = list.filter(function (p) { return p.xy; });
      mapList.innerHTML = mapped.map(function (p) {
        var name = p.pg ? '<a href="/properties/' + p.s + '/">' + esc(p.n) + "</a>" : "<b>" + esc(p.n) + "</b>";
        return "<li>" + name + "<span>" + esc(p.c) + ", " + esc(p.st) + " · " + esc(p.t) + "</span></li>";
      }).join("");
    }
    syncUrl(s);
  }

  function setView(v) {
    view = v;
    document.querySelectorAll(".seg button").forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.view === v)); });
    grid.hidden = v !== "grid";
    mapWrap.hidden = v !== "map";
    update(false);
  }

  // Load state from the URL (?state=NC&type=Retail&avail=lease&dev=1&view=map)
  var params = new URLSearchParams(location.search);
  ["q", "state", "type", "avail"].forEach(function (k) {
    if (params.get(k) && form.elements[k]) form.elements[k].value = params.get(k);
  });
  ["dev", "man", "uc"].forEach(function (k) { if (params.get(k)) form.elements[k].checked = true; });

  var t;
  form.addEventListener("input", function (ev) {
    clearTimeout(t);
    t = setTimeout(function () { update(true); }, ev.target.type === "search" ? 160 : 0);
  });
  form.addEventListener("submit", function (ev) { ev.preventDefault(); });
  more.addEventListener("click", function () { shown += PAGE; update(false); });
  function clearAll() { form.reset(); update(true); }
  clear.addEventListener("click", clearAll);
  grid.addEventListener("click", function (ev) { if (ev.target.hasAttribute("data-clear")) clearAll(); });
  document.querySelectorAll(".seg button").forEach(function (b) { b.addEventListener("click", function () { setView(b.dataset.view); }); });

  setView(params.get("view") === "map" ? "map" : "grid");
})();
