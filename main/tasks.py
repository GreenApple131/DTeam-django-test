from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from .models import CV
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import io
import logging
from .services import TranslationService

logger = logging.getLogger(__name__)


@shared_task
def send_cv_pdf_email(cv_id, recipient_email):
    """
    Generate CV PDF and send it via email
    """
    try:
        # Get CV object
        cv = CV.objects.get(id=cv_id)

        # Generate PDF
        pdf_buffer = generate_cv_pdf(cv)

        # Create email
        subject = f"CV for {cv.full_name}"
        message = render_to_string(
            "main/email_cv_template.txt", {"cv": cv, "recipient_email": recipient_email}
        )

        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
        )

        # Attach PDF
        email.attach(f"{cv.full_name}_CV.pdf", pdf_buffer.getvalue(), "application/pdf")

        # Send email
        email.send()

        logger.info(f"CV PDF sent successfully to {recipient_email} for CV ID: {cv_id}")
        return f"Email sent successfully to {recipient_email}"

    except CV.DoesNotExist:
        logger.error(f"CV with ID {cv_id} not found")
        return f"CV with ID {cv_id} not found"
    except Exception as e:
        logger.error(f"Error sending CV PDF: {str(e)}")
        return f"Error sending email: {str(e)}"


def generate_cv_pdf(cv):
    """
    Generate PDF from CV data
    """
    buffer = io.BytesIO()

    # Create the PDF object
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title = Paragraph(f"<b>{cv.full_name}</b>", styles["Title"])
    story.append(title)
    story.append(Spacer(1, 12))

    # Professional Title
    if cv.title:
        prof_title = Paragraph(f"<b>{cv.title}</b>", styles["Heading2"])
        story.append(prof_title)
        story.append(Spacer(1, 12))

    # Contact Information
    contact_info = f"""
    <b>Email:</b> {cv.email}<br/>
    <b>Phone:</b> {cv.phone or 'Not provided'}<br/>
    <b>Location:</b> {cv.location or 'Not provided'}
    """
    contact_para = Paragraph(contact_info, styles["Normal"])
    story.append(contact_para)
    story.append(Spacer(1, 12))

    # Professional Summary
    if cv.bio:
        bio_title = Paragraph("<b>Professional Summary</b>", styles["Heading3"])
        story.append(bio_title)
        bio_para = Paragraph(cv.bio, styles["Normal"])
        story.append(bio_para)
        story.append(Spacer(1, 12))

    # Experience
    if cv.experience:
        exp_title = Paragraph("<b>Work Experience</b>", styles["Heading3"])
        story.append(exp_title)
        exp_para = Paragraph(cv.experience, styles["Normal"])
        story.append(exp_para)
        story.append(Spacer(1, 12))

    # Education
    if cv.education:
        edu_title = Paragraph("<b>Education</b>", styles["Heading3"])
        story.append(edu_title)
        edu_para = Paragraph(cv.education, styles["Normal"])
        story.append(edu_para)
        story.append(Spacer(1, 12))

    # Skills
    if cv.skills.exists():
        skills_title = Paragraph("<b>Skills</b>", styles["Heading3"])
        story.append(skills_title)
        skills_list = ", ".join([skill.name for skill in cv.skills.all()])
        skills_para = Paragraph(skills_list, styles["Normal"])
        story.append(skills_para)
        story.append(Spacer(1, 12))

    # URLs
    urls = []
    if cv.portfolio_url:
        urls.append(f"Portfolio: {cv.portfolio_url}")
    if cv.linkedin_url:
        urls.append(f"LinkedIn: {cv.linkedin_url}")
    if cv.github_url:
        urls.append(f"GitHub: {cv.github_url}")

    if urls:
        urls_title = Paragraph("<b>Links</b>", styles["Heading3"])
        story.append(urls_title)
        urls_para = Paragraph("<br/>".join(urls), styles["Normal"])
        story.append(urls_para)

    # Build PDF
    doc.build(story)
    buffer.seek(0)

    return buffer


@shared_task
def translate_cv_content_task(cv_id, target_language):
    """
    Translate CV content asynchronously
    """
    try:
        cv = CV.objects.get(id=cv_id)
        translation_service = TranslationService()

        result = translation_service.translate_cv_content(cv, target_language)

        logger.info(f"Translation completed for CV ID: {cv_id} to {target_language}")
        return result

    except CV.DoesNotExist:
        logger.error(f"CV with ID {cv_id} not found")
        return {"success": False, "error": f"CV with ID {cv_id} not found"}
    except Exception as e:
        logger.error(f"Error translating CV: {str(e)}")
        return {"success": False, "error": str(e)}
