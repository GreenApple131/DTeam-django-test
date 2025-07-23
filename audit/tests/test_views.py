from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from audit.models import RequestLog
from audit.middleware import RequestLoggingMiddleware
import time


class RequestLoggingMiddlewareTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

    def test_middleware_logs_get_request(self):
        """Test that GET requests are logged"""
        initial_count = RequestLog.objects.count()

        response = self.client.get("/")

        self.assertEqual(RequestLog.objects.count(), initial_count + 1)

        log_entry = RequestLog.objects.latest("timestamp")
        self.assertEqual(log_entry.method, "GET")
        self.assertEqual(log_entry.path, "/")
        self.assertIsNotNone(log_entry.timestamp)
        self.assertIsNotNone(log_entry.status_code)

    def test_middleware_logs_post_request(self):
        """Test that POST requests are logged"""
        initial_count = RequestLog.objects.count()

        response = self.client.post("/", {"test": "data"})

        self.assertEqual(RequestLog.objects.count(), initial_count + 1)

        log_entry = RequestLog.objects.latest("timestamp")
        self.assertEqual(log_entry.method, "POST")
        self.assertEqual(log_entry.path, "/")

    def test_middleware_logs_authenticated_user(self):
        """Test that authenticated user is logged"""
        self.client.login(username="testuser", password="testpass123")

        response = self.client.get("/")

        log_entry = RequestLog.objects.latest("timestamp")
        self.assertEqual(log_entry.user, self.user)

    def test_middleware_logs_anonymous_user(self):
        """Test that anonymous requests are logged without user"""
        response = self.client.get("/")

        log_entry = RequestLog.objects.latest("timestamp")
        self.assertIsNone(log_entry.user)

    def test_middleware_logs_query_string(self):
        """Test that query strings are logged"""
        response = self.client.get("/?search=test&page=1")

        log_entry = RequestLog.objects.latest("timestamp")
        self.assertEqual(log_entry.query_string, "search=test&page=1")

    def test_middleware_logs_response_time(self):
        """Test that response time is logged"""
        response = self.client.get("/")

        log_entry = RequestLog.objects.latest("timestamp")
        self.assertIsNotNone(log_entry.response_time_ms)
        self.assertGreater(log_entry.response_time_ms, 0)

    def test_middleware_skips_static_files(self):
        """Test that static files are not logged"""
        initial_count = RequestLog.objects.count()

        # These should be skipped
        static_paths = [
            "/static/css/style.css",
            "/static/js/script.js",
            "/favicon.ico",
            "/media/image.png",
        ]

        for path in static_paths:
            response = self.client.get(path)

        # Count should remain the same
        self.assertEqual(RequestLog.objects.count(), initial_count)

    def test_middleware_logs_status_codes(self):
        """Test that different status codes are logged correctly"""
        # Test 404
        response = self.client.get("/nonexistent-page/")
        log_entry = RequestLog.objects.latest("timestamp")
        self.assertEqual(log_entry.status_code, 404)


class RecentRequestsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("audit:recent_requests")

        # Create test request logs
        for i in range(15):
            RequestLog.objects.create(
                method="GET",
                path=f"/test-path-{i}/",
                status_code=200,
                response_time_ms=50.0 + i,
            )

    def test_recent_requests_view_shows_10_requests(self):
        """Test that view shows only 10 most recent requests"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("requests", response.context)
        self.assertEqual(len(response.context["requests"]), 10)

    def test_recent_requests_view_orders_by_timestamp_desc(self):
        """Test that requests are ordered by timestamp descending"""
        response = self.client.get(self.url)

        requests = response.context["requests"]
        timestamps = [req.timestamp for req in requests]

        # Check that timestamps are in descending order
        self.assertEqual(timestamps, sorted(timestamps, reverse=True))

    def test_recent_requests_view_shows_total_count(self):
        """Test that view shows total request count"""
        response = self.client.get(self.url)

        self.assertIn("total_requests", response.context)
        self.assertEqual(response.context["total_requests"], 15)

    def test_recent_requests_view_renders_template(self):
        """Test that view renders correct template"""
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, "audit/recent_requests.html")

    def test_recent_requests_view_with_no_logs(self):
        """Test view behavior when no logs exist"""
        RequestLog.objects.all().delete()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["requests"]), 0)
        self.assertEqual(response.context["total_requests"], 0)

    def test_recent_requests_view_displays_user_info(self):
        """Test that view displays user information correctly"""
        user = User.objects.create_user(username="testuser", password="testpass")

        RequestLog.objects.create(
            method="POST",
            path="/api/test/",
            status_code=201,
            user=user,
            remote_ip="127.0.0.1",
            response_time_ms=25.5,
        )

        response = self.client.get(self.url)
        self.assertContains(response, "testuser")

    def test_recent_requests_view_handles_long_paths(self):
        """Test that view handles long paths gracefully"""
        long_path = "/very-long-path-" + "x" * 200 + "/"
        RequestLog.objects.create(method="GET", path=long_path, status_code=200)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class RequestLogModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser")

    def test_request_log_string_representation(self):
        """Test RequestLog __str__ method"""
        log = RequestLog.objects.create(method="GET", path="/test/", user=self.user)

        expected = (
            f"GET /test/ - {log.timestamp.strftime('%Y-%m-%d %H:%M:%S')} (testuser)"
        )
        self.assertEqual(str(log), expected)

    def test_request_log_string_representation_anonymous(self):
        """Test RequestLog __str__ method for anonymous user"""
        log = RequestLog.objects.create(method="POST", path="/api/test/")

        expected = f"POST /api/test/ - {log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        self.assertEqual(str(log), expected)

    def test_is_api_request_property(self):
        """Test is_api_request property"""
        api_log = RequestLog.objects.create(method="GET", path="/api/cvs/")
        regular_log = RequestLog.objects.create(method="GET", path="/admin/")

        self.assertTrue(api_log.is_api_request)
        self.assertFalse(regular_log.is_api_request)

    def test_is_successful_property(self):
        """Test is_successful property"""
        success_log = RequestLog.objects.create(method="GET", path="/", status_code=200)
        error_log = RequestLog.objects.create(method="GET", path="/", status_code=404)
        redirect_log = RequestLog.objects.create(
            method="GET", path="/", status_code=302
        )

        self.assertTrue(success_log.is_successful)
        self.assertFalse(error_log.is_successful)
        self.assertFalse(redirect_log.is_successful)


class MiddlewareIntegrationTest(TestCase):
    def test_middleware_integration_with_views(self):
        """Test that middleware works correctly with actual views"""
        initial_count = RequestLog.objects.count()

        # Make request to logs view (which should also be logged)
        url = reverse("audit:recent_requests")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(RequestLog.objects.count(), initial_count + 1)

        # The request to logs view should be logged
        log_entry = RequestLog.objects.latest("timestamp")
        self.assertEqual(log_entry.path, url)
        self.assertEqual(log_entry.method, "GET")
        self.assertEqual(log_entry.status_code, 200)
