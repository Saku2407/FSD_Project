from django.urls import path
from . import views

app_name = "register_inout"

urlpatterns = [
    # Home pages
    path("", views.home, name="home"),
    path("objectives/", views.home_section,
         {"section": "objectives"}, name="objectives"),
    path("audience/", views.home_section,
         {"section": "audience"}, name="audience"),
    path("alignment/", views.home_section,
         {"section": "alignment"}, name="alignment"),
    path("experiments/", views.experiments, name="experiments"),

    # Authentication
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.logout_view, name="logout"),

    # IMPORTANT:
    # Specific experiment actions MUST come BEFORE the generic
    # <str:section> route.
    path("experiments/<slug:slug>/pretest/",
         views.quiz,
         {"test_type": "pretest"},
         name="pretest"),

    path("experiments/<slug:slug>/posttest/",
         views.quiz,
         {"test_type": "posttest"},
         name="posttest"),

    path("experiments/<slug:slug>/assignment/",
         views.code_assignment,
         name="assignment"),

    # Generic experiment sections come AFTER specific routes.
    path("experiments/<slug:slug>/",
         views.experiment,
         name="experiment"),

    path("experiments/<slug:slug>/<str:section>/",
         views.experiment,
         name="experiment_section"),

    # Feedback
    path("feedback/", views.feedback, name="feedback"),
]