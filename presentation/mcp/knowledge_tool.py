import json
from typing import List, Dict, Any
from core.services.embedding_service import EmbeddingService
from infrastructure.repositories.knowledge_repository import KnowledgeRepository
from infrastructure.handlers.genai_client import get_genai_client
from constants import MAX_LOOPRAG_RETRIES

class KnowledgeTool:
    """
    Expose les outils de connaissance via le protocole MCP.
    Implémente la boucle fermée LoopRAG (PDCA).
    """

    def __init__(self):
        self._repository = KnowledgeRepository()
        self._embedding_service = EmbeddingService()
        self._client = get_genai_client()

    def find_knowledge(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Cycle PDCA (Plan-Do-Check-Act) pour la recherche de connaissances."""
        attempt = 0
        current_query = query
        
        while attempt < MAX_LOOPRAG_RETRIES:
            # 1. PLAN : MCPO (Optimisation de prompt)
            variants = self._plan_query_variants(current_query)
            
            # 2. DO : Recherche Fisher multi-variante
            results = self._search_multi_variantes(variants, limit)
            
            # 3. CHECK : Audit de qualité
            audit = self._check_quality(query, results)
            if audit["is_sufficient"]:
                return results
            
            # 4. ACT : Re-routage / Correction
            current_query = f"{query} (Focus: {audit['suggestion']})"
            attempt += 1
            
        return results

    def _plan_query_variants(self, query: str) -> List[str]:
        """Gère les variantes pour maximiser le rappel (Recall)."""
        prompt = f"Générez 2 variantes sémantiques techniques pour cette question : {query}. Répondez avec les variantes séparées par |."
        try:
            res = self._client.models.generate_content(model="gemini-3.1-flash-lite-preview", contents=prompt)
            variants = [query]
            if res.text:
                variants.extend([v.strip() for v in res.text.split("|") if len(v.strip()) > 5])
            return variants[:3]
        except Exception:
            return [query]

    def _search_multi_variantes(self, variants: List[str], limit: int) -> List[Dict[str, Any]]:
        """Exécute la recherche pour chaque variante et fusionne les résultats."""
        all_results = []
        seen_ids = set()
        
        for v in variants:
            emb = self._embedding_service._fetch_embedding(v) # Simplification pour le DO
            results = self._repository.find_similar_chunks({"query_embedding": emb, "limit": limit})
            for r in results:
                if r["id"] not in seen_ids:
                    all_results.append(r)
                    seen_ids.add(r["id"])
                    
        return sorted(all_results, key=lambda x: x.get("final_score", 0), reverse=True)[:limit]

    def _check_quality(self, query: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evalue l'alignement entre la requête et les résultats."""
        if not results:
            return {"is_sufficient": False, "suggestion": "Essayer des termes plus génériques."}
            
        context = "\n".join([f"- {r['content'][:100]}" for r in results])
        prompt = f"La question est '{query}'. Ces extraits y répondent-ils ? JSON: {{\"is_sufficient\": bool, \"suggestion\": \"string\"}}\n{context}"
        
        try:
            res = self._client.models.generate_content(
                model="gemini-3.1-flash-lite-preview", 
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            return json.loads(res.text)
        except Exception:
            return {"is_sufficient": True, "suggestion": ""} # On laisse passer par défaut
