from django.urls import path
from . import views

app_name = "lab"
urlpatterns = [
    path("", views.introduction, name="introduction"),
    path("objective/", views.objective, name="objective"),
    path("experiments/", views.experiments, name="experiments"),
    path("experiments/<slug:slug>/", views.experiment_detail, name="experiment_detail"),
    path("experiments/<slug:slug>/<slug:section>/", views.experiment_section, name="experiment_section"),
    path("target-audience/", views.audience, name="audience"),
    path("course-alignment/", views.alignment, name="alignment"),
    path("feedback/", views.feedback, name="feedback"),
    path("home/", views.home, name="home"),
    path("partners/", views.partners, name="partners"),
    path("contact/", views.contact, name="contact"),
]
