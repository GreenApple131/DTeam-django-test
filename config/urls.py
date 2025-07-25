from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("main.urls")),
    path("api/v1/", include("main.api.urls")),
    path("", include("audit.urls")),
]
