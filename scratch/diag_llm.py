import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

try:
    print("Appel avec models/gemini-3.1-flash-lite-preview")
    res = client.models.generate_content(
        model="models/gemini-3.1-flash-lite-preview",
        contents="Say hello in JSON.",
        config={"response_mime_type": "application/json"}
    )
    print(f"Success: {res.text}")
except Exception as e:
    print(f"ERROR: {str(e)}")
