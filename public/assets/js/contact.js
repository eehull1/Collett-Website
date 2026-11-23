/* Collett: contact form.
   If the form has a data-endpoint (set contactForm.endpoint in content/site.json),
   submissions are POSTed there as form data (works with Formspree, Basin, Getform…).
   Otherwise, with a data-email, the visitor's email app opens with the message filled in.
   With neither, visitors are asked to call. */
(function () {
  var form = document.getElementById("contact-form");
  if (!form) return;
  var status = form.querySelector(".form-status");
  var props = {};
  (window.COLLETT_PROPERTIES || []).forEach(function (p) { props[p.s] = p.n + " (" + p.c + ", " + p.st + ")"; });

  // Prefill from ?property=slug&subject=flyer|careers
  var params = new URLSearchParams(location.search);
  if (params.get("property") && form.elements.property) {
    form.elements.property.value = params.get("property");
    if (!form.elements.message.value && props[params.get("property")]) {
      form.elements.subject.value = "Leasing";
      form.elements.message.value = "I'd like more information about " + props[params.get("property")] + ".";
    }
  }
  var subj = { flyer: "Property flyer", careers: "Careers" }[params.get("subject")];
  if (subj) {
    form.elements.subject.value = subj;
    if (subj === "Property flyer" && props[params.get("property")]) form.elements.message.value = "Please send me the flyer for " + props[params.get("property")] + ".";
  }

  function say(msg, err) { status.hidden = false; status.textContent = msg; status.classList.toggle("err", !!err); }

  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    if (form.elements.website.value) return; // spam trap
    var bad = null;
    form.querySelectorAll("[required]").forEach(function (el) {
      var ok = el.value.trim() && (el.type !== "email" || /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(el.value));
      el.setAttribute("aria-invalid", ok ? "false" : "true");
      if (!ok && !bad) bad = el;
    });
    if (bad) { say("Please fill in the highlighted fields.", true); bad.focus(); return; }

    var data = new FormData(form);
    data.delete("website");
    if (data.get("property")) data.set("property", props[data.get("property")] || data.get("property"));
    var endpoint = form.dataset.endpoint, email = form.dataset.email;
    var btn = form.querySelector("button[type=submit]");

    if (endpoint) {
      btn.disabled = true;
      fetch(endpoint, { method: "POST", body: data, headers: { Accept: "application/json" } })
        .then(function (r) { if (!r.ok) throw new Error(r.status); form.reset(); say("Thank you. Your message has been sent and someone from our team will be in touch soon."); })
        .catch(function () { say("Sorry, your message could not be sent. Please call us at 704.206.8300.", true); })
        .then(function () { btn.disabled = false; });
      return;
    }
    if (email) {
      var lines = [];
      data.forEach(function (v, k) { if (v && k !== "message") lines.push(k.replace(/_/g, " ") + ": " + v); });
      var body = data.get("message") + "\n\n" + lines.join("\n");
      window.location.href = "mailto:" + email + "?subject=" + encodeURIComponent("Website inquiry: " + data.get("subject")) + "&body=" + encodeURIComponent(body);
      say("Your email app should open with your message ready to send.");
      return;
    }
    say("Online messages aren't set up yet. Please call us at 704.206.8300 and we'll be glad to help.", true);
  });
})();
