from django.contrib.staticfiles import finders
from django.http import Http404
from django.shortcuts import redirect, render
from django.templatetags.static import static
from django.urls import reverse
from .forms import FeedbackForm

from .content import (DEPARTMENT, EXPERIMENTS, LAB_TITLE, QUIZZES,
                      get_experiment, sections_for)


def _main_sidebar(active):
    """Sidebar of the lab's own pages. `active` is a url name."""
    items = [
        ("lab:introduction", "Introduction"),
        ("lab:objective", "Objective"),
        ("lab:experiments", "List of experiments"),
        ("lab:audience", "Target Audience"),
        ("lab:alignment", "Course Alignment"),
        ("lab:feedback", "Feedback"),
    ]
    return [
        {"url": reverse(name), "label": label, "active": name == active}
        for name, label in items
    ]


def _ctx(request, sidebar, **extra):
    ctx = {
        "lab_title": LAB_TITLE,
        "department": DEPARTMENT,
        "sidebar": sidebar,
    }
    ctx.update(extra)
    return ctx


def _page(request, template, active, **extra):
    return render(request, template,
                  _ctx(request, _main_sidebar(active), **extra))


def introduction(request):
    return _page(request, "lab/introduction.html", "lab:introduction")


def objective(request):
    return _page(request, "lab/objective.html", "lab:objective")


def experiments(request):
    return _page(request, "lab/experiments.html", "lab:experiments",
                 experiments=EXPERIMENTS)


def audience(request):
    return _page(request, "lab/audience.html", "lab:audience")


def alignment(request):
    return _page(request, "lab/alignment.html", "lab:alignment")


def feedback(request):
    submitted = request.method == "POST"
    return _page(request, "lab/feedback.html", "lab:feedback",
                 submitted=submitted)


def experiment_root(request, num):
    if get_experiment(num) is None:
        raise Http404("No such experiment")
    return redirect("lab:experiment", num=num, section="aim")


def experiment(request, num, section):
    exp = get_experiment(num)
    if exp is None:
        raise Http404("No such experiment page")
    sections = sections_for(exp)
    keys = [k for k, _ in sections]
    if section not in keys:
        raise Http404("No such experiment page")

    idx = keys.index(section)
    sidebar = [{"url": reverse("lab:experiments"),
                "label": "← All experiments", "active": False,
                "back": True}]
    sidebar += [
        {"url": reverse("lab:experiment", args=[num, key]),
         "label": label, "active": key == section}
        for key, label in sections
    ]

    prev_url = prev_label = next_url = next_label = None
    if idx > 0:
        prev_url = reverse("lab:experiment", args=[num, keys[idx - 1]])
        prev_label = sections[idx - 1][1]
    if idx < len(keys) - 1:
        next_url = reverse("lab:experiment", args=[num, keys[idx + 1]])
        next_label = sections[idx + 1][1]
    elif get_experiment(num + 1):
        next_url = reverse("lab:experiment", args=[num + 1, "aim"])
        next_label = "Experiment %d" % (num + 1)

    video_url = None
    if section == "video" and exp.get("video"):
        path = "lab/videos/" + exp["video"]
        if finders.find(path):          # None if the file has not been added
            video_url = static(path)

    return render(request, "model_migrations/introduction.html", _ctx(
        request, sidebar,
        exp=exp,
        section=section,
        section_label=sections[idx][1],
        video_url=video_url,
        sidebar_heading="Experiment %d" % num,
        # theory / procedure / simulation each have their own template
        section_template="lab/exp/e%d_%s.html" % (num, section),
        quiz_data=QUIZZES.get(num, []),
        prev_url=prev_url, prev_label=prev_label,
        next_url=next_url, next_label=next_label,
    ))


def home(request):
    return render(request, "model_migrations/simple.html", _ctx(
        request, _main_sidebar(""), page_title="Home",
        body="Welcome to the virtual lab on Creating Django Models and "
             "Migrations. Use the menu on the left to begin, or jump "
             "straight to the List of experiments."))


def partners(request):
    return render(request, "model_migrations/simple.html", _ctx(
        request, _main_sidebar(""), page_title="Partners",
        body="This lab is part of a Virtual Labs style initiative "
             "supported by partner institutions."))


def contact(request):
    return render(request, "model_migrations/simple.html", _ctx(
        request, _main_sidebar(""), page_title="Contact",
        body="Phone: General Information: 011-26582050 | "
             "Email: support@vlabs.somaiya.edu"))
    
def feedback(request):
    form = FeedbackForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect(reverse("lab:feedback") + "?thanks=1")
    return _page(request, "lab/feedback.html", "lab:feedback",
                 form=form, submitted=request.GET.get("thanks") == "1")
