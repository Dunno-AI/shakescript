import google.generativeai as gemini
from ..core.config import settings

gemini.configure(api_key=settings.GEMINI_API_KEY)
model = gemini.GenerativeModel("gemini-2.0-flash")


def genai():
    return model
