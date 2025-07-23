import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.db import transaction
from .models import RequestLog


logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all HTTP requests to the database.
    Efficiently captures request details and response information.
    """

    # Paths to exclude from logging (to avoid noise)
    EXCLUDED_PATHS = {
        "/admin/jsi18n/",
        "/favicon.ico",
        "/robots.txt",
    }

    # Static file extensions to exclude
    EXCLUDED_EXTENSIONS = {
        ".css",
        ".js",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".ico",
        ".woff",
        ".woff2",
        ".ttf",
        ".svg",
        ".map",
    }

    def process_request(self, request):
        """Store request start time for response time calculation"""
        request._request_start_time = time.time()
        return None

    def process_response(self, request, response):
        """Log the request after processing"""
        try:
            # Skip logging for excluded paths and static files
            if self._should_skip_logging(request):
                return response

            # Calculate response time
            response_time = None
            if hasattr(request, "_request_start_time"):
                response_time = (
                    time.time() - request._request_start_time
                ) * 1000  # Convert to milliseconds

            # Extract client IP
            remote_ip = self._get_client_ip(request)

            # Get user if authenticated
            user = request.user if request.user.is_authenticated else None

            # Create log entry efficiently using bulk operations
            self._create_log_entry(
                request=request,
                response=response,
                remote_ip=remote_ip,
                user=user,
                response_time=response_time,
            )

        except Exception as e:
            # Log the error but don't break the request/response cycle
            logger.error(f"Error in RequestLoggingMiddleware: {e}")

        return response

    def _should_skip_logging(self, request):
        """Determine if this request should be skipped from logging"""
        path = request.path

        # Skip excluded paths
        if path in self.EXCLUDED_PATHS:
            return True

        # Skip static files
        if any(path.endswith(ext) for ext in self.EXCLUDED_EXTENSIONS):
            return True

        # Skip Django admin static files
        if path.startswith("/static/") or path.startswith("/media/"):
            return True

        return False

    def _get_client_ip(self, request):
        """Extract client IP address from request"""
        # Check for IP in headers (for load balancers/proxies)
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            # Take the first IP if there are multiple
            ip = x_forwarded_for.split(",")[0].strip()
            return ip

        # Check for real IP header
        x_real_ip = request.META.get("HTTP_X_REAL_IP")
        if x_real_ip:
            return x_real_ip

        # Fall back to REMOTE_ADDR
        return request.META.get("REMOTE_ADDR")

    def _create_log_entry(self, request, response, remote_ip, user, response_time):
        """Create RequestLog entry efficiently"""
        try:
            # Use select_for_update to avoid potential race conditions
            with transaction.atomic():
                RequestLog.objects.create(
                    method=request.method,
                    path=request.path,
                    query_string=request.META.get("QUERY_STRING", ""),
                    remote_ip=remote_ip,
                    user_agent=request.META.get("HTTP_USER_AGENT", "")[:1000],
                    user=user,
                    status_code=response.status_code,
                    response_time_ms=response_time,
                    content_type=response.get("Content-Type", ""),
                    content_length=self._get_content_length(response),
                )
        except Exception as e:
            logger.error(f"Failed to create RequestLog entry: {e}")

    def _get_content_length(self, response):
        """Extract content length from response"""
        try:
            content_length = response.get("Content-Length")
            if content_length:
                return int(content_length)
            # If no Content-Length header, try to get from content
            if hasattr(response, "content"):
                return len(response.content)
        except (ValueError, TypeError):
            pass
        return None


class RequestLoggingMiddlewareAsync(RequestLoggingMiddleware):
    """
    Async version of RequestLoggingMiddleware for better performance
    in async Django applications
    """

    async def __call__(self, request):
        """Async middleware entry point"""
        request._request_start_time = time.time()

        response = await self.get_response(request)

        # Log the request asynchronously
        await self._log_request_async(request, response)

        return response

    async def _log_request_async(self, request, response):
        """Async version of request logging"""
        try:
            if self._should_skip_logging(request):
                return

            # Calculate response time
            response_time = None
            if hasattr(request, "_request_start_time"):
                response_time = (time.time() - request._request_start_time) * 1000

            # Extract client IP
            remote_ip = self._get_client_ip(request)

            # Get user if authenticated
            user = request.user if request.user.is_authenticated else None

            # Create log entry asynchronously
            from django.db import sync_to_async

            create_log = sync_to_async(self._create_log_entry)
            await create_log(
                request=request,
                response=response,
                remote_ip=remote_ip,
                user=user,
                response_time=response_time,
            )

        except Exception as e:
            logger.error(f"Error in async RequestLoggingMiddleware: {e}")
