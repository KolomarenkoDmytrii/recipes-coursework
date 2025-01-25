import google.generativeai as genai
from django.apps import AppConfig
from django.conf import settings


class MainConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "main"

    def ready(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
