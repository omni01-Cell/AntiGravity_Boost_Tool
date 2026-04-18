import pytest
from unittest.mock import MagicMock, patch
from core.services.cohomology_service import CohomologyService, ActionResponse

@pytest.fixture
def mock_repository():
    return MagicMock()

@pytest.fixture
def service(mock_repository):
    with patch("core.services.cohomology_service.get_genai_client") as mock_client:
        return CohomologyService(mock_repository)

def test_check_contradiction_insert_when_no_neighbors(service, mock_repository):
    # Arrange
    mock_repository.find_similar_chunks.return_value = []
    
    # Act
    response = service.check_contradiction("New info", [0.1, 0.2])
    
    # Assert
    assert response["action"] == "INSERT"
    assert response["reason"] is None

def test_check_contradiction_flag_when_critical_conflict(service, mock_repository):
    # Arrange
    neighbor = {"id": "old-1", "content": "The earth is flat."}
    mock_repository.find_similar_chunks.return_value = [neighbor]
    
    # Mock LLM response for evaluate_conflict
    mock_response = MagicMock()
    mock_response.text = '{"is_contradiction": true, "confidence": 0.95, "reason": "Scientific consensus", "recommendation": "FLAG_FOR_REVIEW"}'
    service._client.models.generate_content.return_value = mock_response

    # Act
    response = service.check_contradiction("The earth is round.", [0.1, 0.2])
    
    # Assert
    assert response["action"] == "FLAG"
    assert "Scientific consensus" in response["reason"]

def test_check_contradiction_overwrite_when_recommended(service, mock_repository):
    # Arrange
    neighbor = {"id": "old-1", "content": "Version 1.0 is stable."}
    mock_repository.find_similar_chunks.return_value = [neighbor]
    
    # Mock LLM response for evaluate_conflict
    mock_response = MagicMock()
    mock_response.text = '{"is_contradiction": true, "confidence": 0.99, "reason": "Version 2.0 released", "recommendation": "OVERWRITE"}'
    service._client.models.generate_content.return_value = mock_response

    # Act
    response = service.check_contradiction("Version 2.0 is stable.", [0.1, 0.2])
    
    # Assert
    assert response["action"] == "INSERT"
    mock_repository.flag_chunk_as_obsolete.assert_called_once_with("old-1")

def test_evaluate_conflict_error_handling(service):
    # Arrange
    service._client.models.generate_content.side_effect = Exception("API Down")
    
    # Act
    # This calls _evaluate_conflict internally
    result = service._evaluate_conflict("Old", "New")
    
    # Assert
    assert result["is_contradiction"] is False
    assert result["recommendation"] == "INSERT_BOTH"
