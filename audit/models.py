from django.db import models
from django.contrib.auth.models import User


class AuditLog(models.Model):
    """Model to store audit logs."""

    id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    level = models.CharField(max_length=10)
    message = models.TextField()

    class Meta:
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.timestamp} - {self.level} - {self.message}"


class RequestLog(models.Model):
    """Model to log HTTP requests for auditing purposes"""

    # Request details
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    method = models.CharField(max_length=10, db_index=True)
    path = models.CharField(max_length=500, db_index=True)
    query_string = models.TextField(blank=True)

    # Client information
    remote_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    # User information (if authenticated)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="request_logs",
    )

    # Response information
    status_code = models.IntegerField(null=True, blank=True)
    response_time_ms = models.FloatField(
        null=True, blank=True, help_text="Response time in milliseconds"
    )

    # Additional metadata
    content_type = models.CharField(max_length=100, blank=True)
    content_length = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Request Log"
        verbose_name_plural = "Request Logs"
        indexes = [
            models.Index(fields=["timestamp", "method"]),
            models.Index(fields=["path", "timestamp"]),
            models.Index(fields=["user", "timestamp"]),
        ]

    def __str__(self):
        user_info = f" ({self.user.username})" if self.user else ""
        return f"{self.method} {self.path} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}{user_info}"

    @property
    def is_api_request(self):
        """Check if this is an API request"""
        return self.path.startswith("/api/")

    @property
    def is_successful(self):
        """Check if the request was successful (2xx status code)"""
        return self.status_code and 200 <= self.status_code < 300
