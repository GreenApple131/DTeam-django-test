from django.urls import path
from .views import RecentRequestsView

app_name = "audit"

urlpatterns = [
    path("logs/", RecentRequestsView.as_view(), name="recent_requests"),
]
