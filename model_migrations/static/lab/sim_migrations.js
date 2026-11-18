/* Experiment 2 simulation: the migration lifecycle, step by step. */
(function () {
  "use strict";
  var V = window.VLab, $ = V.$;
  if (!$("migsim")) return;

  var MODEL_V1 = [
    "from django.db import models",
    "",
    "class Book(models.Model):",
    "    title = models.CharField(max_length=100)",
    "    pages = models.IntegerField()"
  ].join("\n");

  var MODEL_V2 = MODEL_V1 + "\n    published = models.DateField(null=True)";

  var MIG1 = [
    "from django.db import migrations, models",
    "",
    "",
    "class Migration(migrations.Migration):",
    "",
    "    initial = True",
    "",
    "    dependencies = []",
    "",
    "    operations = [",
    "        migrations.CreateModel(",
    "            name='Book',",
    "            fields=[",
    "                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),",
    "                ('title', models.CharField(max_length=100)),",
    "                ('pages', models.IntegerField()),",
    "            ],",
    "        ),",
    "    ]"
  ].join("\n");

  var MIG2 = [
    "from django.db import migrations, models",
    "",
    "",
    "class Migration(migrations.Migration):",
    "",
    "    dependencies = [",
    "        ('library', '0001_initial'),",
    "    ]",
    "",
    "    operations = [",
    "        migrations.AddField(",
    "            model_name='book',",
    "            name='published',",
    "            field=models.DateField(null=True),",
    "        ),",
    "    ]"
  ].join("\n");

  var COLS_V1 = [["id", "integer", "PK"], ["title", "varchar(100)", ""], ["pages", "integer", ""]];
  var COLS_V2 = COLS_V1.concat([["published", "date NULL", ""]]);

  var SQL1 = [
    "BEGIN;",
    "--",
    "-- Create model Book",
    "--",
    'CREATE TABLE "library_book" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(100) NOT NULL, "pages" integer NOT NULL);',
    "COMMIT;"
  ];

  /* Each step: what is typed, what is printed, which flow nodes light up,
     and the patch it applies to the state. */
  var STEPS = [
    {
      title: "Write the model",
      cmd: null,
      out: [],
      nodes: [0],
      before: "You edit models.py to define a Book with a title and a page count. Will anything change in the database?",
      after: "No. Editing a model is just editing a Python file. There is no migration and no table yet.",
      status: ["warn", "models.py has changes that are not in any migration"],
      patch: { models: MODEL_V1 }
    },
    {
      title: "makemigrations",
      cmd: "python manage.py makemigrations library",
      out: ["Migrations for 'library':", "  library/migrations/0001_initial.py", "    + Create model Book"],
      nodes: [0, 1],
      before: "Django compares models.py with the existing migrations (there are none). What will it create, and will it change the database?",
      after: "A new file, 0001_initial.py, now describes the change. The database panel is still empty because makemigrations never touches the database.",
      status: ["warn", "Migration file exists, database not updated"],
      patch: { files: [["0001_initial.py", MIG1]] }
    },
    {
      title: "showmigrations",
      cmd: "python manage.py showmigrations library",
      out: ["library", " [ ] 0001_initial"],
      nodes: [1],
      before: "Which symbol will Django show next to 0001_initial: [X] or [ ]?",
      after: "[ ] means the migration exists as a file but has not been applied yet.",
      status: ["warn", "Migration file exists, database not updated"],
      patch: {}
    },
    {
      title: "sqlmigrate",
      cmd: "python manage.py sqlmigrate library 0001",
      out: SQL1,
      nodes: [1],
      before: "sqlmigrate prints the SQL for a migration. Will it also run it?",
      after: "It only prints the SQL. Find the part that came from the title field. Still nothing in the database.",
      status: ["warn", "Migration file exists, database not updated"],
      patch: {}
    },
    {
      title: "migrate",
      cmd: "python manage.py migrate library",
      out: ["Operations to perform:", "  Apply all migrations: library", "Running migrations:", "  Applying library.0001_initial... OK"],
      nodes: [1, 2],
      before: "Now the database will be changed. Which two things should change?",
      after: "The library_book table was created, and a row was added to django_migrations so Django remembers 0001 is applied.",
      status: ["ok", "Database is in sync with the migrations"],
      patch: { db: COLS_V1, dm: ["0001_initial"] }
    },
    {
      title: "showmigrations again",
      cmd: "python manage.py showmigrations library",
      out: ["library", " [X] 0001_initial"],
      nodes: [2],
      before: "What will the symbol be this time?",
      after: "[X] means applied. Django read the django_migrations table to work that out.",
      status: ["ok", "Database is in sync with the migrations"],
      patch: {}
    },
    {
      title: "Change the model",
      cmd: null,
      out: [],
      nodes: [0],
      before: "You add published = models.DateField(null=True) to the model. Does the database change now?",
      after: "No. models.py now says one thing, and the database says another. Django will not notice until you run makemigrations.",
      status: ["warn", "models.py has changes that are not in any migration"],
      patch: { models: MODEL_V2 }
    },
    {
      title: "makemigrations (2nd time)",
      cmd: "python manage.py makemigrations library",
      out: ["Migrations for 'library':", "  library/migrations/0002_book_published.py", "    + Add field published to book"],
      nodes: [0, 1],
      before: "Will Django rewrite 0001, or create a new file?",
      after: "A new file, 0002_book_published.py, with an AddField. It depends on 0001_initial. Migrations that have been applied are never rewritten.",
      status: ["warn", "Migration file exists, database not updated"],
      patch: { files: [["0001_initial.py", MIG1], ["0002_book_published.py", MIG2]] }
    },
    {
      title: "migrate (2nd time)",
      cmd: "python manage.py migrate library",
      out: ["Operations to perform:", "  Apply all migrations: library", "Running migrations:", "  Applying library.0002_book_published... OK"],
      nodes: [1, 2],
      before: "Django will run only the migrations that are missing. Which one(s)?",
      after: "Only 0002 ran. The published column was added to the table, and a second row was recorded in django_migrations.",
      status: ["ok", "Database is in sync with the migrations"],
      patch: { db: COLS_V2, dm: ["0001_initial", "0002_book_published"] }
    },
    {
      title: "makemigrations (nothing changed)",
      cmd: "python manage.py makemigrations library",
      out: ["No changes detected in app 'library'"],
      nodes: [0],
      before: "You change nothing and run makemigrations again. What happens?",
      after: "Django finds no difference between the models and the migrations, so it writes nothing. This is why the commands are safe to repeat.",
      status: ["ok", "Database is in sync with the migrations"],
      patch: {}
    }
  ];

  var pos, busy, auto, autoTimer, state, prevState, timers = [];

  function emptyState() {
    return { models: "", files: [], db: null, dm: [], selected: 0 };
  }

  function cloneState(s) { return JSON.parse(JSON.stringify(s)); }

  function nowStamp() {
    var d = new Date(), p = function (n) { return (n < 10 ? "0" : "") + n; };
    return d.getFullYear() + "-" + p(d.getMonth() + 1) + "-" + p(d.getDate()) +
      " " + p(d.getHours()) + ":" + p(d.getMinutes()) + ":" + p(d.getSeconds());
  }

  /* ---------- rendering ---------- */
  function flash(id) {
    var n = $(id);
    n.classList.remove("flashbox");
    void n.offsetWidth;
    n.classList.add("flashbox");
  }

  function renderState(animate) {
    var ps = prevState;
    $("mg-models").innerHTML = state.models ? V.py(state.models)
      : '<span class="empty">(models.py is empty)</span>';

    var ul = $("mg-files");
    ul.innerHTML = "";
    var init = document.createElement("li");
    init.innerHTML = '<span class="file dim">__init__.py</span>';
    ul.appendChild(init);
    state.files.forEach(function (f, i) {
      var li = document.createElement("li");
      var b = document.createElement("button");
      b.type = "button";
      b.className = "file" + (i === state.selected ? " sel" : "");
      b.textContent = f[0];
      b.addEventListener("click", function () {
        state.selected = i; renderState(false);
      });
      li.appendChild(b);
      ul.appendChild(li);
    });
    var code = $("mg-filecode");
    code.innerHTML = state.files.length
      ? V.py(state.files[state.selected][1])
      : '<span class="empty">(no migration files yet)</span>';

    var db = $("mg-db");
    if (!state.db) {
      db.innerHTML = '<p class="empty">No library tables yet.</p>';
    } else {
      var h = '<table class="data compact"><caption>library_book</caption><thead><tr><th>column</th><th>type</th></tr></thead><tbody>';
      var old = ps && ps.db ? ps.db.map(function (c) { return c[0]; }) : [];
      state.db.forEach(function (c) {
        var isNew = animate && old.indexOf(c[0]) === -1;
        h += '<tr class="' + (isNew ? "flash" : "") + '"><td><code>' + V.esc(c[0]) + "</code></td><td>" +
          V.esc(c[1]) + (c[2] ? " &middot; " + c[2] : "") + "</td></tr>";
      });
      db.innerHTML = h + "</tbody></table>";
    }

    var dm = $("mg-dm");
    if (!state.dm.length) {
      dm.innerHTML = '<p class="empty">No rows for the library app.</p>';
    } else {
      var t = '<table class="data compact"><thead><tr><th>id</th><th>app</th><th>name</th><th>applied</th></tr></thead><tbody>';
      state.dm.forEach(function (r, i) {
        var isNew = animate && (!ps || ps.dm.length <= i);
        t += '<tr class="' + (isNew ? "flash" : "") + '"><td>' + (i + 1) + "</td><td>library</td><td>" +
          V.esc(r.name) + "</td><td>" + V.esc(r.at) + "</td></tr>";
      });
      dm.innerHTML = t + "</tbody></table>";
    }

    if (animate && ps) {
      if (ps.models !== state.models) flash("mg-p-models");
      if (ps.files.length !== state.files.length) flash("mg-p-files");
      if (JSON.stringify(ps.db) !== JSON.stringify(state.db)) flash("mg-p-db");
      if (ps.dm.length !== state.dm.length) flash("mg-p-dm");
    }
  }

  function renderStepList() {
    var ol = $("mg-steps");
    ol.innerHTML = "";
    STEPS.forEach(function (s, i) {
      var li = document.createElement("li");
      li.className = i < pos ? "done" : i === pos ? "now" : "";
      li.textContent = s.title;
      ol.appendChild(li);
    });
  }

  function setNodes(nodes) {
    document.querySelectorAll("#mg-flow .node").forEach(function (n) {
      var k = parseInt(n.getAttribute("data-n"), 10);
      n.classList.toggle("on", nodes.indexOf(k) !== -1);
    });
  }

  function setStatus(st) {
    var c = $("mg-status");
    c.textContent = st[1];
    c.className = "chip " + st[0];
  }

  function renderHeader() {
    var done = pos >= STEPS.length;
    $("mg-stepno").textContent = done ? "All steps done" :
      "Step " + (pos + 1) + " of " + STEPS.length;
    $("mg-title").textContent = done ? "Finished" : STEPS[pos].title;
    $("mg-before").textContent = done
      ? "You have seen the whole lifecycle. Press Reset to run it again, or try Experiment 3."
      : STEPS[pos].before;
    $("mg-next").disabled = busy || done;
    $("mg-next").textContent = pos === 0 ? "Run next step" : "Run next step";
    renderStepList();
  }

  /* ---------- terminal ---------- */
  function termLine(cls, text) {
    var d = document.createElement("div");
    d.className = cls;
    d.textContent = text;
    $("mg-term").appendChild(d);
    $("mg-term").scrollTop = $("mg-term").scrollHeight;
    return d;
  }

  function later(fn, ms) {
    var t = setTimeout(fn, ms);
    timers.push(t);
    return t;
  }

  function runStep() {
    if (busy || pos >= STEPS.length) return;
    busy = true;
    var s = STEPS[pos];
    $("mg-next").disabled = true;
    $("mg-after-box").hidden = true;
    setNodes(s.nodes);

    var finish = function () {
      prevState = cloneState(state);
      applyPatch(s.patch);
      if (s.cmd && s.patch.dm) {
        /* stamp newly applied migrations with the current time */
        state.dm = s.patch.dm.map(function (n, i) {
          var existing = prevState.dm[i];
          return { name: n, at: existing ? existing.at : nowStamp() };
        });
      }
      if (s.patch.files) state.selected = s.patch.files.length - 1;
      renderState(true);
      setStatus(s.status);
      $("mg-after").textContent = s.after;
      $("mg-after-box").hidden = false;
      pos++;
      busy = false;
      renderHeader();
      if (auto && pos < STEPS.length) autoTimer = later(runStep, 1800);
      else { auto = false; $("mg-auto").textContent = "Auto-play"; }
    };

    if (!s.cmd) { finish(); return; }

    var line = termLine("cmd", "");
    var text = "$ " + s.cmd, k = 0;
    var typeNext = function () {
      if (V.reduceMotion()) k = text.length; else k++;
      line.textContent = text.slice(0, k);
      if (k < text.length) { later(typeNext, 18); return; }
      var i = 0;
      var out = function () {
        if (i < s.out.length) {
          termLine("out", s.out[i]); i++;
          later(out, V.reduceMotion() ? 0 : 140);
        } else {
          later(finish, V.reduceMotion() ? 0 : 250);
        }
      };
      later(out, V.reduceMotion() ? 0 : 250);
    };
    typeNext();
  }

  function applyPatch(p) {
    if (p.models !== undefined) state.models = p.models;
    if (p.files !== undefined) state.files = p.files;
    if (p.db !== undefined) state.db = p.db;
  }

  function reset() {
    timers.forEach(clearTimeout); timers = [];
    pos = 0; busy = false; auto = false;
    state = emptyState(); prevState = null;
    $("mg-term").innerHTML = "";
    $("mg-auto").textContent = "Auto-play";
    $("mg-after-box").hidden = true;
    setNodes([]);
    setStatus(["", "Empty project"]);
    renderState(false);
    renderHeader();
  }

  $("mg-next").addEventListener("click", function () { auto = false; runStep(); });
  $("mg-reset").addEventListener("click", reset);
  $("mg-auto").addEventListener("click", function () {
    if (auto) {
      auto = false; clearTimeout(autoTimer);
      $("mg-auto").textContent = "Auto-play";
      return;
    }
    if (pos >= STEPS.length) return;
    auto = true;
    $("mg-auto").textContent = "Pause";
    if (!busy) runStep();
  });

  reset();
})();
