import os
import logging
from typing import List, Dict, TypedDict
from core.entities.knowledge_chunk import KnowledgeChunk
from core.services.embedding_service import EmbeddingService
from core.services.sanitization_service import SanitizationService, SafetyResult
from core.services.cohomology_service import CohomologyService, ActionResponse
from infrastructure.repositories.knowledge_repository import KnowledgeRepository
from infrastructure.handlers.docstrange_client import DocStrangeClient

logger = logging.getLogger(__name__)

class IngestionStats(TypedDict):
    """Statistiques d'ingestion pour une session."""
    inserted: int
    blocked: int

class IngestionService:
    """
    Service d'orchestration du pipeline d'ingestion (SLM-V3).
    Gère le cycle : Extraction -> Sanitisation -> Embedding Monte Carlo -> Ingestion.
    """

    def __init__(self):
        self._doc_client = DocStrangeClient()
        self._embedding_service = EmbeddingService()
        self._sanitization_service = SanitizationService()
        self._repository = KnowledgeRepository()
        self._cohomology = CohomologyService(self._repository)

    def process_file(self, filepath: str) -> IngestionStats:
        """Traite un fichier complet et l'ingère par chunks."""
        try:
            filename = os.path.basename(filepath)
            content = self._doc_client.extract_markdown(filepath)
            chunks = self._chunk_text(content)
            
            stats: IngestionStats = {"inserted": 0, "blocked": 0}
            for chunk_text in chunks:
                if self._ingest_chunk(chunk_text, filename):
                    stats["inserted"] += 1
                else:
                    stats["blocked"] += 1
                    
            return stats
        except Exception as e:
            logger.error(f"Erreur d'ingestion du fichier {filepath} : {str(e)}")
            return {"inserted": 0, "blocked": 0}

    def _ingest_chunk(self, text: str, source: str) -> bool:
        """Pipeline pour un seul chunk."""
        # 1. Sanitisation Zero-Trust
        validation: SafetyResult = self._sanitization_service.validate_content(text)
        if not validation["is_safe"]:
            logger.warning(f"Chunk bloqué par la sanitisation (source: {source}) : {validation['threats']}")
            return False

        # 2. Embedding + Variance (Monte Carlo)
        variants = self._embedding_service.generate_variants(text)
        mu, sigma_sq = self._embedding_service.calculate_distribution(variants)

        # 3. Cohomologie (Contradictions)
        action: ActionResponse = self._cohomology.check_contradiction(text, mu)
        if action["action"] == "FLAG":
            logger.info(f"Chunk flaggé pour revue (contradiction) : {action['reason']}")
            return False

        # 4. Persistence
        chunk = KnowledgeChunk(
            content=text,
            source=source,
            embedding=mu,
            variance=sigma_sq
        )
        self._repository.save_chunk(chunk)
        return True

    def _chunk_text(self, text: str, size: int = 1500, overlap: int = 200) -> List[str]:
        """Découpe le texte en segments avec chevauchement."""
        if not text: return []
        chunks: List[str] = []
        start = 0
        while start < len(text):
            end = min(start + size, len(text))
            chunks.append(text[start:end])
            start += size - overlap
        return chunks
