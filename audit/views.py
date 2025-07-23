from django.shortcuts import render
from django.views.generic import ListView
from .models import RequestLog


class RecentRequestsView(ListView):
    """Display the 10 most recent logged requests"""

    model = RequestLog
    template_name = "audit/recent_requests.html"
    context_object_name = "requests"
    queryset = RequestLog.objects.select_related("user").order_by("-timestamp")[:10]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_requests"] = RequestLog.objects.count()
        return context
