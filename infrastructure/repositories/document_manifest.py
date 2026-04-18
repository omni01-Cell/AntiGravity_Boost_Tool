import hashlib
import json
import os
import logging
from typing import Set, List, TypedDict, Optional

logger = logging.getLogger(__name__)

class ManifestEntry(TypedDict):
    """Structure d'une entrée dans le manifest des documents."""
    filename: str
    sha256: str
    status: str
    processed_at: str

class DocumentManifest:
    """Suivi des documents déjà traités (idempotence)."""

    def __init__(self, path: str):
        self._path = path
        self._entries: List[ManifestEntry] = []
        self._processed_hashes: Set[str] = set()
        self._load()

    def has_been_processed(self, sha256: str) -> bool:
        """Vérifie si le hash existe dans le manifest."""
        return sha256 in self._processed_hashes

    def mark_as_processed(self, entry: ManifestEntry) -> None:
        """Ajoute un document au manifest."""
        self._entries.append(entry)
        self._processed_hashes.add(entry["sha256"])
        self._save()

    def remove_errors(self) -> int:
        """Nettoie les entrées en erreur pour permettre un re-essai."""
        initial_len = len(self._entries)
        self._entries = [e for e in self._entries if e.get("status") != "error"]
        cleared = initial_len - len(self._entries)
        
        if cleared > 0:
            self._processed_hashes = {e["sha256"] for e in self._entries}
            self._save()
        return cleared

    def _load(self) -> None:
        """Charge le manifest depuis le disque avec gestion d'erreurs."""
        if not os.path.exists(self._path):
            return
            
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._entries = data.get("processed", [])
                self._processed_hashes = {e["sha256"] for e in self._entries}
        except Exception as e:
            logger.error(f"Échec du chargement du manifest {self._path} : {str(e)}")
            self._entries = []

    def _save(self) -> None:
        """Persiste le manifest sur le disque."""
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump({"processed": self._entries}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Échec de la sauvegarde du manifest {self._path} : {str(e)}")

def calculate_sha256(filepath: str) -> str:
    """Calcule le hash SHA-256 d'un fichier de manière efficace par blocs."""
    hasher = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for block in iter(lambda: f.read(8192), b""):
                hasher.update(block)
        return hasher.hexdigest()
    except Exception as e:
        logger.error(f"Échec du calcul du hash pour {filepath} : {str(e)}")
        return ""
