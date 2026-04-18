import json
import logging
from typing import TypedDict, List, Literal, Optional
from google.genai import types
from infrastructure.handlers.genai_client import get_genai_client
from infrastructure.repositories.knowledge_repository import KnowledgeRepository
from constants import (
    CONTRADICTION_CONFIDENCE_THRESHOLD,
    DEFAULT_COGNITIVE_MODEL
)

# Configuration du logger pour le service
logger = logging.getLogger(__name__)

class ContradictionResult(TypedDict):
    """Structure du résultat retourné par le LLM de Cohomologie."""
    is_contradiction: bool
    confidence: float
    reason: str
    recommendation: Literal["OVERWRITE", "FLAG_FOR_REVIEW", "INSERT_BOTH"]

class ActionResponse(TypedDict):
    """Structure de retour du service CohomologyService."""
    action: Literal["INSERT", "FLAG"]
    reason: Optional[str]

class CohomologyService:
    """
    Service de détection de contradictions sémantiques (Cohomologie).
    Empêche l'insertion de chunks contradictoires avec le savoir existant.
    """

    def __init__(self, repository: KnowledgeRepository):
        self._client = get_genai_client()
        self._repository = repository

    def check_contradiction(self, new_content: str, embedding: List[float]) -> ActionResponse:
        """Vérifie si le nouveau contenu contredit les voisins les plus proches."""
        neighbors = self._repository.find_similar_chunks({
            "query_embedding": embedding,
            "limit": 3,
            "threshold": 0.82
        })
        
        for neighbor in neighbors:
            result = self._evaluate_conflict(neighbor["content"], new_content)
            if self._is_critical_conflict(result):
                return self._handle_conflict(neighbor, new_content, result)
        
        return {"action": "INSERT", "reason": None}

    def _evaluate_conflict(self, existing: str, new: str) -> ContradictionResult:
        """Utilise le modèle cognitif pour détecter une contradiction logique."""
        prompt = self._build_contradiction_prompt(existing, new)
        try:
            res = self._client.models.generate_content(
                model=DEFAULT_COGNITIVE_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    thinking_config=types.ThinkingConfig(thinking_level="HIGH")
                )
            )
            
            if not res or not res.text:
                raise ValueError("Réponse LLM vide pour l'évaluation du conflit.")
            
            result: ContradictionResult = json.loads(res.text)
            self._validate_result_schema(result)
            return result
            
        except Exception as e:
            logger.error(f"Erreur d'évaluation Cohomologie : {str(e)}")
            # En cas d'erreur de raisonnement, on privilégie la sécurité (non-contradiction par défaut)
            return {
                "is_contradiction": False,
                "confidence": 0.0,
                "reason": "Evaluation failed",
                "recommendation": "INSERT_BOTH"
            }

    def _validate_result_schema(self, result: ContradictionResult) -> None:
        """Vérifie la présence des clés essentielles dans le retour JSON (Règle 66)."""
        required_keys = ["is_contradiction", "confidence", "reason", "recommendation"]
        for key in required_keys:
            if key not in result:
                raise KeyError(f"Clé manquante dans le résultat de Cohomologie : {key}")

    def _is_critical_conflict(self, result: ContradictionResult) -> bool:
        """Détermine si le conflit atteint le seuil de criticité configuré."""
        return (result.get("is_contradiction", False) and 
                result.get("confidence", 0.0) >= CONTRADICTION_CONFIDENCE_THRESHOLD)

    def _handle_conflict(self, neighbor: dict, new_content: str, result: ContradictionResult) -> ActionResponse:
        """Gère l'arbitrage du conflit (FLAG ou OVERWRITE)."""
        recommendation = result.get("recommendation", "FLAG_FOR_REVIEW")
        
        if recommendation == "OVERWRITE":
            self._repository.flag_chunk_as_obsolete(neighbor["id"])
            return {"action": "INSERT", "reason": "Existing chunk marked as obsolete"}
            
        return {"action": "FLAG", "reason": result.get("reason")}

    def _build_contradiction_prompt(self, existing: str, new: str) -> str:
        """Construit le prompt pour l'analyse cognitive du conflit."""
        return f"""Identifiez les contradictions logiques entre ces deux textes techniques.
Existant : {existing}
Nouveau : {new}
Répondez strictement en JSON: {{"is_contradiction": boolean, "confidence": float, "reason": "string", "recommendation": "OVERWRITE|FLAG_FOR_REVIEW|INSERT_BOTH"}}"""
