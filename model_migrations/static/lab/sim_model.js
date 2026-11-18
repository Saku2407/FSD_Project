/* Experiment 1 simulation: Model Builder.
   Design a model; see models.py, the table and the SQL update live. */
(function () {
  "use strict";
  var V = window.VLab, $ = V.$;
  if (!$("modelsim")) return;

  var state, lastAdded = null;

  function starter() {
    return {
      cls: "Book",
      str: true,
      fields: [
        V.col({ name: "title", type: "CharField", maxLength: 100 }),
        V.col({ name: "pages", type: "IntegerField" })
      ]
    };
  }

  function example() {
    return {
      cls: "Book",
      str: true,
      fields: [
        V.col({ name: "title", type: "CharField", maxLength: 100 }),
        V.col({ name: "isbn", type: "CharField", maxLength: 13, unique: true }),
        V.col({ name: "pages", type: "IntegerField" }),
        V.col({ name: "published", type: "DateField", null: true, blank: true }),
        V.col({ name: "author", type: "ForeignKey", onDelete: "CASCADE" })
      ]
    };
  }

  /* ---------- messages ---------- */
  function say(text, kind) {
    var m = $("ms-msg");
    m.textContent = text || "";
    m.className = "msg" + (text ? " " + kind : "");
  }

  /* ---------- rendering ---------- */
  function tableName() { return V.APP + "_" + state.cls.toLowerCase(); }

  function codeText() {
    var L = ["# " + V.APP + "/models.py", "from django.db import models", ""];
    var hasFk = state.fields.some(function (f) { return f.type === "ForeignKey"; });
    if (hasFk) {
      L.push("class Author(models.Model):",
        "    name = models.CharField(max_length=100)", "", "");
    }
    L.push("class " + state.cls + "(models.Model):");
    if (!state.fields.length) L.push("    pass");
    state.fields.forEach(function (f) {
      L.push("    " + f.name + " = " + V.fieldCode(f));
    });
    if (state.str) {
      var first = state.fields.filter(function (f) { return f.type === "CharField"; })[0];
      L.push("", "    def __str__(self):");
      L.push(first ? "        return self." + first.name
                   : "        return f\"" + state.cls + " #{self.pk}\"");
    }
    return L.join("\n");
  }

  function sqlText() {
    var cols = ['"id" integer NOT NULL PRIMARY KEY AUTOINCREMENT'];
    state.fields.forEach(function (f) { cols.push(V.columnSql(f)); });
    var s = 'CREATE TABLE "' + tableName() + '" (\n  ' + cols.join(",\n  ") + "\n);";
    state.fields.forEach(function (f) {
      if (f.type === "ForeignKey") {
        s += '\n-- Django also creates an index on "' + V.dbName(f) + '"';
      }
    });
    return s;
  }

  function renderTable() {
    var cols = [{ name: "id", type: "integer", pk: true, f: null }];
    state.fields.forEach(function (f) {
      cols.push({ name: V.dbName(f), type: V.sqlType(f), f: f,
        isNew: f.name === lastAdded });
    });
    var h = '<table class="data"><caption>' + V.esc(tableName()) + "</caption><thead><tr>";
    cols.forEach(function (c) {
      h += '<th class="' + (c.isNew ? "flash" : "") + '">' + V.esc(c.name) +
        "<small>" + V.esc(c.type) + (c.pk ? " &middot; PK" : "") + "</small></th>";
    });
    h += "</tr></thead><tbody>";
    for (var r = 0; r < 3; r++) {
      h += "<tr>";
      cols.forEach(function (c) {
        var v = c.pk ? r + 1 : V.sample(c.f, r);
        h += '<td class="' + (c.isNew ? "flash" : "") + '">' + V.cell(v) + "</td>";
      });
      h += "</tr>";
    }
    return h + "</tbody></table>";
  }

  function renderList() {
    var ul = $("ms-fields");
    ul.innerHTML = "";
    if (!state.fields.length) {
      var li = document.createElement("li");
      li.className = "empty";
      li.textContent = "No fields yet. Only the automatic id column exists.";
      ul.appendChild(li);
    }
    state.fields.forEach(function (f, i) {
      var li = document.createElement("li");
      var t = document.createElement("span");
      t.innerHTML = "<code>" + V.esc(f.name) + "</code> &middot; " + V.esc(f.type);
      var b = document.createElement("button");
      b.type = "button"; b.className = "mini";
      b.textContent = "remove";
      b.setAttribute("aria-label", "Remove field " + f.name);
      b.addEventListener("click", function () {
        state.fields.splice(i, 1);
        lastAdded = null;
        say("Removed '" + f.name + "'.", "ok");
        render();
      });
      li.appendChild(t); li.appendChild(b);
      ul.appendChild(li);
    });
  }

  function render() {
    $("ms-code").innerHTML = V.py(codeText());
    $("ms-sql").innerHTML = V.sql(sqlText());
    $("ms-table").innerHTML = renderTable();
    renderList();
    $("ms-class").value = state.cls;
    $("ms-str").checked = state.str;
  }

  /* ---------- form behaviour ---------- */
  function updateParams() {
    var t = $("ms-type").value;
    document.querySelectorAll("#modelsim [data-for]").forEach(function (n) {
      n.hidden = n.getAttribute("data-for").split(" ").indexOf(t) === -1;
    });
    document.querySelectorAll("#modelsim [data-hide]").forEach(function (n) {
      n.hidden = n.getAttribute("data-hide").split(" ").indexOf(t) !== -1;
    });
    if (t === "BooleanField") $("ms-unique").checked = false;
  }

  function intVal(id) { return parseInt($(id).value, 10); }

  function addField() {
    var name = $("ms-name").value.trim();
    var type = $("ms-type").value;
    var existing = state.fields.map(function (f) { return f.name; });

    var err = V.checkFieldName(name, existing);
    if (err) return say(err, "error");

    var c = V.col({
      name: name, type: type,
      null: $("ms-null").checked, blank: $("ms-blank").checked,
      unique: $("ms-unique").checked, autoNowAdd: $("ms-autonow").checked,
      onDelete: $("ms-ondelete").value
    });

    if (type === "CharField") {
      c.maxLength = intVal("ms-maxlen");
      if (!(c.maxLength >= 1)) return say("CharField needs a max_length of at least 1.", "error");
    }
    if (type === "DecimalField") {
      c.maxDigits = intVal("ms-digits"); c.decimalPlaces = intVal("ms-places");
      if (!(c.maxDigits >= 1)) return say("max_digits must be at least 1.", "error");
      if (!(c.decimalPlaces >= 0) || c.decimalPlaces > c.maxDigits) {
        return say("decimal_places must be between 0 and max_digits.", "error");
      }
    }
    if (type === "ForeignKey" && c.onDelete === "SET_NULL" && !c.null) {
      return say("on_delete=SET_NULL needs null=True, otherwise Django cannot set the column to NULL.", "error");
    }
    if (type === "BooleanField") {
      c.def = $("ms-defbool").value || null;
    } else if (["CharField", "TextField", "EmailField", "IntegerField", "FloatField"].indexOf(type) !== -1) {
      var d = V.parseDefault(type, $("ms-default").value.trim());
      if (d.err) return say(d.err, "error");
      c.def = d.value;
    }

    state.fields.push(c);
    lastAdded = name;

    var hint = "Added '" + name + "'.";
    var kind = "ok";
    if (c.null && (type === "CharField" || type === "TextField" || type === "EmailField")) {
      hint += " Hint: Django convention is to avoid null=True on text fields. Use blank=True and store an empty string, so 'no value' has only one form.";
      kind = "warn";
    } else if (c.blank && !c.null && type !== "CharField" && type !== "TextField" && type !== "EmailField") {
      hint += " Note: blank=True only relaxes form validation. For a non-text field you usually need null=True too, or saving an empty value will fail in the database.";
      kind = "warn";
    }
    say(hint, kind);

    $("ms-name").value = "";
    $("ms-default").value = "";
    $("ms-null").checked = false;
    $("ms-blank").checked = false;
    $("ms-unique").checked = false;
    $("ms-autonow").checked = false;
    render();
    $("ms-name").focus();
  }

  function setClass() {
    var v = $("ms-class").value.trim();
    if (/^[A-Z][A-Za-z0-9]*$/.test(v)) {
      state.cls = v;
      say("", "");
      render();
      $("ms-class").value = v;
    } else {
      say("Model names use CapWords, e.g. Book or LibraryMember. Keeping '" + state.cls + "' for now.", "warn");
    }
  }

  $("ms-add").addEventListener("click", addField);
  $("ms-name").addEventListener("keydown", function (e) {
    if (e.key === "Enter") { e.preventDefault(); addField(); }
  });
  $("ms-type").addEventListener("change", updateParams);
  $("ms-class").addEventListener("change", setClass);
  $("ms-class").addEventListener("input", function () {
    var v = $("ms-class").value.trim();
    if (/^[A-Z][A-Za-z0-9]*$/.test(v)) { state.cls = v; render(); $("ms-class").value = $("ms-class").value; }
  });
  $("ms-str").addEventListener("change", function () {
    state.str = $("ms-str").checked; render();
  });
  $("ms-reset").addEventListener("click", function () {
    state = starter(); lastAdded = null; say("Reset.", "ok"); render();
  });
  $("ms-example").addEventListener("click", function () {
    state = example(); lastAdded = null; say("Loaded an example.", "ok"); render();
  });

  state = starter();
  updateParams();
  render();
})();
