import pytest
import os
from unittest.mock import patch, MagicMock
from infrastructure.handlers.docstrange_client import DocStrangeClient

def test_docstrange_client_init_success():
    # Arrange
    with patch.dict(os.environ, {"DOCSTRANGE_API_KEY": "test-key"}):
        with patch("infrastructure.handlers.docstrange_client.DocumentExtractor"):
            # Act
            client = DocStrangeClient()
            # Assert
            assert client._api_key == "test-key"

def test_docstrange_client_init_missing_key():
    # Arrange
    with patch.dict(os.environ, {}, clear=True):
        # Act & Assert
        with pytest.raises(ValueError, match="DOCSTRANGE_API_KEY manquant"):
            DocStrangeClient()

def test_extract_markdown_api_path(tmp_path):
    """Vérifie que pour un PDF, on appelle l'API externe."""
    # Arrange
    with patch.dict(os.environ, {"DOCSTRANGE_API_KEY": "test-key"}):
        with patch("infrastructure.handlers.docstrange_client.DocumentExtractor") as mock_extractor:
            mock_instance = mock_extractor.return_value
            mock_result = MagicMock()
            mock_result.extract_markdown.return_value = "# Hello"
            mock_instance.extract.return_value = mock_result
            
            client = DocStrangeClient()
            
            # Act
            result = client.extract_markdown("fake.pdf")
            
            # Assert
            assert result == "# Hello"
            mock_instance.extract.assert_called_once_with("fake.pdf")

def test_extract_markdown_direct_read(tmp_path):
    """Vérifie que pour un MD, on lit directement le fichier sans appel API."""
    # Arrange
    test_file = tmp_path / "test.md"
    test_file.write_text("# Direct Content", encoding="utf-8")
    
    with patch.dict(os.environ, {"DOCSTRANGE_API_KEY": "test-key"}):
        with patch("infrastructure.handlers.docstrange_client.DocumentExtractor") as mock_extractor:
            client = DocStrangeClient()
            
            # Act
            result = client.extract_markdown(str(test_file))
            
            # Assert
            assert result == "# Direct Content"
            mock_extractor.return_value.extract.assert_not_called()
