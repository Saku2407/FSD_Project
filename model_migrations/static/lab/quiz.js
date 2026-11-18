/* Quiz: one question at a time, instant feedback, final score + review. */
(function () {
  "use strict";
  var root = document.getElementById("quiz");
  var dataEl = document.getElementById("quiz-data");
  if (!root || !dataEl) return;

  var original = JSON.parse(dataEl.textContent);
  var questions = original;
  var key = "vlab-quiz-" + (root.getAttribute("data-key") || "x");
  var i, score, answers;

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }

  function best() {
    try { return parseInt(localStorage.getItem(key), 10); } catch (e) { return NaN; }
  }
  function saveBest(n) {
    try {
      var b = best();
      if (isNaN(b) || n > b) localStorage.setItem(key, String(n));
    } catch (e) { /* storage may be blocked; ignore */ }
  }

  /* Shuffle the options of every question (Fisher-Yates), keeping track
     of where the correct one ends up, so the answer is not always "B". */
  function shuffled() {
    return original.map(function (q) {
      var order = q.options.map(function (_, k) { return k; });
      for (var k = order.length - 1; k > 0; k--) {
        var j = Math.floor(Math.random() * (k + 1));
        var t = order[k]; order[k] = order[j]; order[j] = t;
      }
      var copy = {};
      for (var key in q) copy[key] = q[key];
      copy.options = order.map(function (o) { return q.options[o]; });
      copy.answer = order.indexOf(q.answer);
      return copy;
    });
  }

  function start() {
    questions = shuffled();
    i = 0; score = 0; answers = [];
    show();
  }

  function show() {
    root.innerHTML = "";
    var q = questions[i];

    var bar = el("div", "q-progress");
    var fill = el("div", "q-fill");
    fill.style.width = (i / questions.length * 100) + "%";
    bar.appendChild(fill);
    root.appendChild(bar);
    root.appendChild(el("p", "q-count",
      "Question " + (i + 1) + " of " + questions.length));

    root.appendChild(el("h3", "q-text", q.q));
    if (q.code) root.appendChild(el("pre", "code", q.code));

    var list = el("div", "q-options");
    list.setAttribute("role", "group");
    list.setAttribute("aria-label", "Answer options");
    var feedback = el("div", "q-feedback");
    feedback.setAttribute("aria-live", "polite");
    var next = el("button", "btn", i === questions.length - 1 ? "See score" : "Next question");
    next.type = "button";
    next.hidden = true;
    next.addEventListener("click", function () {
      i++;
      if (i < questions.length) show(); else finish();
    });

    var buttons = [];
    q.options.forEach(function (opt, idx) {
      var b = el("button", "q-opt");
      b.type = "button";
      b.appendChild(el("span", "q-letter", String.fromCharCode(65 + idx)));
      b.appendChild(el("span", "q-label", opt));
      b.addEventListener("click", function () {
        var ok = idx === q.answer;
        if (ok) score++;
        answers.push({ chosen: idx, ok: ok });
        buttons.forEach(function (x, j) {
          x.disabled = true;
          if (j === q.answer) x.classList.add("correct");
          else if (j === idx) x.classList.add("wrong");
        });
        feedback.className = "q-feedback " + (ok ? "good" : "bad");
        feedback.textContent = "";
        feedback.appendChild(el("strong", "", ok ? "Correct. " : "Not quite. "));
        feedback.appendChild(document.createTextNode(q.why));
        next.hidden = false;
        next.focus();
      });
      buttons.push(b);
      list.appendChild(b);
    });

    root.appendChild(list);
    root.appendChild(feedback);
    root.appendChild(next);
  }

  function finish() {
    saveBest(score);
    root.innerHTML = "";
    var pct = Math.round(score / questions.length * 100);
    var box = el("div", "q-result");
    box.appendChild(el("div", "q-score", score + " / " + questions.length));
    var msg = pct === 100 ? "Perfect score!"
      : pct >= 60 ? "Good work. Review the questions you missed below."
      : "Keep going. Re-read the Theory page and try the Simulation, then retry.";
    box.appendChild(el("p", "", msg));
    var b = best();
    if (!isNaN(b)) box.appendChild(el("p", "q-best", "Your best score on this browser: " + b + " / " + questions.length));
    root.appendChild(box);

    var review = el("ol", "q-review");
    questions.forEach(function (q, idx) {
      var a = answers[idx];
      var li = el("li", a.ok ? "good" : "bad");
      li.appendChild(el("strong", "", q.q));
      var line = el("div", "q-line");
      line.appendChild(document.createTextNode("Your answer: " + q.options[a.chosen]));
      if (!a.ok) {
        line.appendChild(document.createElement("br"));
        line.appendChild(document.createTextNode("Correct answer: " + q.options[q.answer]));
      }
      li.appendChild(line);
      li.appendChild(el("div", "q-why", q.why));
      review.appendChild(li);
    });
    root.appendChild(review);

    var again = el("button", "btn", "Retry quiz");
    again.type = "button";
    again.addEventListener("click", start);
    root.appendChild(again);
  }

  start();
})();
