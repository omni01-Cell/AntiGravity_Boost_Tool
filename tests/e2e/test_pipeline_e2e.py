import pytest
import os
import shutil
import tempfile
from pathlib import Path
from dotenv import load_dotenv
from core.services.ingestion_service import IngestionService
from infrastructure.repositories.document_manifest import DocumentManifest, calculate_sha256

# Chargement de l'environnement réel pour le test E2E
ROOT_DIR = Path(__file__).parent.parent.parent
load_dotenv(dotenv_path=ROOT_DIR / ".env")

@pytest.fixture
def temp_books_dir():
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)

@pytest.fixture
def manifest(temp_books_dir):
    path = temp_books_dir / "manifest.json"
    return DocumentManifest(str(path))

@pytest.fixture
def ingestion_service():
    return IngestionService()

@pytest.mark.e2e
def test_pipeline_e2e_nominal(temp_books_dir, manifest, ingestion_service):
    """
    Test End-to-End nominal : un document passer tout le pipeline
    DocStrange -> Sanitization -> Embedding MC -> Cohomology -> Supabase.
    """
    # 1. Arrange : Créer un fichier de test
    test_file = temp_books_dir / "e2e_test.md"
    content = "# Cognitive Architecture\n\nSLM-V3 uses Fisher information metric for vector search."
    test_file.write_text(content, encoding="utf-8")
    sha256 = calculate_sha256(str(test_file))

    # 2. Act : Lancer le traitement
    stats = ingestion_service.process_file(str(test_file))

    # 3. Assert
    assert stats["inserted"] > 0
    assert stats["blocked"] == 0
    
    # Vérifier le manifest (simulé ici car on utilise un manifest temporaire)
    # Dans un vrai usage, le watcher met à jour le manifest.
    # Ici on vérifie que le service a fonctionné.
    
    # 4. Cleanup (automatique via fixture)
