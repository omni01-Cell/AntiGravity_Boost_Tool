import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from core.services.embedding_service import EmbeddingService

@pytest.fixture
def service():
    with patch("core.services.embedding_service.get_genai_client") as mock_client:
        return EmbeddingService()

def test_calculate_distribution_math(service):
    # Arrange
    # variants: [[1, 0], [0, 1]]
    # mu: [0.5, 0.5]
    # var: [0.25, 0.25]
    variants = ["v1", "v2"]
    mock_embeddings = [
        [1.0, 0.0],
        [0.0, 1.0]
    ]
    
    with patch.object(service, "_fetch_embedding", side_effect=mock_embeddings):
        # Act
        mu, sigma_sq = service.calculate_distribution(variants)
        
        # Assert
        assert mu == [0.5, 0.5]
        assert sigma_sq == [0.25, 0.25]

def test_generate_variants_includes_original(service):
    # Arrange
    text = "Source text"
    
    with patch.object(service, "_generate_single_variant", return_value="Variant"):
        # Act
        variants = service.generate_variants(text)
        
        # Assert
        assert text in variants
        assert len(variants) == 3 # 1 original + 2 prompts

def test_fetch_embedding_api_call(service):
    # Arrange
    mock_res = MagicMock()
    mock_res.embeddings = [MagicMock(values=[0.1, 0.2])]
    service._client.models.embed_content.return_value = mock_res
    
    # Act
    emb = service._fetch_embedding("test")
    
    # Assert
    assert emb == [0.1, 0.2]
    service._client.models.embed_content.assert_called_once()
