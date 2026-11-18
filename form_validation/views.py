from django.shortcuts import render
from django.urls import reverse

from .forms import RegistrationForm

LAB_TITLE = "Custom Form Validation using clean() in Django"

# Order here = order of the sidebar menu.
TAB_DEFINITIONS = [
    ("introduction", "Introduction"),
    ("objective", "Objective"),
    ("theory", "Theory"),
    ("experiment", "Experiment"),
    ("assessment", "Assessment"),
    ("feedback", "Feedback"),
]

# Questions for the Assessment tab.
# "answer" is the key of the correct option.
QUIZ_QUESTIONS = [
    {
        "id": 1,
        "text": "Which method validates ONLY the field named 'age' in a Django form?",
        "options": [
            ("a", "clean()"),
            ("b", "clean_age()"),
            ("c", "validate_age()"),
            ("d", "is_valid_age()"),
        ],
        "answer": "b",
        "explanation": "Django automatically calls clean_<fieldname>() for each field, so clean_age() validates the 'age' field.",
    },
    {
        "id": 2,
        "text": "What must a clean_<fieldname>() method always do when validation succeeds?",
        "options": [
            ("a", "Return None"),
            ("b", "Return True"),
            ("c", "Return the cleaned value of the field"),
            ("d", "Save the form to the database"),
        ],
        "answer": "c",
        "explanation": "The returned value replaces the field's value in cleaned_data, so forgetting the return statement makes the field None.",
    },
    {
        "id": 3,
        "text": "Which method should you use to compare 'password' and 'confirm_password'?",
        "options": [
            ("a", "clean()"),
            ("b", "clean_password()"),
            ("c", "clean_confirm_password()"),
            ("d", "__init__()"),
        ],
        "answer": "a",
        "explanation": "Rules that depend on more than one field belong in the form-level clean() method, which runs after all field-level checks.",
    },
    {
        "id": 4,
        "text": "Which exception is raised to report a validation problem in a form?",
        "options": [
            ("a", "ValueError"),
            ("b", "FormError"),
            ("c", "ValidationError"),
            ("d", "InvalidInputException"),
        ],
        "answer": "c",
        "explanation": "django.core.exceptions.ValidationError is the standard exception for validation failures.",
    },
    {
        "id": 5,
        "text": "Inside clean(), how do you attach an error message to one specific field?",
        "options": [
            ("a", "self.add_error('field_name', message)"),
            ("b", "self.errors.append(message)"),
            ("c", "return message"),
            ("d", "print(message)"),
        ],
        "answer": "a",
        "explanation": "add_error('field_name', ...) shows the message next to that field. add_error(None, ...) creates a non-field error.",
    },
]

FEEDBACK_RATINGS = ["1", "2", "3", "4", "5"]


def _render_tab(request, slug, extra_context=None):
    """Render templates/form_validation/<slug>.html with the shared lab context."""
    tabs = [
        {
            "slug": tab_slug,
            "label": label,
            "url": reverse(f"form_validation:{tab_slug}"),
            "is_active": tab_slug == slug,
        }
        for tab_slug, label in TAB_DEFINITIONS
    ]

    context = {
        "lab_title": LAB_TITLE,
        "tabs": tabs,
        "active_tab": slug,
    }
    if extra_context:
        context.update(extra_context)

    return render(request, f"form_validation/{slug}.html", context)


# ---------------------------------------------------------------------------
# 1. Introduction
# ---------------------------------------------------------------------------
def introduction(request):
    return _render_tab(request, "introduction")


# ---------------------------------------------------------------------------
# 2. Objective
# ---------------------------------------------------------------------------
def objective(request):
    return _render_tab(request, "objective")


# ---------------------------------------------------------------------------
# 3. Theory
# ---------------------------------------------------------------------------
def theory(request):
    return _render_tab(request, "theory")


# ---------------------------------------------------------------------------
# 4. Experiment (the live demo of clean() validation)
# ---------------------------------------------------------------------------
def experiment(request):
    """
    GET  -> show an empty registration form.
    POST -> validate the submitted data with RegistrationForm.
            success = True  : all validation passed
            error   = True  : at least one validation error was found
    """
    submitted = False
    success = False
    error = False
    error_count = 0
    submitted_data = None

    if request.method == "POST":
        submitted = True
        form = RegistrationForm(request.POST)

        if form.is_valid():
            success = True
            # Never display or store passwords in the demo output.
            submitted_data = {
                "username": form.cleaned_data["username"],
                "email": form.cleaned_data["email"],
                "age": form.cleaned_data["age"],
            }
            # A real project would create the user here, for example:
            # User.objects.create_user(username, email, password)
        else:
            error = True
            # Count every individual error message (field + non-field).
            error_count = sum(len(messages) for messages in form.errors.values())
    else:
        form = RegistrationForm()

    return _render_tab(
        request,
        "experiment",
        {
            "form": form,
            "submitted": submitted,
            "success": success,
            "error": error,
            "error_count": error_count,
            "submitted_data": submitted_data,
        },
    )


# ---------------------------------------------------------------------------
# 5. Assessment (multiple-choice quiz, scored on the server)
# ---------------------------------------------------------------------------
def assessment(request):
    """
    GET  -> show the quiz.
    POST -> score the answers and mark each option correct / wrong.
    """
    submitted = request.method == "POST"
    score = 0
    questions = []

    for q in QUIZ_QUESTIONS:
        selected = request.POST.get(f"q{q['id']}") if submitted else None
        is_correct = selected == q["answer"]
        if is_correct:
            score += 1

        options = [
            {
                "key": key,
                "text": text,
                "is_selected": selected == key,
                "is_correct": key == q["answer"],
            }
            for key, text in q["options"]
        ]

        questions.append(
            {
                "id": q["id"],
                "field_name": f"q{q['id']}",
                "text": q["text"],
                "options": options,
                "explanation": q["explanation"],
                "answered": selected is not None,
                "is_correct": is_correct,
            }
        )

    total = len(QUIZ_QUESTIONS)
    percentage = round((score / total) * 100) if submitted else 0

    return _render_tab(
        request,
        "assessment",
        {
            "questions": questions,
            "submitted": submitted,
            "score": score,
            "total": total,
            "percentage": percentage,
            "passed": percentage >= 60,
        },
    )


# ---------------------------------------------------------------------------
# 6. Feedback
# ---------------------------------------------------------------------------
def feedback(request):
    """
    GET  -> show the feedback form.
    POST -> validate name, rating and comments, then set success / error flags.
    """
    submitted = False
    success = False
    error = False
    errors = {}
    values = {"name": "", "rating": "", "comments": ""}

    if request.method == "POST":
        submitted = True
        values = {
            "name": request.POST.get("name", "").strip(),
            "rating": request.POST.get("rating", "").strip(),
            "comments": request.POST.get("comments", "").strip(),
        }

        if not values["name"]:
            errors["name"] = "Please enter your name."

        if values["rating"] not in FEEDBACK_RATINGS:
            errors["rating"] = "Please choose a rating from 1 to 5."

        if len(values["comments"]) < 10:
            errors["comments"] = "Please write at least 10 characters of feedback."

        if errors:
            error = True
        else:
            success = True
            # A real project would save the feedback to a model here.
            values = {"name": "", "rating": "", "comments": ""}

    return _render_tab(
        request,
        "feedback",
        {
            "submitted": submitted,
            "success": success,
            "error": error,
            "errors": errors,
            "values": values,
            "ratings": FEEDBACK_RATINGS,
        },
    )