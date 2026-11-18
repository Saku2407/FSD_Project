

LAB_TITLE = "Creating Django Models and Migrations"
DEPARTMENT = "Computer Science and Engineering"

# Sections shown in the sidebar of every experiment: (url slug, label)
SECTIONS = [
    ("aim", "Aim"),
    ("theory", "Theory"),
    ("video", "Animation"),   
    ("procedure", "Procedure"),
    ("simulation", "Simulation"),
    ("quiz", "Quiz"),
    ("references", "Further Reading"),
]

DOCS = "https://docs.djangoproject.com/en/stable"

EXPERIMENTS = [
    {
        "num": 1,
        "video": "exp1.mp4",
        "title": "Defining Django models",
        "desc": "Turn a Python class into a database table: choose field "
                "types, set options such as null, blank and unique, and "
                "link models with a ForeignKey.",
        "aim": "To design a Django model and understand how each field "
               "definition maps to a column in the database table.",
        "objectives": [
            "Write a model class that inherits from <code>models.Model</code>.",
            "Choose suitable field types (<code>CharField</code>, "
            "<code>IntegerField</code>, <code>DateField</code>, ...).",
            "Explain the difference between <code>null=True</code> and "
            "<code>blank=True</code>.",
            "Relate two models with a <code>ForeignKey</code> and "
            "<code>on_delete</code>.",
            "Predict the table name, column names and SQL that Django will use.",
        ],
        "references": [
            ("Django docs: Models", f"{DOCS}/topics/db/models/"),
            ("Django docs: Model field reference", f"{DOCS}/ref/models/fields/"),
            ("Django tutorial, part 2: Models and the admin site",
             f"{DOCS}/intro/tutorial02/"),
        ],
    },
    {
        "num": 2,
        "video": "exp2.mp4",
        "title": "Making and applying migrations",
        "desc": "Follow the lifecycle models.py → makemigrations → "
                "migration file → migrate → database, and inspect the "
                "SQL Django runs for you.",
        "aim": "To generate migration files from model changes and apply "
               "them to the database using <code>makemigrations</code> and "
               "<code>migrate</code>.",
        "objectives": [
            "Describe what a migration file contains "
            "(<code>dependencies</code> and <code>operations</code>).",
            "Use <code>makemigrations</code>, <code>migrate</code>, "
            "<code>showmigrations</code> and <code>sqlmigrate</code>.",
            "Explain how the <code>django_migrations</code> table records "
            "which migrations have been applied.",
            "State why migration files are committed to version control.",
        ],
        "references": [
            ("Django docs: Migrations", f"{DOCS}/topics/migrations/"),
            ("Django docs: django-admin and manage.py commands",
             f"{DOCS}/ref/django-admin/"),
            ("Django tutorial, part 2: Activating models",
             f"{DOCS}/intro/tutorial02/#activating-models"),
        ],
    },
    {
        "num": 3,
        "title": "Evolving the schema",
        "desc": "Add, remove, rename and alter fields on a live table, "
                "watch the migration chain grow, and roll the database back "
                "to an earlier migration.",
        "aim": "To change an existing model safely, understand the "
               "operations Django generates, and move the database forward "
               "and backward along the migration chain.",
        "objectives": [
            "Recognise <code>AddField</code>, <code>RemoveField</code>, "
            "<code>RenameField</code> and <code>AlterField</code> operations.",
            "Explain why a non-nullable field needs a default when added to "
            "a table that already has rows.",
            "Explain how Django detects a rename, and what is lost if it "
            "does not.",
            "Roll back with <code>migrate &lt;app&gt; &lt;migration&gt;</code> "
            "and describe which data is lost.",
        ],
        "references": [
            ("Django docs: Migration operations",
             f"{DOCS}/ref/migration-operations/"),
            ("Django docs: Writing migrations",
             f"{DOCS}/howto/writing-migrations/"),
            ("Django docs: Squashing migrations",
             f"{DOCS}/topics/migrations/#squashing-migrations"),
        ],
    },
]


def sections_for(exp):
    """Sidebar sections for an experiment (Animation only if it has a video)."""
    return [s for s in SECTIONS if s[0] != "video" or exp.get("video")]


def get_experiment(num):
    for exp in EXPERIMENTS:
        if exp["num"] == num:
            return exp
    return None


# ---------------------------------------------------------------------------
# Quizzes. Each question: q, optional code, options, answer (index), why.
# ---------------------------------------------------------------------------
QUIZZES = {
    1: [
        {
            "q": "Which class must every Django model inherit from?",
            "options": ["models.Model", "models.Table", "forms.Form",
                        "db.Schema"],
            "answer": 0,
            "why": "Subclassing django.db.models.Model is what makes a "
                   "class a model: Django then maps it to a table and gives "
                   "it the ORM manager and methods such as save().",
        },
        {
            "q": "In an app named library, the model class Book is stored "
                 "by default in which table?",
            "options": ["Book", "books", "library_book", "library.Book"],
            "answer": 2,
            "why": "The default table name is <app label>_<model name in "
                   "lower case>, so library_book. It can be changed with "
                   "Meta.db_table.",
        },
        {
            "q": "A model defines no primary key. What does Django do?",
            "options": [
                "Raises an error when the server starts",
                "Adds an auto-incrementing id field automatically",
                "Uses the first field as the primary key",
                "Creates the table without a primary key",
            ],
            "answer": 1,
            "why": "If no field has primary_key=True, Django adds an "
                   "auto-incrementing id column (BigAutoField by default).",
        },
        {
            "q": "Which option lets the database column store NULL?",
            "options": ["blank=True", "null=True", "default=None only",
                        "unique=False"],
            "answer": 1,
            "why": "null=True is a database-level setting. blank=True only "
                   "affects validation in forms and the admin, so an empty "
                   "value is allowed there.",
        },
        {
            "q": "Which argument is required on a ForeignKey?",
            "options": ["related_name", "on_delete", "to_field", "db_index"],
            "answer": 1,
            "why": "on_delete says what happens to this row when the "
                   "referenced row is deleted (for example CASCADE or "
                   "PROTECT). It has been required since Django 2.0.",
        },
        {
            "q": "What column name does this field create in the database?",
            "code": "author = models.ForeignKey(Author, "
                    "on_delete=models.CASCADE)",
            "options": ["author", "author_id", "author_pk", "fk_author"],
            "answer": 1,
            "why": "A ForeignKey stores the key of the related row, so "
                   "Django names the column after the field with _id "
                   "appended: author_id.",
        },
    ],
    2: [
        {
            "q": "Which command creates migration files from the changes "
                 "you made to models.py?",
            "options": ["migrate", "makemigrations", "sqlmigrate",
                        "syncdb"],
            "answer": 1,
            "why": "makemigrations compares your models with the existing "
                   "migrations and writes a new migration file describing "
                   "the difference.",
        },
        {
            "q": "Which command actually changes the database schema?",
            "options": ["makemigrations", "showmigrations", "migrate",
                        "check"],
            "answer": 2,
            "why": "migrate runs the unapplied migrations against the "
                   "database and records them as applied.",
        },
        {
            "q": "Where does Django keep track of which migrations have "
                 "already been applied?",
            "options": [
                "In a file called migrations.lock",
                "In the django_migrations table of the database",
                "In settings.py",
                "In the __pycache__ folder",
            ],
            "answer": 1,
            "why": "Each applied migration gets a row (app, name, applied "
                   "time) in the django_migrations table.",
        },
        {
            "q": "What does this command do?",
            "code": "python manage.py sqlmigrate library 0001",
            "options": [
                "Runs migration 0001 on the database",
                "Deletes migration 0001",
                "Prints the SQL for migration 0001 without running it",
                "Converts the migration into a model",
            ],
            "answer": 2,
            "why": "sqlmigrate only displays the SQL statements a "
                   "migration would execute. It never touches the "
                   "database.",
        },
        {
            "q": "You ran makemigrations but have not run migrate yet. "
                 "What is the state of the database?",
            "options": [
                "Already updated",
                "Unchanged: only a migration file exists so far",
                "Locked until migrate is run",
                "Deleted and re-created",
            ],
            "answer": 1,
            "why": "makemigrations only writes files. The database is "
                   "changed only when you run migrate.",
        },
        {
            "q": "Why should migration files be committed to version "
                 "control?",
            "options": [
                "They are compiled code that Git needs",
                "So every developer and server can build the same schema "
                "by running migrate",
                "Django refuses to start without them in Git",
                "They hold the production data",
            ],
            "answer": 1,
            "why": "Migrations are the history of your schema. Sharing "
                   "them means teammates and deployment servers all reach "
                   "the same database structure.",
        },
    ],
    3: [
        {
            "q": "You add a new field to an existing model. Which "
                 "operation does Django put in the migration?",
            "options": ["CreateModel", "AddField", "AlterField",
                        "RunPython"],
            "answer": 1,
            "why": "Adding a field to a model that already exists "
                   "generates an AddField operation.",
        },
        {
            "q": "You add a non-nullable field with no default to a table "
                 "that already has rows. What happens?",
            "options": [
                "Old rows are silently filled with NULL",
                "Django asks for a one-off default (or you set a default "
                "or null=True yourself)",
                "The table is emptied",
                "The field is ignored",
            ],
            "answer": 1,
            "why": "Existing rows need some value for the new column. "
                   "makemigrations stops and asks for a one-off default, "
                   "or you can give the field a default or null=True.",
        },
        {
            "q": "Which command rolls the library app back to its first "
                 "migration, 0001_initial?",
            "options": [
                "python manage.py migrate library 0001",
                "python manage.py rollback library",
                "python manage.py makemigrations library --undo",
                "python manage.py sqlmigrate library 0001",
            ],
            "answer": 0,
            "why": "Giving migrate a target migration moves the database "
                   "to that point, unapplying later migrations if needed.",
        },
        {
            "q": "You rename a field and answer N when Django asks 'Was "
                 "book.pages renamed to book.page_count?'. What does it "
                 "generate?",
            "options": [
                "A RenameField operation",
                "A RemoveField followed by an AddField",
                "Nothing",
                "An AlterField",
            ],
            "answer": 1,
            "why": "Without your confirmation Django sees one field "
                   "removed and a different one added. The old column's "
                   "data is dropped, which is why the prompt matters.",
        },
        {
            "q": "Which attribute of a migration says which earlier "
                 "migrations must be applied first?",
            "options": ["operations", "initial", "dependencies",
                        "atomic"],
            "answer": 2,
            "why": "dependencies lists (app, migration) pairs that must "
                   "already be applied. It is what forms the chain of "
                   "migrations.",
        },
        {
            "q": "Which operation lets a migration run your own Python "
                 "code, for example to copy or transform data?",
            "options": ["RunSQL only", "RunPython", "AlterModelOptions",
                        "SeparateDatabaseAndState"],
            "answer": 1,
            "why": "RunPython executes a Python function you write. It is "
                   "the usual way to do a data migration (RunSQL can run "
                   "raw SQL, but it is not Python code).",
        },
    ],
}
