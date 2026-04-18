import pytest
from unittest.mock import MagicMock, patch, ANY
from core.entities.knowledge_chunk import KnowledgeChunk
from infrastructure.repositories.knowledge_repository import KnowledgeRepository

@pytest.fixture
def mock_supabase():
    with patch("infrastructure.repositories.knowledge_repository.get_supabase_client") as mock:
        yield mock.return_value

@pytest.fixture
def repository(mock_supabase):
    return KnowledgeRepository()

def test_save_chunk(repository, mock_supabase):
    # Arrange
    chunk = KnowledgeChunk(content="Test", source="src", embedding=[0.1], variance=[0.2])
    
    # Act
    repository.save_chunk(chunk)
    
    # Assert
    mock_supabase.table.assert_called_with("knowledge_chunks")
    mock_supabase.table().insert.assert_called_once()

def test_find_similar_chunks(repository, mock_supabase):
    # Arrange
    mock_response = MagicMock()
    mock_response.data = [{"id": "1", "content": "Match"}]
    mock_supabase.rpc.return_value.execute.return_value = mock_response
    
    # On mocke aussi la mise à jour des métriques appelée en interne
    with patch.object(repository, "_update_recall_metrics"):
        # Act
        results = repository.find_similar_chunks({"query_embedding": [0.1], "limit": 2})
        
        # Assert
        assert len(results) == 1
        assert results[0]["id"] == "1"
        mock_supabase.rpc.assert_called_with("search_knowledge_fisher", ANY)

def test_apply_langevin_update(repository, mock_supabase):
    # Act
    repository.apply_langevin_update(0.1, 0.01, 0.05)
    
    # Assert
    mock_supabase.rpc.assert_called_with("langevin_energy_update", {
        "dt": 0.1,
        "noise_amplitude": 0.01,
        "storage_cost": 0.05
    })
