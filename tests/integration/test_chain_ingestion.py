import pytest
from unittest.mock import MagicMock, patch
from core.services.sanitization_service import SanitizationService
from core.services.embedding_service import EmbeddingService
from core.services.cohomology_service import CohomologyService
from core.entities.knowledge_chunk import KnowledgeChunk
from infrastructure.repositories.knowledge_repository import KnowledgeRepository

@pytest.fixture
def repo():
    with patch("infrastructure.repositories.knowledge_repository.get_supabase_client") as mock_db:
        return KnowledgeRepository()

@pytest.fixture
def sanitizer():
    with patch("core.services.sanitization_service.get_genai_client") as mock_client:
        return SanitizationService()

@pytest.fixture
def embedder():
    with patch("core.services.embedding_service.get_genai_client") as mock_client:
        return EmbeddingService()

@pytest.fixture
def cohort(repo):
    with patch("core.services.cohomology_service.get_genai_client") as mock_client:
        return CohomologyService(repo)

def test_full_chain_isolation(sanitizer, embedder, cohort, repo):
    """
    Test d'intégration simulant le passage d'un texte à travers toute la chaîne.
    Les services sont réels, seules les APIs externes sont mockées.
    """
    # Arrange
    text = "The Boy Scout Rule: Leave the code cleaner than you found it."
    
    # Mock Sanitizer L3 (Success)
    mock_sani_res = MagicMock()
    mock_sani_res.text = '{"is_safe": true}'
    sanitizer._client.models.generate_content.return_value = mock_sani_res
    
    # Mock Embedder (MC distribution)
    mock_emb_res = MagicMock()
    mock_emb_res.embeddings = [MagicMock(values=[0.1] * 768)]
    embedder._client.models.embed_content.return_value = mock_emb_res
    # Mock variant generation (Skipping LLM for speed)
    with patch.object(embedder, "generate_variants", return_value=[text]):
        # Mock Cohomology neighbors (No conflict)
        repo.find_similar_chunks = MagicMock(return_value=[])

        # Act
        # 1. Sanitization
        safety = sanitizer.validate_content(text)
        assert safety["is_safe"] is True
        
        # 2. Embedding
        mu, sigma = embedder.calculate_distribution([text])
        
        # 3. Cohomology
        action = cohort.check_contradiction(text, mu)
        assert action["action"] == "INSERT"
        
        # 4. Persistence
        chunk = KnowledgeChunk(content=text, source="test.md", embedding=mu, variance=sigma)
        repo.save_chunk(chunk)
        
        # Assert
        repo._db.table.assert_called_with("knowledge_chunks")
        repo._db.table().insert.assert_called()
