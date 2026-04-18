import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_client: Client = None

def get_supabase_client() -> Client:
    """Fournit un client Supabase singleton."""
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("SUPABASE_URL et SUPABASE_KEY manquants dans l'environnement.")
        _client = create_client(url, key)
    return _client
