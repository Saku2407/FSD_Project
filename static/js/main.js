(function () {
  // Live date and time in the top bar, e.g. "18 Nov, 2026 | 00:11:03 AM"
  var clock = document.getElementById("clock");
  function pad(n) { return String(n).padStart(2, "0"); }
  function tick() {
    if (!clock) return;
    var d = new Date();
    var months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
    var h = d.getHours();
    var ampm = h >= 12 ? "PM" : "AM";
    var h12 = h % 12;
    clock.textContent = d.getDate() + " " + months[d.getMonth()] + ", " + d.getFullYear() +
      " | " + pad(h12) + ":" + pad(d.getMinutes()) + ":" + pad(d.getSeconds()) + " " + ampm;
  }
  tick();
  setInterval(tick, 1000);

  // Reference Books / Syllabus Mapping dropdowns (one open panel per lab card)
  document.querySelectorAll(".toggle").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var panel = document.getElementById(btn.getAttribute("aria-controls"));
      var opening = btn.getAttribute("aria-expanded") !== "true";
      var card = btn.closest(".lab-card");
      card.querySelectorAll(".toggle").forEach(function (b) {
        b.setAttribute("aria-expanded", "false");
        document.getElementById(b.getAttribute("aria-controls")).hidden = true;
      });
      if (opening) {
        btn.setAttribute("aria-expanded", "true");
        panel.hidden = false;
      }
    });
  });

  // Search Lab: filter cards as you type
  var search = document.getElementById("lab-search");
  var cards = document.querySelectorAll(".lab-card");
  var empty = document.getElementById("no-results");
  if (search && cards.length) {
    search.addEventListener("input", function () {
      var q = search.value.trim().toLowerCase();
      var shown = 0;
      cards.forEach(function (card) {
        var match = card.dataset.title.indexOf(q) !== -1;
        card.hidden = !match;
        if (match) shown++;
      });
      if (empty) empty.hidden = shown !== 0;
    });
  }

  // Back-to-top button
  var top = document.getElementById("to-top");
  if (top) {
    window.addEventListener("scroll", function () {
      top.hidden = window.scrollY < 300;
    });
    top.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }
})();
