import pytest
import os
from unittest.mock import patch, MagicMock
from infrastructure.handlers import supabase_client
from infrastructure.handlers.supabase_client import get_supabase_client

@pytest.fixture(autouse=True)
def reset_singleton():
    """Réinitialise le singleton avant chaque test pour éviter les fuites d'état."""
    with patch("infrastructure.handlers.supabase_client._client", None):
        yield

def test_get_supabase_client_singleton():
    # Arrange
    with patch.dict(os.environ, {"SUPABASE_URL": "http://test", "SUPABASE_KEY": "test-key"}):
        with patch("infrastructure.handlers.supabase_client.create_client") as mock_create:
            # Act
            client1 = get_supabase_client()
            client2 = get_supabase_client()
            
            # Assert
            assert client1 is client2
            mock_create.assert_called_once()

def test_get_supabase_client_missing_config():
    # Arrange
    with patch.dict(os.environ, {}, clear=True):
        # Act & Assert
        with pytest.raises(ValueError, match="SUPABASE_URL et SUPABASE_KEY manquants"):
            get_supabase_client()
