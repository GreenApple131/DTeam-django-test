from django.conf import settings


def settings_context(request):
    """
    Context processor that injects Django settings into all templates.
    Be careful not to expose sensitive information in production.
    """
    # Define safe settings to expose in templates
    safe_settings = {
        "DEBUG": settings.DEBUG,
        "LANGUAGE_CODE": settings.LANGUAGE_CODE,
        "TIME_ZONE": settings.TIME_ZONE,
        "USE_I18N": settings.USE_I18N,
        "USE_TZ": settings.USE_TZ,
        "STATIC_URL": settings.STATIC_URL,
        "DEFAULT_AUTO_FIELD": settings.DEFAULT_AUTO_FIELD,
        "INSTALLED_APPS": settings.INSTALLED_APPS,
        "MIDDLEWARE": settings.MIDDLEWARE,
        "ROOT_URLCONF": settings.ROOT_URLCONF,
        "WSGI_APPLICATION": settings.WSGI_APPLICATION,
        "DATABASE_ENGINE": settings.DATABASES["default"]["ENGINE"],
        "REST_FRAMEWORK": getattr(settings, "REST_FRAMEWORK", {}),
    }

    # Add all settings in development mode (be cautious in production)
    if settings.DEBUG:
        # In debug mode, we can expose more settings
        # but still exclude sensitive ones
        excluded_settings = {
            "SECRET_KEY",
            "DATABASES",
            "PASSWORD_HASHERS",
            "AUTH_PASSWORD_VALIDATORS",
            "EMAIL_HOST_PASSWORD",
            "AWS_SECRET_ACCESS_KEY",
            "STRIPE_SECRET_KEY",
        }

        all_settings = {}
        for setting_name in dir(settings):
            if (
                not setting_name.startswith("_")
                and setting_name not in excluded_settings
                and setting_name.isupper()
            ):
                try:
                    all_settings[setting_name] = getattr(settings, setting_name)
                except Exception:
                    # Skip settings that can't be accessed
                    continue

        return {
            "django_settings": safe_settings,
            "all_django_settings": all_settings,
        }
    else:
        # In production, only expose safe settings
        return {
            "django_settings": safe_settings,
        }
