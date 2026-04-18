import pytest
import os
import json
from infrastructure.repositories.document_manifest import DocumentManifest, calculate_sha256

@pytest.fixture
def manifest_path(tmp_path):
    return tmp_path / "manifest.json"

def test_calculate_sha256(tmp_path):
    # Arrange
    f = tmp_path / "test.txt"
    f.write_text("hello", encoding="utf-8")
    
    # Act
    h = calculate_sha256(str(f))
    
    # Assert
    # hash of "hello" (sha256)
    assert h == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"

def test_manifest_lifecycle(manifest_path):
    # Arrange
    manifest = DocumentManifest(str(manifest_path))
    entry = {
        "filename": "test.md",
        "sha256": "abc",
        "status": "success",
        "processed_at": "now"
    }
    
    # Act & Assert 1: New
    assert not manifest.has_been_processed("abc")
    
    # Act 2: Mark as processed
    manifest.mark_as_processed(entry)
    assert manifest.has_been_processed("abc")
    
    # Act 3: Load again
    manifest2 = DocumentManifest(str(manifest_path))
    assert manifest2.has_been_processed("abc")

def test_remove_errors(manifest_path):
    # Arrange
    manifest = DocumentManifest(str(manifest_path))
    manifest.mark_as_processed({"filename": "ok.md", "sha256": "1", "status": "success", "processed_at": "now"})
    manifest.mark_as_processed({"filename": "err.md", "sha256": "2", "status": "error", "processed_at": "now"})
    
    # Act
    cleared = manifest.remove_errors()
    
    # Assert
    assert cleared == 1
    assert manifest.has_been_processed("1")
    assert not manifest.has_been_processed("2")
