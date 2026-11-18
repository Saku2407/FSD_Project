from django.urls import path

from . import views

app_name = "model_migrations"

urlpatterns = [
    path("", views.introduction, name="introduction"),
    path("objective/", views.objective, name="objective"),
    path("experiments/", views.experiments, name="experiments"),
    path("experiments/<int:num>/", views.experiment_root,
         name="experiment_root"),
    path("experiments/<int:num>/<slug:section>/", views.experiment,
         name="experiment"),
    path("target-audience/", views.audience, name="audience"),
    path("course-alignment/", views.alignment, name="alignment"),
    path("feedback/", views.feedback, name="feedback"),
    path("home/", views.home, name="home"),
    path("partners/", views.partners, name="partners"),
    path("contact/", views.contact, name="contact"),
]
