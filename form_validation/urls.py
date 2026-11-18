from django.urls import path

from . import views

app_name = "form_validation"

urlpatterns = [
    path("", views.introduction, name="home"),
    path("introduction/", views.introduction, name="introduction"),
    path("objective/", views.objective, name="objective"),
    path("theory/", views.theory, name="theory"),
    path("experiment/", views.experiment, name="experiment"),
    path("assessment/", views.assessment, name="assessment"),
    path("feedback/", views.feedback, name="feedback"),
]