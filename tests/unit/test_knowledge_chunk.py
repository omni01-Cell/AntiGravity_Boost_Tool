import pytest
from datetime import datetime
from core.entities.knowledge_chunk import KnowledgeChunk

def test_knowledge_chunk_creation_with_defaults():
    # Arrange
    content = "Logic is the beginning of wisdom."
    source = "vulcan_logic.pdf"
    embedding = [0.1, 0.2, 0.3]
    variance = [0.01, 0.01, 0.01]

    # Act
    chunk = KnowledgeChunk(
        content=content,
        source=source,
        embedding=embedding,
        variance=variance
    )

    # Assert
    assert chunk.content == content
    assert chunk.source == source
    assert chunk.energy == 1.0
    assert chunk.category == "THEORY"
    assert isinstance(chunk.id, str)
    assert isinstance(chunk.created_at, datetime)

def test_knowledge_chunk_immutability():
    # Arrange
    chunk = KnowledgeChunk("Test", "source", [0.1], [0.01])
    
    # Act & Assert
    with pytest.raises(AttributeError):
        # dataclass(frozen=True) should prevent assignment
        chunk.energy = 2.0

def test_knowledge_chunk_to_dict():
    # Arrange
    chunk = KnowledgeChunk("Test", "source", [0.1], [0.01], energy=1.5)
    
    # Act
    data = chunk.to_dict()
    
    # Assert
    assert data["content"] == "Test"
    assert data["energy"] == 1.5
    assert isinstance(data["created_at"], str) # Should be ISO format
    assert "id" in data
