from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from main.models import CV, Skill, Project
from django.test import TestCase


class CVAPITestCase(APITestCase):
    def setUp(self):
        """Set up test data"""
        self.cv_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "+1234567890",
            "location": "New York, NY",
            "title": "Software Developer",
            "bio": "Experienced developer with passion for clean code",
            "experience": "5+ years of software development experience",
            "education": "Bachelor's in Computer Science",
            "portfolio_url": "https://johndoe.dev",
            "linkedin_url": "https://linkedin.com/in/johndoe",
            "github_url": "https://github.com/johndoe",
        }
        self.cv = CV.objects.create(**self.cv_data)
        self.list_create_url = reverse("cv-list-create")
        self.detail_url = reverse("cv-detail", kwargs={"pk": self.cv.pk})

    def test_create_cv_success(self):
        """Test successful CV creation via POST /api/cvs/"""
        new_cv_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "phone": "+0987654321",
            "location": "San Francisco, CA",
            "title": "UX Designer",
            "bio": "Creative designer with eye for detail",
            "experience": "3+ years in UX/UI design",
            "education": "Master's in Design",
        }
        response = self.client.post(self.list_create_url, new_cv_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CV.objects.count(), 2)
        self.assertEqual(response.data["first_name"], new_cv_data["first_name"])
        self.assertEqual(response.data["email"], new_cv_data["email"])

        # Verify CV exists in database
        created_cv = CV.objects.get(email="jane.smith@example.com")
        self.assertEqual(created_cv.first_name, new_cv_data["first_name"])

    def test_create_cv_missing_required_fields(self):
        """Test CV creation with missing required fields"""
        test_cases = [
            {"first_name": "John"},  # Missing required fields
            {"email": "test@example.com"},  # Missing first_name, last_name, etc.
            {"first_name": "Test", "email": "invalid-email"},  # Invalid email
        ]

        for incomplete_data in test_cases:
            response = self.client.post(
                self.list_create_url, incomplete_data, format="json"
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_cv_duplicate_email(self):
        """Test CV creation with duplicate email fails"""
        duplicate_data = {
            "first_name": "Jane",
            "last_name": "Duplicate",
            "email": self.cv_data["email"],  # Same email as existing CV
            "title": "Another Developer",
            "bio": "Different bio",
            "experience": "Different experience",
            "education": "Different education",
        }
        response = self.client.post(self.list_create_url, duplicate_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_list_cvs_success(self):
        """Test successful CV listing via GET /api/cvs/"""
        response = self.client.get(self.list_create_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["first_name"], self.cv_data["first_name"]
        )

    def test_retrieve_cv_success(self):
        """Test successful CV retrieval via GET /api/cvs/{id}/"""
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.cv.pk)
        self.assertEqual(response.data["first_name"], self.cv_data["first_name"])
        self.assertEqual(response.data["last_name"], self.cv_data["last_name"])
        self.assertEqual(response.data["email"], self.cv_data["email"])
        self.assertEqual(response.data["title"], self.cv_data["title"])

    def test_update_cv_full_success(self):
        """Test successful full CV update via PUT /api/cvs/{id}/"""
        updated_data = {
            "first_name": "John",
            "last_name": "Updated",
            "email": "john.updated@example.com",
            "phone": "+9876543210",
            "location": "Los Angeles, CA",
            "title": "Senior Software Developer",
            "bio": "Senior developer with leadership experience",
            "experience": "10+ years of software development",
            "education": "Master's in Computer Science",
            "portfolio_url": "https://johnupdated.dev",
            "linkedin_url": "https://linkedin.com/in/johnupdated",
            "github_url": "https://github.com/johnupdated",
        }
        response = self.client.put(self.detail_url, updated_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["last_name"], updated_data["last_name"])
        self.assertEqual(response.data["title"], updated_data["title"])

        # Verify database update
        self.cv.refresh_from_db()
        self.assertEqual(self.cv.last_name, updated_data["last_name"])
        self.assertEqual(self.cv.title, updated_data["title"])

    def test_partial_update_cv_success(self):
        """Test successful partial CV update via PATCH /api/cvs/{id}/"""
        partial_data = {
            "title": "Lead Software Developer",
            "bio": "Updated professional summary",
        }
        response = self.client.patch(self.detail_url, partial_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], partial_data["title"])
        self.assertEqual(response.data["bio"], partial_data["bio"])
        # Other fields should remain unchanged
        self.assertEqual(response.data["first_name"], self.cv_data["first_name"])
        self.assertEqual(response.data["email"], self.cv_data["email"])

    def test_delete_cv_success(self):
        """Test successful CV deletion via DELETE /api/cvs/{id}/"""
        cv_count_before = CV.objects.count()
        cv_id = self.cv.pk

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CV.objects.count(), cv_count_before - 1)
        self.assertFalse(CV.objects.filter(pk=cv_id).exists())

    def test_api_response_structure(self):
        """Test that API responses have correct structure and fields"""
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "location",
            "title",
            "bio",
            "experience",
            "education",
            "skills",
            "portfolio_url",
            "linkedin_url",
            "github_url",
            "created_at",
            "updated_at",
        ]
        for field in expected_fields:
            with self.subTest(field=field):
                self.assertIn(field, response.data)

    def test_create_cv_with_skills(self):
        """Test creating CV with skills"""
        # Create some skills first
        skill1 = Skill.objects.create(name="Python")
        skill2 = Skill.objects.create(name="Django")

        cv_data_with_skills = {
            "first_name": "Alice",
            "last_name": "Developer",
            "email": "alice@example.com",
            "title": "Python Developer",
            "bio": "Python specialist",
            "experience": "Expert in Python development",
            "education": "CS Degree",
            "skills": [skill1.id, skill2.id],
        }

        response = self.client.post(
            self.list_create_url, cv_data_with_skills, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_cv = CV.objects.get(email="alice@example.com")
        self.assertEqual(created_cv.skills.count(), 2)

    def test_url_field_validation(self):
        """Test URL field validation for portfolio, LinkedIn, and GitHub URLs"""
        invalid_url_data = self.cv_data.copy()
        invalid_url_data["portfolio_url"] = "not-a-valid-url"

        response = self.client.post(
            self.list_create_url, invalid_url_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cv_string_representation(self):
        """Test CV model string representation"""
        expected_str = f"{self.cv.first_name} {self.cv.last_name} - {self.cv.title}"
        self.assertEqual(str(self.cv), expected_str)

    def test_cv_full_name_property(self):
        """Test CV full_name property"""
        expected_full_name = f"{self.cv.first_name} {self.cv.last_name}"
        self.assertEqual(self.cv.full_name, expected_full_name)

    def test_list_pagination_with_ordering(self):
        """Test CV list pagination with proper ordering"""
        # Create additional CVs
        for i in range(5):
            CV.objects.create(
                first_name=f"User{i}",
                last_name=f"Test{i}",
                email=f"user{i}@example.com",
                title=f"Developer {i}",
                bio=f"Bio for user {i}",
                experience=f"Experience {i}",
                education=f"Education {i}",
            )

        response = self.client.get(self.list_create_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that results are ordered by updated_at (most recent first)
        results = response.data["results"]
        if len(results) > 1:
            for i in range(len(results) - 1):
                first_updated = results[i]["updated_at"]
                second_updated = results[i + 1]["updated_at"]
                self.assertGreaterEqual(first_updated, second_updated)

    def test_retrieve_nonexistent_cv(self):
        """Test retrieving non-existent CV returns 404"""
        nonexistent_url = reverse("cv-detail", kwargs={"pk": 99999})
        response = self.client.get(nonexistent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_nonexistent_cv(self):
        """Test deleting non-existent CV returns 404"""
        nonexistent_url = reverse("cv-detail", kwargs={"pk": 99999})
        response = self.client.delete(nonexistent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
