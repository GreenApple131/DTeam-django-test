import os
import tempfile
import json

from weasyprint import HTML
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from main.models import CV
from .tasks import send_cv_pdf_email
from .services import TranslationService
from .tasks import translate_cv_content_task


class CVListView(ListView):
    model = CV
    template_name = "main/cv_list.html"
    context_object_name = "cvs"
    paginate_by = 10

    def get_queryset(self):
        return CV.objects.prefetch_related("skills", "project_set").order_by(
            "-updated_at"
        )


class CVDetailView(DetailView):
    model = CV
    template_name = "main/cv_detail.html"
    context_object_name = "cv"

    def get_queryset(self):
        return CV.objects.prefetch_related("skills", "project_set")


def cv_pdf_download(request, pk):
    """Generate and download CV as PDF"""
    cv = get_object_or_404(CV.objects.prefetch_related("skills", "project_set"), pk=pk)

    # Render the PDF template
    html_string = render_to_string("main/pdf/cv.html", {"cv": cv})

    # Create PDF
    html = HTML(string=html_string)

    # Generate PDF in memory
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        html.write_pdf(tmp_file.name)

        # Read the PDF content
        with open(tmp_file.name, "rb") as pdf_file:
            pdf_content = pdf_file.read()

        # Clean up temporary file
        os.unlink(tmp_file.name)

    # Create HTTP response
    response = HttpResponse(pdf_content, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{cv.full_name}_CV.pdf"'

    return response


# Function-based view alternative
def cv_list(request):
    cvs = CV.objects.prefetch_related("skills", "project_set").order_by("-updated_at")
    return render(request, "main/cv_list.html", {"cvs": cvs})


def cv_detail(request, pk):
    cv = get_object_or_404(CV, pk=pk)
    return render(request, "main/cv_detail.html", {"cv": cv})


def settings_view(request):
    """
    Display Django settings page.
    Available to all users in DEBUG mode, staff only in production.
    """
    if not settings.DEBUG and not request.user.is_staff:
        from django.http import HttpResponseForbidden

        return HttpResponseForbidden("Access denied. Staff privileges required.")

    # Get settings from context processor
    context = {
        "page_title": "Django Settings",
        "debug_mode": settings.DEBUG,
    }

    return render(request, "main/settings.html", context)


@staff_member_required
def detailed_settings_view(request):
    """
    Display detailed Django settings (staff only).
    """
    # Get settings that are safe to display
    safe_settings = {}
    excluded_settings = {
        "SECRET_KEY",
        "DATABASES",
        "PASSWORD_HASHERS",
        "AUTH_PASSWORD_VALIDATORS",
        "EMAIL_HOST_PASSWORD",
    }

    for setting_name in dir(settings):
        if (
            not setting_name.startswith("_")
            and setting_name not in excluded_settings
            and setting_name.isupper()
        ):
            try:
                setting_value = getattr(settings, setting_name)
                # Convert complex objects to JSON-serializable format
                if isinstance(setting_value, (dict, list, tuple)):
                    safe_settings[setting_name] = setting_value
                else:
                    safe_settings[setting_name] = str(setting_value)
            except Exception:
                safe_settings[setting_name] = "Unable to display"

    context = {
        "page_title": "Detailed Django Settings",
        "settings_dict": safe_settings,
        "debug_mode": settings.DEBUG,
    }

    return render(request, "main/detailed_settings.html", context)


@require_POST
def send_cv_email(request, cv_id):
    """
    Trigger Celery task to send CV PDF via email
    """
    try:
        data = json.loads(request.body)
        recipient_email = data.get("email")

        if not recipient_email:
            return JsonResponse({"error": "Email is required"}, status=400)

        # Get CV to validate it exists
        cv = CV.objects.get(id=cv_id)

        # Trigger Celery task
        task = send_cv_pdf_email.delay(cv_id, recipient_email)

        return JsonResponse({"message": "Email is being sent", "task_id": task.id})

    except CV.DoesNotExist:
        return JsonResponse({"error": "CV not found"}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_POST
def translate_cv(request, cv_id):
    """
    Trigger CV translation via OpenAI
    """
    try:
        data = json.loads(request.body)
        target_language = data.get("language")

        if not target_language:
            return JsonResponse({"error": "Language is required"}, status=400)

        # Validate language
        supported_languages = TranslationService.get_supported_languages()
        if target_language not in supported_languages:
            return JsonResponse({"error": "Unsupported language"}, status=400)

        # Get CV to validate it exists
        cv = CV.objects.get(id=cv_id)

        # Trigger translation task
        task = translate_cv_content_task.delay(cv_id, target_language)

        return JsonResponse(
            {
                "message": "Translation is being processed",
                "task_id": task.id,
                "target_language": supported_languages[target_language],
            }
        )

    except CV.DoesNotExist:
        return JsonResponse({"error": "CV not found"}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def get_translation_result(request, task_id):
    """
    Get translation task result
    """
    from celery.result import AsyncResult

    try:
        result = AsyncResult(task_id)

        if result.ready():
            if result.successful():
                return JsonResponse({"status": "completed", "result": result.get()})
            else:
                return JsonResponse({"status": "failed", "error": str(result.info)})
        else:
            return JsonResponse({"status": "pending"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
