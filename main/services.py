import openai
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class TranslationService:
    """Service for translating CV content using OpenAI"""

    # Supported languages with their native names
    SUPPORTED_LANGUAGES = {
        "cornish": "Cornish (Kernewek)",
        "manx": "Manx (Gaelg)",
        "breton": "Breton (Brezhoneg)",
        "inuktitut": "Inuktitut (ᐃᓄᒃᑎᑐᑦ)",
        "kalaallisut": "Kalaallisut (Greenlandic)",
        "romani": "Romani (Rromani ćhib)",
        "occitan": "Occitan (Occità)",
        "ladino": "Ladino (Judeo-Spanish)",
        "northern_sami": "Northern Sami (Davvisámegiella)",
        "upper_sorbian": "Upper Sorbian (Hornjoserbšćina)",
        "kashubian": "Kashubian (Kaszëbsczi jãzëk)",
        "zazaki": "Zazaki (Kirmanjki)",
        "chuvash": "Chuvash (Чӑваш чӗлхи)",
        "livonian": "Livonian (Līvõ kēļ)",
        "tsakonian": "Tsakonian (Τσακώνικα)",
        "saramaccan": "Saramaccan",
        "bislama": "Bislama",
    }

    def __init__(self):
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
        else:
            logger.warning("OpenAI API key not configured")

    def translate_cv_content(self, cv, target_language):
        """
        Translate CV content to target language using OpenAI
        """
        if not settings.OPENAI_API_KEY:
            raise Exception("OpenAI API key not configured")

        if target_language not in self.SUPPORTED_LANGUAGES:
            raise Exception(f"Language '{target_language}' not supported")

        language_name = self.SUPPORTED_LANGUAGES[target_language]

        # Prepare content to translate
        content_to_translate = {
            "title": cv.title,
            "bio": cv.bio,
            "experience": cv.experience,
            "education": cv.education,
            "skills": [skill.name for skill in cv.skills.all()],
        }

        # Create translation prompt
        prompt = self._create_translation_prompt(content_to_translate, language_name)

        try:
            # Call OpenAI API
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional translator specializing in translating CVs and professional documents to {language_name}. Maintain professional tone and accuracy.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=2000,
                temperature=0.3,
            )

            # Parse response
            translated_content = self._parse_translation_response(
                response.choices[0].message.content
            )

            return {
                "success": True,
                "translated_content": translated_content,
                "target_language": language_name,
                "original_cv": cv,
            }

        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return {"success": False, "error": str(e), "target_language": language_name}

    def _create_translation_prompt(self, content, target_language):
        """Create prompt for OpenAI translation"""
        return f"""
            Please translate the following CV content to {target_language}. 
            Maintain professional terminology and preserve the structure.
            Return the translation in the same JSON format:

            {content}

            Please respond with a JSON object containing the translated fields:
            {{
                "title": "translated title",
                "bio": "translated bio",
                "experience": "translated experience", 
                "education": "translated education",
                "skills": ["translated", "skill", "names"]
            }}
            """

    def _parse_translation_response(self, response_content):
        """Parse OpenAI response and extract translated content"""
        import json

        try:
            # Try to extract JSON from response
            start_idx = response_content.find("{")
            end_idx = response_content.rfind("}") + 1

            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_content[start_idx:end_idx]
                return json.loads(json_str)
            else:
                raise Exception("Could not parse translation response")

        except json.JSONDecodeError:
            # Fallback: return original structure with response as bio
            return {
                "title": "Translation Error",
                "bio": response_content,
                "experience": "Translation Error",
                "education": "Translation Error",
                "skills": ["Translation Error"],
            }

    @classmethod
    def get_supported_languages(cls):
        """Get list of supported languages"""
        return cls.SUPPORTED_LANGUAGES
