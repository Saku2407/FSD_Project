from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required

from django.shortcuts import redirect, render

from django.http import Http404

 

from .forms import CodeSubmissionForm, FeedbackForm, LoginForm, RegistrationForm

from .models import CodeSubmission, Feedback, QuizAttempt

from .quiz_data import QUIZZES

 

 

EXPERIMENTS = {

    "registration": {

        "title": "Experiment 1 — User Registration",

        "short_title": "User Registration",

        "aim": "To implement user registration in Django using the built-in User model and UserCreationForm.",

        "time": "30–45 minutes",

        "overview": "Create a registration form, validate the submitted data, create a user, and store the account securely in the database.",

        "prerequisites": ["Basic Python", "Basic HTML forms", "Django basics", "Basic database concepts"],

        "concepts": [

            ("Authentication", "The process of verifying who a user is.", "Django uses credentials and its authentication system to identify a user."),

            ("UserCreationForm", "A built-in Django form designed for creating users.", "It handles password validation and user creation safely."),

            ("Password hashing", "A one-way transformation used to store passwords without storing the original password.", "The database does not need to keep the actual password."),

            ("CSRF", "Cross-Site Request Forgery protection for unsafe requests.", "The CSRF token helps Django confirm that a POST form came from the application.")

        ],

        "assignment": "Build a registration form with username, full name, email, password and password confirmation. Validate the form and create the user only when the form is valid.",

        "result": "After successful registration, Django stores the user in the auth_user table. The student can then use the created credentials to log in."

    },

    "login": {

        "title": "Experiment 2 — User Login",

        "short_title": "User Login",

        "aim": "To authenticate a registered user in Django and create a login session.",

        "time": "25–40 minutes",

        "overview": "Accept a username and password, verify the credentials with Django's authentication system, call login(), and display the authenticated user.",

        "prerequisites": ["Experiment 1 completed", "Basic forms", "Django views and URLs", "Basic session concept"],

        "concepts": [

            ("authenticate()", "Checks supplied credentials against Django's authentication back end.", "Django checks whether the username and password are correct."),

            ("login()", "Associates the authenticated user with the current request/session.", "After login, Django remembers the user between requests."),

            ("request.user", "The user object associated with the current request.", "A logged-in page can ask Django who is currently using it."),

            ("Session", "Server-side state associated with a browser session.", "The session lets Django remember that the browser has logged in.")

        ],

        "assignment": "Create a login form and authenticate a registered user. Display a dashboard showing request.user.username after successful login.",

        "result": "Correct credentials create an authenticated session. Incorrect credentials return a useful error and do not authenticate the user."

    },

    "logout": {

        "title": "Experiment 3 — User Logout",

        "short_title": "User Logout",

        "aim": "To terminate a user's authenticated session using Django's logout() function.",

        "time": "20–30 minutes",

        "overview": "Require an authenticated user, provide a logout action, call logout(), and verify that the protected page is no longer accessible without logging in again.",

        "prerequisites": ["Experiments 1 and 2 completed", "Basic sessions", "Django decorators"],

        "concepts": [

            ("logout()", "Clears the authenticated user information from the current session.", "It signs the user out."),

            ("@login_required", "A decorator that restricts a view to authenticated users.", "If a user is not logged in, Django sends them to the login page."),

            ("Authorization", "Determines what an authenticated user is allowed to access.", "Knowing who the user is is authentication; deciding what they can access is authorization."),

            ("POST logout action", "Uses a POST request for the state-changing logout operation.", "Clicking the logout button sends a form request instead of changing state through a normal link.")

        ],

        "assignment": "Protect a dashboard with @login_required and implement a POST logout form. Verify that request.user becomes anonymous after logout.",

        "result": "After logout, the authentication session is cleared. A protected dashboard redirects an anonymous user to the login page."

    },

}

 

def home(request):

    return render(request, "register_inout/home.html", {"active": "introduction"})

 

 

def home_section(request, section):

    allowed = {

        "objectives": ("Objectives", "This section explains what students will learn while completing the three Django authentication experiments."),

        "audience": ("Target Audience", "This Virtual Lab is intended for students learning Django, Python web development and authentication concepts."),

        "alignment": ("Course Alignment", "The lab supports Django/Web Development topics including forms, models, authentication, sessions, databases, templates and security."),

    }

    title, text = allowed.get(section, ("Section", "Content not available."))

    return render(request, "register_inout/home_section.html", {

        "active": section,

        "section_title": title,

        "section_text": text,

    })

 

 

def experiments(request):

    return render(request, "register_inout/experiments.html", {

        "active": "experiments",

        "experiments": EXPERIMENTS,

    })

 

 

def experiment(request, slug, section="aim"):

    data = EXPERIMENTS.get(slug)

    if data is None:

        raise Http404("Experiment not found")

    return render(request, "register_inout/experiment.html", {

        "active": section,

        "experiment": data,

        "slug": slug,

        "section": section,

    })

 

 

def register(request):

    if request.method == "POST":

        form = RegistrationForm(request.POST)

        if form.is_valid():

            user = form.save(commit=False)

            user.email = form.cleaned_data["email"]

            full_name = form.cleaned_data["full_name"].strip()

            parts = full_name.split(maxsplit=1)

            user.first_name = parts[0]

            user.last_name = parts[1] if len(parts) == 2 else ""

            user.save()

            return render(request, "register_inout/register.html", {

                "form": RegistrationForm(),

                "success": True,

                "created_username": user.username,

            })

    else:

        form = RegistrationForm()

    return render(request, "register_inout/register.html", {"form": form})

 

 

def login_view(request):

    if request.method == "POST":

        form = LoginForm(request, data=request.POST)

        if form.is_valid():

            user = form.get_user()

            login(request, user)

            return redirect("register_inout:dashboard")

    else:

        form = LoginForm(request)

    return render(request, "register_inout/login.html", {"form": form})

 

 

@login_required

def dashboard(request):

    return render(request, "register_inout/dashboard.html")

 

 

@login_required

def logout_view(request):

    if request.method == "POST":

        logout(request)

        return redirect("register_inout:home")

    return render(request, "register_inout/experiment.html", {

        "active": "real",

        "experiment": EXPERIMENTS["logout"],

        "slug": "logout",

        "section": "real",

    })

 

 

def quiz(request, slug, test_type):
    experiment = EXPERIMENTS.get(slug)

    if experiment is None:
        raise Http404("Experiment not found")

    if test_type not in {"pretest", "posttest"}:
        raise Http404("Test type not found")

    difficulty = (
        request.POST.get("difficulty")
        or request.GET.get("difficulty")
        or "beginner"
    ).lower()

    if difficulty not in {"beginner", "advanced"}:
        difficulty = "beginner"

    questions = QUIZZES[slug][test_type][difficulty]

    if request.method == "POST":
        score = 0
        answers = {}

        for question in questions:
            field_name = f"q{question['id']}"
            selected = request.POST.get(field_name)
            answers[str(question["id"])] = selected

            if selected == question["answer"]:
                score += 1

        QuizAttempt.objects.create(
            user=request.user if request.user.is_authenticated else None,
            experiment=experiment["short_title"],
            test_type=test_type,
            difficulty=difficulty,
            score=score,
            total=len(questions),
            answers=answers,
        )

        result_items = [
            {
                "question": question,
                "selected": answers.get(str(question["id"])),
            }
            for question in questions
        ]

        return render(request, "register_inout/quiz_result.html", {
            "experiment": experiment,
            "slug": slug,
            "test_type": test_type,
            "difficulty": difficulty,
            "result_items": result_items,
            "score": score,
            "total": len(questions),
        })

    return render(request, "register_inout/quiz.html", {
        "experiment": experiment,
        "slug": slug,
        "test_type": test_type,
        "difficulty": difficulty,
        "questions": questions,
    })

def code_assignment(request, slug):
    experiment = EXPERIMENTS.get(slug)

    if experiment is None:
        raise Http404("Experiment not found")

    assessment = None

    if request.method == "POST":
        form = CodeSubmissionForm(request.POST)

        if form.is_valid():
            code_text = form.cleaned_data["code"]

            submission = form.save(commit=False)
            submission.user = request.user if request.user.is_authenticated else None
            submission.experiment = experiment["short_title"]
            submission.save()

            checks = []

            if slug == "registration":
                checks = [
                    ("Uses UserCreationForm", "UserCreationForm" in code_text),
                    ("Uses form validation", "is_valid()" in code_text),
                    ("Uses form saving", ".save(" in code_text),
                    ("Uses CSRF protection", "csrf_token" in code_text),
                ]

            elif slug == "login":
                checks = [
                    ("Uses authenticate()", "authenticate(" in code_text),
                    ("Uses login()", "login(" in code_text),
                    ("Uses request object", "request" in code_text),
                    ("Handles POST data", "POST" in code_text),
                ]

            elif slug == "logout":
                checks = [
                    ("Uses logout()", "logout(" in code_text),
                    ("Uses login_required", "login_required" in code_text),
                    ("Uses POST method", "POST" in code_text),
                    ("Redirects after logout", "redirect(" in code_text),
                ]

            passed = sum(1 for _, ok in checks if ok)
            total = len(checks)

            if passed == total:
                message = "Excellent. All required concepts were detected."
            elif passed >= total / 2:
                message = "Partially correct. Review the failed requirements."
            else:
                message = "Several required concepts are missing. Review the experiment and try again."

            assessment = {
                "score": passed,
                "total": total,
                "items": [
                    {"label": label, "passed": ok}
                    for label, ok in checks
                ],
                "message": message,
            }

    else:
        form = CodeSubmissionForm()

    return render(request, "register_inout/code_assignment.html", {
        "experiment": experiment,
        "slug": slug,
        "form": form,
        "assessment": assessment,
    })

def feedback(request):

    if request.method == "POST":

        form = FeedbackForm(request.POST)

        if form.is_valid():

            feedback_obj = form.save(commit=False)

            feedback_obj.user = request.user if request.user.is_authenticated else None

            feedback_obj.save()

            return render(request, "register_inout/feedback.html", {

                "form": FeedbackForm(),

                "submitted": True,

            })

    else:

        form = FeedbackForm()

    return render(request, "register_inout/feedback.html", {"form": form})