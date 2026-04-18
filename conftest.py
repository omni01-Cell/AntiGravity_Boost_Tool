"""
Fixtures et mocks partagés pour toute la suite de tests AGBoost.
Isole les dépendances externes (Supabase, Gemini API) afin que
les tests soient F.I.R.S.T. : Fast, Independent, Repeatable.
"""
import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# Assurer que le projet est dans le path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ──────────────────────────────────────────────
# Fixture : Mock du client Supabase global
# ──────────────────────────────────────────────
@pytest.fixture
def mock_supabase():
    """Fournit un client Supabase entièrement mocké."""
    mock = MagicMock()
    mock_response = MagicMock()
    mock_response.data = []
    mock.table.return_value.select.return_value.limit.return_value.execute.return_value = mock_response
    mock.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response
    mock.table.return_value.insert.return_value.execute.return_value = mock_response
    mock.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_response
    mock.rpc.return_value.execute.return_value = mock_response
    return mock


# ──────────────────────────────────────────────
# Fixture : Mock du client Gemini API
# ──────────────────────────────────────────────
@pytest.fixture
def mock_gemini_client():
    """Fournit un client Gemini API mocké avec embedding par défaut."""
    mock = MagicMock()
    mock_embedding = MagicMock()
    mock_embedding.values = [0.1] * 768
    mock_embed_result = MagicMock()
    mock_embed_result.embeddings = [mock_embedding]
    mock.models.embed_content.return_value = mock_embed_result
    mock_generate = MagicMock()
    mock_generate.text = '{"is_safe": true}'
    mock.models.generate_content.return_value = mock_generate
    return mock


# ──────────────────────────────────────────────
# Fixture : Répertoire temporaire pour fichiers
# ──────────────────────────────────────────────
@pytest.fixture
def temp_review_dir(tmp_path):
    """Crée un dossier temporaire simulant pending/review."""
    review_dir = tmp_path / "pending" / "review"
    review_dir.mkdir(parents=True)
    return review_dir


@pytest.fixture
def temp_quarantine_dir(tmp_path):
    """Crée un dossier temporaire simulant pending/quarantine."""
    quarantine_dir = tmp_path / "pending" / "quarantine"
    quarantine_dir.mkdir(parents=True)
    return quarantine_dir
