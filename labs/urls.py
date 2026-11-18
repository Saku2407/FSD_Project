from django.urls import path

from . import views

app_name = "labs"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("lab/<slug:slug>/", views.lab_detail, name="lab_detail"),
]
