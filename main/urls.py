from django.urls import path
from . import views
from .views import settings_view, detailed_settings_view, send_cv_email

app_name = "main"

urlpatterns = [
    path("", views.CVListView.as_view(), name="cv_list"),
    path("cv/<int:pk>/", views.CVDetailView.as_view(), name="cv_detail"),
    path("cv/<int:pk>/pdf/", views.cv_pdf_download, name="cv_pdf_download"),
    path("settings/", settings_view, name="settings"),
    path("settings/detailed/", detailed_settings_view, name="detailed_settings"),
    path("cv/<int:cv_id>/send-email/", send_cv_email, name="send_cv_email"),
]
