from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import uuid

@dataclass(frozen=True)
class KnowledgeChunk:
    """
    Entité immuable représentant un fragment de connaissance.
    Suit les principes de la géométrie de l'information (SLM-V3).
    """
    content: str
    source: str
    embedding: List[float]
    variance: List[float]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    chapter: Optional[str] = None
    category: str = "THEORY"
    energy: float = 1.0
    importance_score: float = 0.5
    access_count: int = 0
    is_flagged: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content": self.content,
            "source": self.source,
            "embedding": self.embedding,
            "variance": self.variance,
            "chapter": self.chapter,
            "category": self.category,
            "energy": self.energy,
            "importance_score": self.importance_score,
            "access_count": self.access_count,
            "is_flagged": self.is_flagged,
            "created_at": self.created_at.isoformat()
        }
