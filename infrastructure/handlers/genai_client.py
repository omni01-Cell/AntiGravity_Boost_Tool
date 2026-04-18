import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

_client: genai.Client = None

def get_genai_client() -> genai.Client:
    """Fournit un client GenAI singleton."""
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY manquant dans l'environnement.")
        _client = genai.Client(api_key=api_key)
    return _client
