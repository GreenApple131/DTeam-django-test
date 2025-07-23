from django.contrib import admin
from .models import RequestLog


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = [
        "timestamp",
        "method",
        "path",
        "status_code",
        "user",
        "remote_ip",
        "response_time_ms",
        "is_api_request",
    ]
    list_filter = ["method", "status_code", "timestamp", "user"]
    search_fields = ["path", "remote_ip", "user__username", "user_agent"]
    readonly_fields = [
        "timestamp",
        "method",
        "path",
        "query_string",
        "remote_ip",
        "user_agent",
        "user",
        "status_code",
        "response_time_ms",
        "content_type",
        "content_length",
    ]
    date_hierarchy = "timestamp"
    ordering = ["-timestamp"]

    def has_add_permission(self, request):
        """Disable manual addition of request logs"""
        return False

    def has_change_permission(self, request, obj=None):
        """Make request logs read-only"""
        return False

    def is_api_request(self, obj):
        """Display if request is an API request"""
        return obj.is_api_request

    is_api_request.boolean = True
    is_api_request.short_description = "API Request"

    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related("user")
