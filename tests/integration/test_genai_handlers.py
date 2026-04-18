import pytest
import os
from unittest.mock import patch
from infrastructure.handlers.genai_client import get_genai_client

def test_genai_client_singleton():
    # Arrange
    with patch.dict(os.environ, {"GEMINI_API_KEY": "fake-key"}):
        # Act
        client1 = get_genai_client()
        client2 = get_genai_client()
        
        # Assert
        assert client1 is client2
        assert client1 is not None

def test_genai_client_missing_key():
    # Arrange
    with patch.dict(os.environ, {}, clear=True):
        # We need to reset the singleton for this test
        import infrastructure.handlers.genai_client as client_module
        client_module._client = None
        
        # Act & Assert
        with pytest.raises(ValueError) as exc:
            get_genai_client()
        assert "GEMINI_API_KEY manquant" in str(exc.value)
