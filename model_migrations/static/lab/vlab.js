/* Shared helpers for the simulations: escaping, syntax colouring,
   field -> Python / SQL generation. No dependencies. */
(function () {
  "use strict";
  var V = (window.VLab = {});

  V.APP = "library";

  V.esc = function (s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  };

  /* Tokenise `text` with `re` (global, with capture groups). `cls` maps the
     index of the matching group to a CSS class. Everything is escaped. */
  function colour(text, re, cls) {
    var out = "", last = 0, m;
    re.lastIndex = 0;
    while ((m = re.exec(text)) !== null) {
      out += V.esc(text.slice(last, m.index));
      var g = 1;
      while (g < m.length && m[g] === undefined) g++;
      out += '<span class="' + cls[g - 1] + '">' + V.esc(m[0]) + "</span>";
      last = m.index + m[0].length;
      if (m[0].length === 0) re.lastIndex++;
    }
    return out + V.esc(text.slice(last));
  }

  var PY = /(#[^\n]*)|('(?:[^'\\\n]|\\.)*'|"(?:[^"\\\n]|\\.)*")|(\b(?:class|def|return|import|from|self|True|False|None)\b)|(\b(?:models|migrations)\.\w+)|(\b\d+\b)/g;
  V.py = function (text) {
    return colour(text, PY, ["tk-c", "tk-s", "tk-k", "tk-m", "tk-n"]);
  };

  var SQL = /(--[^\n]*)|("[^"\n]*")|(\b(?:CREATE|TABLE|NOT|NULL|PRIMARY|KEY|AUTOINCREMENT|UNIQUE|REFERENCES|DEFERRABLE|INITIALLY|DEFERRED|BEGIN|COMMIT|INDEX|ON)\b)|(\b\d+\b)/g;
  V.sql = function (text) {
    return colour(text, SQL, ["tk-c", "tk-s", "tk-k", "tk-n"]);
  };

  /* ---------- field model ----------
     col = {name, type, maxLength, maxDigits, decimalPlaces, onDelete,
            null, blank, unique, autoNowAdd, def}
     `def` is null (no default) or a string. */
  V.col = function (o) {
    var c = {
      name: "", type: "CharField", maxLength: 100, maxDigits: 6,
      decimalPlaces: 2, onDelete: "CASCADE", null: false, blank: false,
      unique: false, autoNowAdd: false, def: null
    };
    for (var k in o) c[k] = o[k];
    return c;
  };

  V.TYPE_LABEL = {
    CharField: "varchar", TextField: "text", IntegerField: "integer",
    FloatField: "real", DecimalField: "decimal", BooleanField: "bool",
    DateField: "date", DateTimeField: "datetime", EmailField: "varchar(254)",
    ForeignKey: "bigint"
  };

  V.sqlType = function (c) {
    switch (c.type) {
      case "CharField": return "varchar(" + c.maxLength + ")";
      case "EmailField": return "varchar(254)";
      default: return V.TYPE_LABEL[c.type];
    }
  };

  V.dbName = function (c) {
    return c.type === "ForeignKey" ? c.name + "_id" : c.name;
  };

  function pyDefault(c) {
    if (c.def === null || c.def === undefined) return null;
    switch (c.type) {
      case "IntegerField": case "FloatField": case "BooleanField":
        return c.def;
      default:
        return "'" + String(c.def).replace(/\\/g, "\\\\")
          .replace(/'/g, "\\'") + "'";
    }
  }

  /* Python source of the field, e.g. models.CharField(max_length=100) */
  V.fieldCode = function (c, forceDefault) {
    var a = [];
    if (c.type === "ForeignKey") {
      a.push("Author", "on_delete=models." + c.onDelete);
    }
    if (c.type === "CharField") a.push("max_length=" + c.maxLength);
    if (c.type === "DecimalField") {
      a.push("max_digits=" + c.maxDigits, "decimal_places=" + c.decimalPlaces);
    }
    if (c.null) a.push("null=True");
    if (c.blank) a.push("blank=True");
    if (c.unique) a.push("unique=True");
    if (c.autoNowAdd) a.push("auto_now_add=True");
    var d = forceDefault !== undefined ? forceDefault : pyDefault(c);
    if (d !== null && d !== undefined) a.push("default=" + d);
    return "models." + c.type + "(" + a.join(", ") + ")";
  };

  V.pyDefault = pyDefault;

  /* One column of CREATE TABLE */
  V.columnSql = function (c) {
    var s = '"' + V.dbName(c) + '" ' + V.sqlType(c) +
      (c.null ? " NULL" : " NOT NULL");
    if (c.type === "ForeignKey") {
      s += ' REFERENCES "' + V.APP + '_author" ("id") DEFERRABLE INITIALLY DEFERRED';
    }
    if (c.unique) s += " UNIQUE";
    return s;
  };

  var RESERVED = ["class", "def", "import", "return", "from", "pass", "none",
    "true", "false", "lambda", "global", "del", "in", "is", "not", "or", "and"];

  /* Returns an error string, or "" if the name is acceptable. */
  V.checkFieldName = function (name, existing) {
    if (!name) return "Give the field a name.";
    if (!/^[a-z][a-z0-9_]*$/.test(name)) {
      return "Use lower-case letters, digits and underscores, starting with a letter (e.g. page_count).";
    }
    if (name.indexOf("__") !== -1 || /_$/.test(name)) {
      return "Django does not allow double underscores or a trailing underscore in field names.";
    }
    if (name === "id" || name === "pk") {
      return "'" + name + "' is reserved: Django already adds the id primary key for you.";
    }
    if (RESERVED.indexOf(name) !== -1) {
      return "'" + name + "' is a Python keyword.";
    }
    if (existing.indexOf(name) !== -1) {
      return "A field called '" + name + "' already exists.";
    }
    return "";
  };

  /* Validate a default value for the type. Returns {err, value}. */
  V.parseDefault = function (type, raw) {
    if (raw === null || raw === undefined || raw === "") {
      return { err: "", value: null };
    }
    if (type === "IntegerField" && !/^-?\d+$/.test(raw)) {
      return { err: "Default for an IntegerField must be a whole number." };
    }
    if (type === "FloatField" && !/^-?\d+(\.\d+)?$/.test(raw)) {
      return { err: "Default for a FloatField must be a number." };
    }
    return { err: "", value: raw };
  };

  /* A sample cell value for row i (0-based) */
  V.sample = function (c, i) {
    if (c.null && i === 2) return null;
    var n = i + 1;
    switch (c.type) {
      case "CharField": return c.name + " " + n;
      case "TextField": return "Some longer text " + n;
      case "IntegerField": return n * 10;
      case "FloatField": return n * 1.5;
      case "DecimalField": return (n * 9.99).toFixed(c.decimalPlaces);
      case "BooleanField": return n % 2 === 1;
      case "DateField": return "2025-01-0" + n;
      case "DateTimeField": return "2025-01-0" + n + " 10:00:00";
      case "EmailField": return "user" + n + "@example.com";
      case "ForeignKey": return n;
    }
    return "";
  };

  /* Render a cell value as HTML */
  V.cell = function (v) {
    if (v === null || v === undefined) return '<i class="null">NULL</i>';
    if (v === true) return "True";
    if (v === false) return "False";
    return V.esc(v);
  };

  V.$ = function (id) { return document.getElementById(id); };

  V.reduceMotion = function () {
    return window.matchMedia &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  };
})();
