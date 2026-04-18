import pytest
from unittest.mock import MagicMock, patch
from core.services.ingestion_service import IngestionService

@pytest.fixture
def service():
    """Fournit une instance de IngestionService avec les dépendances patchées."""
    with patch("core.services.ingestion_service.DocStrangeClient"), \
         patch("core.services.ingestion_service.EmbeddingService"), \
         patch("core.services.ingestion_service.SanitizationService"), \
         patch("core.services.ingestion_service.KnowledgeRepository"), \
         patch("core.services.ingestion_service.CohomologyService"):
        svc = IngestionService()
        yield svc

def test_chunk_text_nominal(service):
    # Arrange
    text = "A" * 3000
    size = 1500
    overlap = 200
    
    # Act
    chunks = service._chunk_text(text, size, overlap)
    
    # Assert
    # 3000 / (1500 - 200) = 3000 / 1300 ≈ 2.3 -> 3 chunks
    assert len(chunks) == 3
    assert chunks[0] == "A" * 1500
    assert len(chunks[2]) < 1500

def test_process_file_nominal(service):
    # Arrange
    filepath = "dummy.md"
    service._doc_client.extract_markdown.return_value = "Contenu test"
    # Simuler 1 chunk
    with patch.object(service, "_chunk_text", return_value=["Chunk 1"]):
        with patch.object(service, "_ingest_chunk", return_value=True) as mock_ingest:
            # Act
            stats = service.process_file(filepath)
            
            # Assert
            assert stats["inserted"] == 1
            assert stats["blocked"] == 0
            mock_ingest.assert_called_once_with("Chunk 1", "dummy.md")

def test_ingest_chunk_blocked_by_sanitization(service):
    # Arrange
    text = "Contenu dangereux"
    service._sanitization_service.validate_content.return_value = {
        "is_safe": False,
        "threats": ["PII"],
        "sanitized_content": None
    }
    
    # Act
    result = service._ingest_chunk(text, "test.md")
    
    # Assert
    assert result is False
    service._repository.save_chunk.assert_not_called()

def test_ingest_chunk_flagged_by_cohomology(service):
    # Arrange
    text = "Contenu contradictoire"
    service._sanitization_service.validate_content.return_value = {"is_safe": True}
    service._embedding_service.generate_variants.return_value = []
    service._embedding_service.calculate_distribution.return_value = ([0.1], [0.01])
    service._cohomology.check_contradiction.return_value = {
        "action": "FLAG",
        "reason": "Contradiction détectée"
    }
    
    # Act
    result = service._ingest_chunk(text, "test.md")
    
    # Assert
    assert result is False
    service._repository.save_chunk.assert_not_called()

def test_ingest_chunk_success(service):
    # Arrange
    text = "Tout est ok"
    service._sanitization_service.validate_content.return_value = {"is_safe": True}
    service._embedding_service.generate_variants.return_value = []
    service._embedding_service.calculate_distribution.return_value = ([0.1], [0.01])
    service._cohomology.check_contradiction.return_value = {"action": "INSERT", "reason": None}
    
    # Act
    result = service._ingest_chunk(text, "test.md")
    
    # Assert
    assert result is True
    service._repository.save_chunk.assert_called_once()
