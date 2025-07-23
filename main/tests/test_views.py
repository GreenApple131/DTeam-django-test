import io
from datetime import date

from django.test import TestCase, Client
from django.urls import reverse
from ..models import CV, Skill, Project

from PyPDF2 import PdfReader


class CVListViewTestCase(TestCase):
    """Test cases for CV List View"""

    def setUp(self):
        self.client = Client()
        self.url = reverse("main:cv_list")

        # Create test CVs
        self.cv1 = CV.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            title="Python Developer",
            bio="Experienced Python developer",
            location="New York, NY",
        )

        self.cv2 = CV.objects.create(
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com",
            title="Frontend Developer",
            bio="Creative frontend developer",
            location="San Francisco, CA",
        )

        # Create skills
        self.skill1 = Skill.objects.create(name="Python")
        self.skill2 = Skill.objects.create(name="JavaScript")

        self.cv1.skills.add(self.skill1)
        self.cv2.skills.add(self.skill2)

    def test_cv_list_view_status_code(self):
        """Test that CV list view returns 200 status code"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_cv_list_view_uses_correct_template(self):
        """Test that CV list view uses correct template"""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "main/cv_list.html")

    def test_cv_list_view_context(self):
        """Test CV list view context data"""
        response = self.client.get(self.url)
        self.assertIn("cvs", response.context)
        self.assertEqual(len(response.context["cvs"]), 2)

    def test_cv_list_view_content(self):
        """Test CV list view displays correct content"""
        response = self.client.get(self.url)
        self.assertContains(response, "John Doe")
        self.assertContains(response, "Jane Smith")
        self.assertContains(response, "Python Developer")
        self.assertContains(response, "Frontend Developer")


class CVDetailViewTestCase(TestCase):
    """Test cases for CV Detail View"""

    def setUp(self):
        self.client = Client()

        # Create test CV
        self.cv = CV.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="+1-555-123-4567",
            location="New York, NY",
            title="Python Developer",
            bio="Experienced Python developer",
            experience="Senior Developer at TechCorp",
            education="Computer Science Degree",
            portfolio_url="https://johndoe.dev",
            linkedin_url="https://linkedin.com/in/johndoe",
            github_url="https://github.com/johndoe",
        )

        self.url = reverse("main:cv_detail", kwargs={"pk": self.cv.pk})

    def test_cv_detail_view_status_code(self):
        """Test that CV detail view returns 200 status code"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_cv_detail_view_uses_correct_template(self):
        """Test that CV detail view uses correct template"""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "main/cv_detail.html")

    def test_cv_detail_view_404_for_invalid_pk(self):
        """Test CV detail view returns 404 for invalid primary key"""
        invalid_url = reverse("main:cv_detail", kwargs={"pk": 99999})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)


class CVPDFTestCase(TestCase):
    """Test cases for CV PDF generation"""

    def setUp(self):
        self.client = Client()

        # Create test CV
        self.cv = CV.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="+1-555-123-4567",
            location="New York, NY",
            title="Python Developer",
            bio="Experienced Python developer",
            experience="Senior Developer at TechCorp",
            education="Computer Science Degree",
            portfolio_url="https://johndoe.dev",
            linkedin_url="https://linkedin.com/in/johndoe",
            github_url="https://github.com/johndoe",
        )

        # Create skills
        self.skill1 = Skill.objects.create(name="Python")
        self.skill2 = Skill.objects.create(name="Django")
        self.cv.skills.add(self.skill1, self.skill2)

        # Create project
        self.project = Project.objects.create(
            cv=self.cv,
            title="Test Project",
            description="A test project",
            technologies="Python, Django",
            url="https://github.com/test",
            start_date=date(2023, 1, 1),
            end_date=date(2023, 6, 1),
        )

        self.url = reverse("main:cv_pdf_download", kwargs={"pk": self.cv.pk})

    def test_pdf_download_status_code(self):
        """Test that PDF download returns 200 status code"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_pdf_download_content_type(self):
        """Test that PDF download returns correct content type"""
        response = self.client.get(self.url)
        self.assertEqual(response["Content-Type"], "application/pdf")

    def test_pdf_download_filename(self):
        """Test that PDF download has correct filename"""
        response = self.client.get(self.url)
        expected_filename = f'attachment; filename="{self.cv.full_name}_CV.pdf"'
        self.assertEqual(response["Content-Disposition"], expected_filename)

    def test_pdf_download_content_not_empty(self):
        """Test that PDF download returns non-empty content"""
        response = self.client.get(self.url)
        self.assertTrue(len(response.content) > 0)

    def test_pdf_download_is_valid_pdf(self):
        """Test that downloaded content is a valid PDF"""
        response = self.client.get(self.url)

        # Try to read the PDF content
        try:
            pdf_file = io.BytesIO(response.content)
            pdf_reader = PdfReader(pdf_file)
            # If we can read pages, it's a valid PDF
            self.assertTrue(len(pdf_reader.pages) > 0)
        except Exception as e:
            self.fail(f"Downloaded content is not a valid PDF: {e}")

    def test_pdf_download_404_for_invalid_pk(self):
        """Test PDF download returns 404 for invalid primary key"""
        invalid_url = reverse("main:cv_pdf_download", kwargs={"pk": 99999})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)

    def test_pdf_template_renders(self):
        """Test that PDF template renders without errors"""
        from django.template.loader import render_to_string

        try:
            html_string = render_to_string("main/cv_pdf.html", {"cv": self.cv})
            self.assertIn(self.cv.full_name, html_string)
            self.assertIn(self.cv.title, html_string)
            self.assertIn(self.cv.email, html_string)
        except Exception as e:
            self.fail(f"PDF template failed to render: {e}")
