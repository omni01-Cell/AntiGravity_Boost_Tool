import os
from docstrange import DocumentExtractor

class DocStrangeClient:
    """Handler pour l'extraction de documents via DocStrange."""
    
    def __init__(self):
        self._api_key = os.getenv("DOCSTRANGE_API_KEY")
        if not self._api_key:
            raise ValueError("DOCSTRANGE_API_KEY manquant.")
        self._extractor = DocumentExtractor(api_key=self._api_key)

    def extract_markdown(self, filepath: str) -> str:
        """
        Extrait le contenu d'un fichier en Markdown.
        Si le fichier est déjà du texte ou du markdown, on le lit directement.
        """
        if filepath.lower().endswith((".md", ".markdown", ".txt")):
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
                
        result = self._extractor.extract(filepath)
        return result.extract_markdown()
