/* Collett: team filters */
(function () {
  var wrap = document.getElementById("team-filters");
  var people = Array.prototype.slice.call(document.querySelectorAll("#people .person"));
  var count = document.getElementById("team-count");
  var empty = document.getElementById("team-empty");
  var office = wrap.querySelector("select[name=office]");
  var q = wrap.querySelector("input[name=q]");
  var group = "";

  function update() {
    var term = q.value.trim().toLowerCase();
    var n = 0;
    people.forEach(function (p) {
      var ok = (!group || p.dataset.group === group) && (!office.value || p.dataset.office === office.value) && (!term || p.dataset.name.indexOf(term) !== -1);
      p.hidden = !ok;
      if (ok) n++;
    });
    count.textContent = n + (n === 1 ? " person" : " people");
    empty.hidden = n > 0;
    var params = new URLSearchParams();
    if (group) params.set("group", group);
    if (office.value) params.set("office", office.value);
    history.replaceState(null, "", location.pathname + (params.toString() ? "?" + params : ""));
  }
  function setGroup(g) {
    group = g;
    wrap.querySelectorAll(".chip").forEach(function (c) { c.setAttribute("aria-pressed", String(c.dataset.group === g)); });
    update();
  }
  wrap.querySelectorAll(".chip").forEach(function (c) { c.addEventListener("click", function () { setGroup(c.dataset.group); }); });
  office.addEventListener("change", update);
  q.addEventListener("input", update);

  var params = new URLSearchParams(location.search);
  if (params.get("office")) office.value = params.get("office");
  setGroup(params.get("group") || "");
})();
