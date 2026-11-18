from django.http import Http404
from django.shortcuts import render

from .data import LABS


def home(request):
    context = {
        "labs": LABS,
        "visitors": 55680839,
    }
    return render(request, "labs/home.html", context)


def lab_detail(request, slug):
    lab = next((item for item in LABS if item["slug"] == slug), None)
    if lab is None:
        raise Http404("Lab not found")
    return render(request, "labs/lab_detail.html", {"lab": lab})


def about(request):
    return render(request, "labs/about.html")


def contact(request):
    return render(request, "labs/contact.html")
