from typing import List, Tuple
import numpy as np
from google.genai import types
from infrastructure.handlers.genai_client import get_genai_client
from constants import (
    EMBEDDING_DIM,
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_GENERATIVE_MODEL
)

class EmbeddingService:
    """
    Service de calcul d'embeddings distribués (SLM-V3).
    Génère la moyenne et la variance via une approche Monte Carlo.
    """

    def __init__(self):
        self._client = get_genai_client()

    def calculate_distribution(self, text_variants: List[str]) -> Tuple[List[float], List[float]]:
        """Calcule μ et σ² pour une liste de variantes sémantiques."""
        all_embeddings = [self._fetch_embedding(t) for t in text_variants]
        
        # Conversion en numpy pour le calcul vectoriel efficace
        matrix = np.array(all_embeddings)
        
        mu = np.mean(matrix, axis=0).tolist()
        sigma_sq = np.var(matrix, axis=0).tolist()
        
        return mu, sigma_sq

    def generate_variants(self, text: str) -> List[str]:
        """Génère des variantes sémantiques pour l'analyse de variance."""
        prompts = [
            f"Résume techniquement ce bloc : {text[:1000]}",
            f"Paraphrase ce texte en gardant la précision : {text[:1000]}"
        ]
        
        variants = [text] # L'original est toujours inclus
        for p in prompts:
            variants.append(self._generate_single_variant(p))
            
        return variants

    def _fetch_embedding(self, text: str) -> List[float]:
        """Appel à l'API Gemini Embedding."""
        res = self._client.models.embed_content(
            model=DEFAULT_EMBEDDING_MODEL,
            contents=text,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
                output_dimensionality=EMBEDDING_DIM
            )
        )
        return res.embeddings[0].values

    def _generate_single_variant(self, prompt: str) -> str:
        """Génération LLM d'une variante unique."""
        try:
            res = self._client.models.generate_content(
                model=DEFAULT_GENERATIVE_MODEL,
                contents=prompt
            )
            return res.text if res.text else ""
        except Exception:
            return "" # Fallback silencieux (le calcul de variance gérera les vides si besoin)
