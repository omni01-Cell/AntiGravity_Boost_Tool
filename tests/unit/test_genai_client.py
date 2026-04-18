import pytest
import os
from unittest.mock import patch, MagicMock
from infrastructure.handlers.genai_client import get_genai_client

def test_get_genai_client_singleton():
    # Arrange
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
        with patch("google.genai.Client") as mock_client:
            # Re-init singleton if needed (difficult with global, but we can check if it returns the same)
            # Act
            client1 = get_genai_client()
            client2 = get_genai_client()
            
            # Assert
            assert client1 is client2
            mock_client.assert_called_once()

def test_get_genai_client_missing_key():
    # Arrange
    with patch.dict(os.environ, {}, clear=True):
        # On doit s'assurer que _client est None pour déclencher l'erreur
        with patch("infrastructure.handlers.genai_client._client", None):
            # Act & Assert
            with pytest.raises(ValueError, match="GEMINI_API_KEY manquant"):
                get_genai_client()
