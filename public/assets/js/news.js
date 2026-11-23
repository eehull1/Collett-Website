/* Collett: news archive (year filter + show more) */
(function () {
  var rows = Array.prototype.slice.call(document.querySelectorAll("#news-list .n-row"));
  var chips = document.querySelectorAll("#year-chips .chip");
  var more = document.getElementById("news-more");
  var PAGE = 15, shown = PAGE, year = "";

  function update() {
    var list = rows.filter(function (r) { return !year || r.dataset.year === year; });
    rows.forEach(function (r) { r.hidden = true; });
    list.forEach(function (r, i) { r.hidden = !year && i >= shown; });
    more.hidden = !!year || list.length <= shown;
  }
  chips.forEach(function (c) {
    c.addEventListener("click", function () {
      year = c.dataset.year;
      chips.forEach(function (x) { x.setAttribute("aria-pressed", String(x === c)); });
      update();
    });
  });
  more.addEventListener("click", function () { shown += PAGE; update(); });
  update();
})();
