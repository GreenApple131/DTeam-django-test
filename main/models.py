from django.db import models
from django.core.validators import URLValidator
from django.urls import reverse


class CV(models.Model):
    # Personal Information
    first_name = models.CharField(max_length=100, verbose_name="First Name")
    last_name = models.CharField(max_length=100, verbose_name="Last Name")
    email = models.EmailField(verbose_name="Email Address", unique=True)
    phone = models.CharField(max_length=20, blank=True, verbose_name="Phone Number")
    location = models.CharField(max_length=200, blank=True, verbose_name="Location")

    # Professional Information
    title = models.CharField(max_length=200, verbose_name="Professional Title")
    bio = models.TextField(verbose_name="Professional Summary")

    # Experience and Skills
    experience = models.TextField(
        verbose_name="Work Experience", help_text="Describe your work experience"
    )
    education = models.TextField(
        verbose_name="Education", help_text="Your educational background"
    )
    skills = models.ManyToManyField(
        "Skill", blank=True, related_name="cv_skills", verbose_name="Skills"
    )

    # Links and Portfolio
    portfolio_url = models.URLField(blank=True, verbose_name="Portfolio URL")
    linkedin_url = models.URLField(blank=True, verbose_name="LinkedIn URL")
    github_url = models.URLField(blank=True, verbose_name="GitHub URL")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "CV"
        verbose_name_plural = "CVs"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.title}"

    def get_absolute_url(self):
        return reverse("cv_detail", kwargs={"pk": self.pk})

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Skill(models.Model):
    """Separate model for skills to allow for better organization"""

    name = models.CharField(unique=True, max_length=100, verbose_name="Skill Name")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}"


class Project(models.Model):
    """Separate model for projects to allow for better organization"""

    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name="project_set")
    title = models.CharField(max_length=200, verbose_name="Project Title")
    description = models.TextField(verbose_name="Project Description")
    technologies = models.CharField(max_length=300, verbose_name="Technologies Used")
    url = models.URLField(blank=True, verbose_name="Project URL")
    start_date = models.DateField(blank=True, null=True, verbose_name="Start Date")
    end_date = models.DateField(blank=True, null=True, verbose_name="End Date")

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return self.title
