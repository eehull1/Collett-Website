/* Collett: property photo gallery + lightbox */
(function () {
  var g = document.querySelector(".gallery[data-gallery]");
  if (!g) return;
  var photos = JSON.parse(g.getAttribute("data-gallery"));
  var main = g.querySelector(".g-main img");
  var thumbs = g.querySelectorAll(".g-thumbs button");
  var cur = 0;

  function select(i) {
    cur = (i + photos.length) % photos.length;
    main.src = photos[cur];
    thumbs.forEach(function (t, j) { if (j === cur) t.setAttribute("aria-current", "true"); else t.removeAttribute("aria-current"); });
  }
  thumbs.forEach(function (t) { t.addEventListener("click", function () { select(+t.dataset.i); }); });

  var svg = function (d) { return '<svg class="i" viewBox="0 0 24 24" aria-hidden="true"><path d="' + d + '"/></svg>'; };
  g.querySelector(".g-main").addEventListener("click", function () {
    var lb = document.createElement("div");
    lb.className = "lightbox";
    lb.setAttribute("role", "dialog");
    lb.setAttribute("aria-modal", "true");
    lb.setAttribute("aria-label", "Photo viewer");
    lb.innerHTML = '<img alt=""><button class="lb-close" aria-label="Close">' + svg("M6 6l12 12M18 6 6 18") + "</button>" +
      (photos.length > 1 ? '<button class="lb-prev" aria-label="Previous photo">' + svg("m15 18-6-6 6-6") + '</button><button class="lb-next" aria-label="Next photo">' + svg("m9 18 6-6-6-6") + "</button>" : "") +
      '<p class="lb-count"></p>';
    var img = lb.querySelector("img");
    var cnt = lb.querySelector(".lb-count");
    var opener = document.activeElement;
    function show() { img.src = photos[cur]; cnt.textContent = (cur + 1) + " / " + photos.length; }
    function close() { document.removeEventListener("keydown", key); lb.remove(); document.body.style.overflow = ""; select(cur); if (opener) opener.focus(); }
    function key(ev) {
      if (ev.key === "Escape") close();
      if (ev.key === "ArrowRight") { cur = (cur + 1) % photos.length; show(); }
      if (ev.key === "ArrowLeft") { cur = (cur - 1 + photos.length) % photos.length; show(); }
    }
    lb.addEventListener("click", function (ev) {
      var b = ev.target.closest("button");
      if (!b) { if (ev.target === lb) close(); return; }
      if (b.classList.contains("lb-close")) close();
      if (b.classList.contains("lb-next")) { cur = (cur + 1) % photos.length; show(); }
      if (b.classList.contains("lb-prev")) { cur = (cur - 1 + photos.length) % photos.length; show(); }
    });
    document.addEventListener("keydown", key);
    document.body.appendChild(lb);
    document.body.style.overflow = "hidden";
    show();
    lb.querySelector(".lb-close").focus();
  });
})();
