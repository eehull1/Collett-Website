/* Collett: portfolio dot map. Renders window.COLLETT_PROPERTIES onto every .us-map. */
(function () {
  var NS = "http://www.w3.org/2000/svg";
  var data = window.COLLETT_PROPERTIES || [];

  function render(mapEl, list) {
    var svg = mapEl.querySelector(".us-map-dots");
    var tip = mapEl.querySelector(".map-tip");
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    // draw land/industrial first so retail (the majority) sits on top
    var order = { Land: 0, Other: 0, Office: 1, Industrial: 2, Retail: 3 };
    list.filter(function (p) { return p.xy; })
      .sort(function (a, b) { return (order[a.t] || 0) - (order[b.t] || 0); })
      .forEach(function (p) {
        var c = document.createElementNS(NS, "circle");
        c.setAttribute("cx", p.xy[0]);
        c.setAttribute("cy", p.xy[1]);
        c.setAttribute("r", 5.2);
        c.setAttribute("data-t", p.t);
        c.setAttribute("tabindex", p.pg ? "0" : "-1");
        c.setAttribute("role", p.pg ? "link" : "img");
        c.setAttribute("aria-label", p.n + ", " + p.c + ", " + p.st);
        c._p = p;
        svg.appendChild(c);
      });

    function show(c) {
      var p = c._p;
      var box = mapEl.getBoundingClientRect();
      var scale = box.width / 960;
      tip.innerHTML = "";
      var b = document.createElement("b"); b.textContent = p.n;
      var s = document.createElement("span"); s.textContent = p.c + ", " + p.st + " · " + p.t + (p.a ? " · " + p.a : "");
      tip.appendChild(b); tip.appendChild(s);
      tip.style.left = Math.min(Math.max(p.xy[0] * scale, 90), box.width - 90) + "px";
      tip.style.top = p.xy[1] * scale + "px";
      tip.hidden = false;
    }
    function hide() { tip.hidden = true; }
    function open(c) { if (c._p.pg) window.location.href = "/properties/" + c._p.s + "/"; }

    svg.onmouseover = function (ev) { if (ev.target.tagName === "circle") show(ev.target); };
    svg.onmouseout = function (ev) { if (ev.target.tagName === "circle") hide(); };
    svg.onfocusin = function (ev) { if (ev.target.tagName === "circle") show(ev.target); };
    svg.onfocusout = hide;
    svg.onclick = function (ev) { if (ev.target.tagName === "circle") open(ev.target); };
    svg.onkeydown = function (ev) { if (ev.key === "Enter" && ev.target.tagName === "circle") open(ev.target); };
  }

  window.CollettMap = { render: render };
  document.querySelectorAll("[data-map]").forEach(function (m) {
    if (!m.hasAttribute("data-map-manual")) render(m, data);
  });
})();
