from typing import List, Dict, Any, TypedDict, Optional
from core.entities.knowledge_chunk import KnowledgeChunk
from infrastructure.handlers.supabase_client import get_supabase_client
from constants import SIMILARITY_THRESHOLD, EMA_ALPHA

class SearchParameters(TypedDict):
    """Paramètres de recherche pour la métrique de Fisher."""
    query_embedding: List[float]
    limit: Optional[int]
    threshold: Optional[float]

class FeedbackData(TypedDict):
    """Données de feedback pour la mise à jour LoopRAG."""
    chunk_id: str
    score: float

class KnowledgeRepository:
    """
    Gère la persistance des fragments de connaissance dans Supabase.
    Implémente la recherche Riemannian Fisher (SLM-V3).
    """

    def __init__(self):
        self._db = get_supabase_client()

    def save_chunk(self, chunk: KnowledgeChunk) -> None:
        """Persiste un chunk dans la base de données."""
        self._db.table("knowledge_chunks").insert(chunk.to_dict()).execute()

    def find_similar_chunks(self, params: SearchParameters) -> List[Dict[str, Any]]:
        """
        Recherche des chunks via la métrique de Fisher.
        """
        response = self._db.rpc("search_knowledge_fisher", {
            "query_embedding": params["query_embedding"],
            "match_count": params.get("limit", 5),
            "similarity_threshold": params.get("threshold", SIMILARITY_THRESHOLD)
        }).execute()
        
        results = response.data
        if results:
            self._update_recall_metrics([r["id"] for r in results])
            
        return results

    def _update_recall_metrics(self, chunk_ids: List[str]) -> None:
        """Incrémente l'usage et booste l'énergie (anti-oubli) lors d'un rappel."""
        for chunk_id in chunk_ids:
            curr = self._db.table("knowledge_chunks")\
                .select("access_count", "energy")\
                .eq("id", chunk_id).single().execute()
            
            if curr.data:
                self._db.table("knowledge_chunks").update({
                    "access_count": curr.data["access_count"] + 1,
                    "energy": min(curr.data["energy"] + 0.05, 1.5),
                    "last_accessed_at": "now()"
                }).eq("id", chunk_id).execute()

    def update_importance(self, feedback: FeedbackData) -> None:
        """Met à jour l'importance score via Moyenne Mobile Exponentielle (LoopRAG)."""
        chunk_id = feedback["chunk_id"]
        score = feedback["score"]
        
        curr = self._db.table("knowledge_chunks")\
            .select("importance_score")\
            .eq("id", chunk_id).single().execute()
        
        if curr.data:
            current_score = curr.data["importance_score"]
            new_score = EMA_ALPHA * score + (1 - EMA_ALPHA) * current_score
            self._db.table("knowledge_chunks").update({
                "importance_score": round(new_score, 4),
                "last_accessed_at": "now()"
            }).eq("id", chunk_id).execute()

    def flag_chunk_as_obsolete(self, chunk_id: str) -> None:
        """Marque un chunk comme obsolète lors d'une contradiction résolue par OVERWRITE."""
        self._db.table("knowledge_chunks").update({
            "is_flagged": True,
            "energy": 0.0
        }).eq("id", chunk_id).execute()

    def apply_langevin_update(self, dt: float, noise: float, cost: float) -> None:
        """Exécute la mise à jour stochastique globale des énergies."""
        self._db.rpc("langevin_energy_update", {
            "dt": dt,
            "noise_amplitude": noise,
            "storage_cost": cost
        }).execute()
