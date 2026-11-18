from django.urls import path
from . import views

app_name = 'views_template'
urlpatterns = [
    path('', views.home, name='home'),
    path('aim/', views.aim, name='aim'),
    path('overview/', views.overview, name='overview'),
    path('views/', views.views_page, name='views_page'),
    path('pretest/', views.pretest, name='pretest'),
    path('procedure/', views.procedure, name='procedure'),
    path('simulation/', views.simulation, name='simulation'),
    path('template-tags/', views.template_tags, name='template_tags'),
    path('template-filters/', views.template_filters, name='template_filters'),
    path('models-data/', views.models_data, name='models_data'),
    path('get-post/', views.get_post, name='get_post'),
    path('analysis/', views.analysis, name='analysis'),
    path('observations/', views.observations, name='observations'),
    path('posttest/', views.posttest, name='posttest'),
    path('references/', views.references, name='references'),
    path('feedback/', views.feedback, name='feedback'),
]
