from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

def list_available_models():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY manquant")
        return
    
    client = genai.Client(api_key=api_key)
    try:
        print("Modèles disponibles :")
        for model in client.models.list():
            print(f"- {model.name} ({model.display_name})")
    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    list_available_models()
