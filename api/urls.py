from django.urls import path
from .views import CVListCreateAPIView, CVRetrieveUpdateDestroyAPIView

# API URLs
urlpatterns = [
    path("cvs/", CVListCreateAPIView.as_view(), name="cv-list-create"),
    path("cvs/<int:pk>/", CVRetrieveUpdateDestroyAPIView.as_view(), name="cv-detail"),
]
