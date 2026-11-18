/* Experiment 3 simulation: evolve a live table with migrations.
   Operations: add / remove / rename / alter a field. Migrate forward
   and backward along the chain and watch the data. */
(function () {
  "use strict";
  var V = window.VLab, $ = V.$;
  if (!$("evosim")) return;

  var INIT_CODE = [
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

  var db, migs, prevSig = null, picked = 0;

  function clone(x) { return JSON.parse(JSON.stringify(x)); }

  function initialCols() {
    return [
      V.col({ name: "title", type: "CharField", maxLength: 100 }),
      V.col({ name: "pages", type: "IntegerField" })
    ];
  }

  function freshDb() {
    return {
      cols: initialCols(),
      rows: [
        { id: 1, title: "Dune", pages: 412 },
        { id: 2, title: "Emma", pages: 474 },
        { id: 3, title: "Ulysses", pages: 730 }
      ]
    };
  }

  function coerce(type, raw) {
    if (raw === null || raw === undefined) return null;
    if (type === "IntegerField") return parseInt(raw, 10);
    if (type === "FloatField") return parseFloat(raw);
    if (type === "BooleanField") return raw === "True" || raw === true;
    return String(raw);
  }

  function zeroFor(type) {
    switch (type) {
      case "IntegerField": case "FloatField": return "0";
      case "BooleanField": return "False";
      case "DateField": return "2025-01-01";
      default: return "";
    }
  }

  function idx(cols, name) {
    for (var i = 0; i < cols.length; i++) if (cols[i].name === name) return i;
    return -1;
  }

  /* ---------- operations: forward / backward on a {cols, rows} ---------- */
  /* Each returns a warning string (or "") about data. */
  function fwd(op, d) {
    var i;
    switch (op.kind) {
      case "add":
        d.cols.push(clone(op.col));
        d.rows.forEach(function (r) { r[op.col.name] = op.fill; });
        return "";
      case "remove":
        i = idx(d.cols, op.old.name);
        d.cols.splice(i, 1);
        d.rows.forEach(function (r) { delete r[op.old.name]; });
        return "RemoveField dropped the column '" + op.old.name + "' and all the data in it.";
      case "rename":
        i = idx(d.cols, op.from);
        d.cols[i].name = op.to;
        d.rows.forEach(function (r) { r[op.to] = r[op.from]; delete r[op.from]; });
        return "";
      case "alter":
        i = idx(d.cols, op.name);
        d.cols[i] = clone(op.newCol);
        return op.newCol.type !== op.oldCol.type
          ? "The type of '" + op.name + "' changed. A real database may refuse values it cannot convert." : "";
    }
    return "";
  }

  function back(op, d) {
    var i;
    switch (op.kind) {
      case "add":
        i = idx(d.cols, op.col.name);
        d.cols.splice(i, 1);
        d.rows.forEach(function (r) { delete r[op.col.name]; });
        return "Reversing AddField dropped the column '" + op.col.name + "' and its data.";
      case "remove":
        d.cols.splice(Math.min(op.index, d.cols.length), 0, clone(op.old));
        d.rows.forEach(function (r) { r[op.old.name] = op.old.null ? null : coerce(op.old.type, zeroFor(op.old.type)); });
        return "Reversing RemoveField re-created '" + op.old.name + "', but the old data is gone: the column holds " +
          (op.old.null ? "NULL." : "a placeholder value.");
      case "rename":
        i = idx(d.cols, op.to);
        d.cols[i].name = op.from;
        d.rows.forEach(function (r) { r[op.from] = r[op.to]; delete r[op.to]; });
        return "";
      case "alter":
        i = idx(d.cols, op.name);
        d.cols[i] = clone(op.oldCol);
        return "";
    }
    return "";
  }

  /* ---------- operation text ---------- */
  function opDescribe(op, sign) {
    switch (op.kind) {
      case "add": return "+ Add field " + op.col.name + " to book";
      case "remove": return "- Remove field " + op.old.name + " from book";
      case "rename": return "~ Rename field " + op.from + " on book to " + op.to;
      case "alter": return "~ Alter field " + op.name + " on book";
    }
  }

  function opFragment(op) {
    switch (op.kind) {
      case "add": return "book_" + op.col.name;
      case "remove": return "remove_book_" + op.old.name;
      case "rename": return "rename_" + op.from + "_book_" + op.to;
      case "alter": return "alter_book_" + op.name;
    }
  }

  function opCode(op) {
    var L = [];
    var pad = "            ";
    switch (op.kind) {
      case "add":
        L.push("        migrations.AddField(",
          pad + "model_name='book',",
          pad + "name='" + op.col.name + "',",
          pad + "field=" + V.fieldCode(op.col, op.codeDefault) + ",");
        if (op.oneOff) L.push(pad + "preserve_default=False,");
        L.push("        ),");
        break;
      case "remove":
        L.push("        migrations.RemoveField(", pad + "model_name='book',",
          pad + "name='" + op.old.name + "',", "        ),");
        break;
      case "rename":
        L.push("        migrations.RenameField(", pad + "model_name='book',",
          pad + "old_name='" + op.from + "',", pad + "new_name='" + op.to + "',", "        ),");
        break;
      case "alter":
        L.push("        migrations.AlterField(", pad + "model_name='book',",
          pad + "name='" + op.name + "',",
          pad + "field=" + V.fieldCode(op.newCol) + ",", "        ),");
        break;
    }
    return L;
  }

  function migCode(i) {
    if (i === 0) return INIT_CODE;
    var m = migs[i];
    var L = ["from django.db import migrations, models", "", "",
      "class Migration(migrations.Migration):", "",
      "    dependencies = [",
      "        ('library', '" + migs[i - 1].name + "'),",
      "    ]", "", "    operations = ["];
    m.ops.forEach(function (op) { L = L.concat(opCode(op)); });
    L.push("    ]");
    return L.join("\n");
  }

  /* ---------- model schema: what models.py says ---------- */
  function modelSchema() {
    var d = { cols: initialCols(), rows: [] };
    migs.forEach(function (m) { m.ops.forEach(function (op) { fwd(op, d); }); });
    return d.cols;
  }

  function appliedIdx() {
    var a = 0;
    migs.forEach(function (m, i) { if (m.applied) a = i; });
    return a;
  }

  /* ---------- UI helpers ---------- */
  function say(text, kind) {
    var m = $("ev-msg");
    m.textContent = text || "";
    m.className = "msg" + (text ? " " + kind : "");
  }

  function warn(list) {
    var w = $("ev-warn");
    w.innerHTML = "";
    w.className = "msg" + (list.length ? " warn" : "");
    list.forEach(function (t) {
      var p = document.createElement("div");
      p.textContent = t;
      w.appendChild(p);
    });
  }

  function log(cls, text) {
    var d = document.createElement("div");
    d.className = cls;
    d.textContent = text;
    $("ev-term").appendChild(d);
    $("ev-term").scrollTop = $("ev-term").scrollHeight;
  }

  /* ---------- rendering ---------- */
  function renderChain() {
    var c = $("ev-chain");
    c.innerHTML = "";
    var cur = appliedIdx();
    migs.forEach(function (m, i) {
      if (i > 0) {
        var ar = document.createElement("span");
        ar.className = "carrow"; ar.textContent = "→";
        c.appendChild(ar);
      }
      var b = document.createElement("button");
      b.type = "button";
      b.className = "cnode" + (m.applied ? " applied" : "") + (i === cur ? " current" : "");
      b.setAttribute("aria-label", "Migrate library to " + m.name +
        (m.applied ? " (applied)" : " (not applied)"));
      b.title = "Migrate to " + m.name;
      var dot = document.createElement("span");
      dot.className = "dot";
      var lab = document.createElement("span");
      lab.className = "clab"; lab.textContent = m.name;
      b.appendChild(dot); b.appendChild(lab);
      b.addEventListener("click", function () { migrateTo(i); });
      c.appendChild(b);
    });
    $("ev-migrate").disabled = cur === migs.length - 1;
  }

  function renderTable() {
    var sig = {};
    var h = '<table class="data"><caption>library_book</caption><thead><tr>';
    h += "<th>id<small>integer &middot; PK</small></th>";
    var flashCols = [];
    db.cols.forEach(function (c) {
      var s = JSON.stringify(c);
      sig[c.name] = s;
      var f = prevSig && prevSig[c.name] !== s;
      flashCols.push(f);
      h += '<th class="' + (f ? "flash" : "") + '">' + V.esc(c.name) + "<small>" +
        V.esc(V.sqlType(c)) + (c.null ? " NULL" : "") + "</small></th>";
    });
    h += "</tr></thead><tbody>";
    db.rows.forEach(function (r) {
      h += "<tr><td>" + r.id + "</td>";
      db.cols.forEach(function (c, k) {
        h += '<td class="' + (flashCols[k] ? "flash" : "") + '">' + V.cell(r[c.name]) + "</td>";
      });
      h += "</tr>";
    });
    prevSig = sig;
    $("ev-table").innerHTML = h + "</tbody></table>";
  }

  function renderModel() {
    var L = ["class Book(models.Model):"];
    modelSchema().forEach(function (c) {
      L.push("    " + c.name + " = " + V.fieldCode(c));
    });
    $("ev-model").innerHTML = V.py(L.join("\n"));
  }

  function fillSelect(id, names, keep) {
    var s = $(id), old = keep || s.value;
    s.innerHTML = "";
    names.forEach(function (n) {
      var o = document.createElement("option");
      o.value = n; o.textContent = n;
      s.appendChild(o);
    });
    if (names.indexOf(old) !== -1) s.value = old;
  }

  function renderPick() {
    var s = $("ev-pick");
    s.innerHTML = "";
    migs.forEach(function (m, i) {
      var o = document.createElement("option");
      o.value = i; o.textContent = m.name;
      s.appendChild(o);
    });
    if (picked >= migs.length) picked = migs.length - 1;
    s.value = picked;
    $("ev-code").innerHTML = V.py(migCode(picked));
  }

  function renderForms() {
    var names = modelSchema().map(function (c) { return c.name; });
    fillSelect("ev-r-field", names);
    fillSelect("ev-n-field", names);
    var before = $("ev-l-field").value;
    fillSelect("ev-l-field", names);
    if ($("ev-l-field").value !== before) prefillAlter();
  }

  function renderAll() {
    renderChain();
    renderTable();
    renderModel();
    renderPick();
    renderForms();
  }

  /* ---------- form behaviour ---------- */
  function currentOp() {
    return document.querySelector("#ev-ops .on").getAttribute("data-op");
  }

  function showOp(op) {
    document.querySelectorAll("#ev-ops button").forEach(function (b) {
      var on = b.getAttribute("data-op") === op;
      b.classList.toggle("on", on);
      b.setAttribute("aria-selected", on ? "true" : "false");
    });
    document.querySelectorAll("#evosim .opform").forEach(function (f) {
      f.hidden = f.getAttribute("data-op") !== op;
    });
    say("", "");
  }

  function updateAdd() {
    var t = $("ev-a-type").value;
    $("ev-a-boolwrap").hidden = t !== "BooleanField";
    $("ev-a-default").parentNode.hidden = t === "BooleanField";
    $("ev-a-default").placeholder = t === "DateField" ? "YYYY-MM-DD" : "none";
  }

  function updateAlter() {
    $("ev-l-lenwrap").hidden = $("ev-l-type").value !== "CharField";
  }

  function prefillAlter() {
    var c = modelSchema().filter(function (x) { return x.name === $("ev-l-field").value; })[0];
    if (!c) return;
    $("ev-l-type").value = c.type;
    if (c.type === "CharField") $("ev-l-len").value = c.maxLength;
    updateAlter();
  }

  /* ---------- makemigrations ---------- */
  function addMigration(ops, extraLines) {
    var n = migs.length;
    var frags = ops.map(opFragment);
    var name = frags[0];
    for (var i = 1; i < frags.length; i++) name += "_" + frags[i];
    var full = ("0000" + (n + 1)).slice(-4) + "_" + name;
    migs.push({ name: full, ops: ops, applied: false });
    picked = migs.length - 1;

    log("cmd", "$ python manage.py makemigrations library");
    (extraLines || []).forEach(function (l) { log(l.cls || "out", l.text); });
    log("out", "Migrations for 'library':");
    log("out", "  library/migrations/" + full + ".py");
    ops.forEach(function (op) { log("out", "    " + opDescribe(op)); });
    renderAll();
    say("Created " + full + ".py. The database has not changed yet: click migrate, or click this migration in the chain.", "ok");
  }

  function promptLines(table, field, val) {
    return [
      { text: "It is impossible to add a non-nullable field '" + field + "' to " + table + " without specifying a default. This is because the database needs something to populate existing rows." },
      { text: "Please select a fix:" },
      { text: " 1) Provide a one-off default now (will be set on all existing rows with a null value for this column)" },
      { text: " 2) Quit and manually define a default value in models.py." },
      { text: "Select an option: 1" },
      { text: ">>> " + val }
    ];
  }

  function makeAddOp(col, rawDefault) {
    /* col: field definition; rawDefault: string/null the user typed */
    var op = { kind: "add" };
    var final = clone(col);
    if (!col.null && rawDefault !== null) {
      op.oneOff = true;
      final.def = null;
      op.codeDefault = V.pyDefault(V.col({ type: col.type, def: rawDefault }));
      op.fill = coerce(col.type, rawDefault);
    } else {
      op.fill = col.def !== null ? coerce(col.type, col.def) : null;
    }
    op.col = final;
    return op;
  }

  function makeAdd() {
    var name = $("ev-a-name").value.trim();
    var type = $("ev-a-type").value;
    var existing = modelSchema().map(function (c) { return c.name; });
    var err = V.checkFieldName(name, existing);
    if (err) return say(err, "error");

    var raw = null;
    if (type === "BooleanField") raw = $("ev-a-defbool").value || null;
    else {
      var d = V.parseDefault(type, $("ev-a-default").value.trim());
      if (d.err) return say(d.err, "error");
      raw = d.value;
      if (type === "DateField" && raw !== null && !/^\d{4}-\d{2}-\d{2}$/.test(raw)) {
        return say("Use the format YYYY-MM-DD for a date default.", "error");
      }
    }

    var col = V.col({ name: name, type: type, null: $("ev-a-null").checked,
      def: $("ev-a-null").checked ? raw : null });

    if (!col.null && raw === null) {
      log("cmd", "$ python manage.py makemigrations library");
      log("out", "It is impossible to add a non-nullable field '" + name + "' to book without specifying a default. This is because the database needs something to populate existing rows.");
      log("out", "(No migration was created.)");
      return say("Django would stop here: the table already has rows and a NOT NULL column needs a value for each. Give the field a default (used once to fill the existing rows) or tick null=True.", "error");
    }

    var op = makeAddOp(col, raw);
    var lines = op.oneOff ? promptLines("book", name, V.pyDefault(V.col({ type: type, def: raw }))) : [];
    addMigration([op], lines);
    $("ev-a-name").value = ""; $("ev-a-default").value = "";
    $("ev-a-null").checked = false;
  }

  function makeRemove() {
    var name = $("ev-r-field").value;
    var schema = modelSchema();
    var i = idx(schema, name);
    if (i === -1) return say("There is no field to remove.", "error");
    addMigration([{ kind: "remove", old: clone(schema[i]), index: i }]);
    say("Created the migration. Applying it will drop the column '" + name + "' and its data.", "warn");
  }

  function makeRename() {
    var from = $("ev-n-field").value;
    var to = $("ev-n-new").value.trim();
    var schema = modelSchema();
    var i = idx(schema, from);
    if (i === -1) return say("There is no field to rename.", "error");
    var others = schema.map(function (c) { return c.name; })
      .filter(function (n) { return n !== from; });
    var err = V.checkFieldName(to, others);
    if (err) return say(err, "error");
    if (to === from) return say("Choose a different name.", "error");

    var col = schema[i];
    var q = "Was book." + from + " renamed to book." + to + " (a " + col.type + ")? [y/N]";
    if ($("ev-n-answer").value === "y") {
      addMigration([{ kind: "rename", from: from, to: to }],
        [{ text: q + " y" }]);
      return;
    }

    /* Answer N: Django sees a removal plus an addition */
    var newCol = clone(col); newCol.name = to;
    var lines = [{ text: q + " N" }];
    var raw = newCol.def;
    if (!newCol.null && raw === null) {
      raw = zeroFor(col.type);
      lines = lines.concat(promptLines("book", to, V.pyDefault(V.col({ type: col.type, def: raw }))));
      lines.push({ text: "(The simulation entered a one-off default for you.)" });
    }
    var addOp = makeAddOp(newCol, raw);
    addMigration([{ kind: "remove", old: clone(col), index: i }, addOp], lines);
    say("Because you answered N, Django generated RemoveField + AddField. Once applied, the data in '" + from + "' will be gone.", "warn");
  }

  function makeAlter() {
    var name = $("ev-l-field").value;
    var schema = modelSchema();
    var i = idx(schema, name);
    if (i === -1) return say("There is no field to alter.", "error");
    var oldCol = schema[i];
    var newCol = clone(oldCol);
    newCol.type = $("ev-l-type").value;
    if (newCol.type === "CharField") {
      var len = parseInt($("ev-l-len").value, 10);
      if (!(len >= 1)) return say("CharField needs a max_length of at least 1.", "error");
      newCol.maxLength = len;
    }
    if (JSON.stringify(newCol) === JSON.stringify(oldCol)) {
      return say("That is the same as the current definition, so there is nothing to migrate. Django would say: No changes detected.", "error");
    }
    addMigration([{ kind: "alter", name: name, oldCol: clone(oldCol), newCol: newCol }]);
    if (newCol.type !== oldCol.type) {
      say("Created the migration. Changing the type can fail or alter data on a real database, so test it first.", "warn");
    }
  }

  /* ---------- migrate ---------- */
  function migrateTo(t) {
    var cur = appliedIdx();
    var last = migs.length - 1;
    var cmd = "$ python manage.py migrate library" +
      (t === last ? "" : " " + migs[t].name.slice(0, 4));
    log("cmd", cmd);
    log("out", "Operations to perform:");
    log("out", t === last ? "  Apply all migrations: library"
      : "  Target specific migration: " + migs[t].name + ", from library");
    log("out", "Running migrations:");

    var warns = [];
    if (t === cur) {
      log("out", "  No migrations to apply.");
    } else if (t > cur) {
      for (var i = cur + 1; i <= t; i++) {
        migs[i].ops.forEach(function (op) {
          var w = fwd(op, db); if (w) warns.push(w);
        });
        migs[i].applied = true;
        log("out", "  Applying library." + migs[i].name + "... OK");
      }
    } else {
      log("out", "  Rendering model states... DONE");
      for (var j = cur; j > t; j--) {
        for (var k = migs[j].ops.length - 1; k >= 0; k--) {
          var w2 = back(migs[j].ops[k], db); if (w2) warns.push(w2);
        }
        migs[j].applied = false;
        log("out", "  Unapplying library." + migs[j].name + "... OK");
      }
    }
    warn(warns);
    renderChain();
    renderTable();
    say("", "");
  }

  /* ---------- wiring ---------- */
  function reset() {
    db = freshDb();
    migs = [{ name: "0001_initial", ops: [], applied: true }];
    prevSig = null; picked = 0;
    $("ev-term").innerHTML = "";
    $("ev-a-name").value = ""; $("ev-n-new").value = "";
    showOp("add");
    warn([]);
    renderAll();
    updateAdd();
    prefillAlter();
  }

  document.querySelectorAll("#ev-ops button").forEach(function (b) {
    b.addEventListener("click", function () { showOp(b.getAttribute("data-op")); });
  });
  $("ev-a-type").addEventListener("change", updateAdd);
  $("ev-l-type").addEventListener("change", updateAlter);
  $("ev-l-field").addEventListener("change", prefillAlter);
  $("ev-pick").addEventListener("change", function () {
    picked = parseInt($("ev-pick").value, 10);
    $("ev-code").innerHTML = V.py(migCode(picked));
  });
  $("ev-make").addEventListener("click", function () {
    var op = currentOp();
    if (op === "add") makeAdd();
    else if (op === "remove") makeRemove();
    else if (op === "rename") makeRename();
    else makeAlter();
  });
  $("ev-migrate").addEventListener("click", function () { migrateTo(migs.length - 1); });
  $("ev-reset").addEventListener("click", reset);
  $("ev-clear").addEventListener("click", function () { $("ev-term").innerHTML = ""; });

  reset();
})();
