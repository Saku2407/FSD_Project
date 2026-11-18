from django.urls import path
from . import views

app_name = 'git_repo_manage'
urlpatterns = [
    path('', views.home, name='home'),
    path('aim/', views.aim, name='aim'),
    path('overview/', views.overview, name='overview'),
    path('procedure/', views.procedure, name='procedure'),
    path('pretest/', views.pretest, name='pretest'),
    path('simulation/', views.simulation, name='simulation'),
    path('observations/', views.observations, name='observations'),
    path('analysis/', views.analysis, name='analysis'),
    path('posttest/', views.posttest, name='posttest'),
    path('references/', views.references, name='references'),
    path('feedback/', views.feedback, name='feedback'),
]
