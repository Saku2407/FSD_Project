from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("labs.urls")),
    path("permissions/", include("permission_groups.urls")),
    path("models/", include("model_migrations.urls")),
    path("data/", include("views_template.urls")),
    path("accounts/", include("register_inout.urls"))
    
]
