import pytest
import time
from unittest.mock import MagicMock, patch
from core.services.memory_service import MemoryService

@pytest.fixture
def service():
    with patch("core.services.memory_service.KnowledgeRepository") as mock_repo:
        svc = MemoryService(interval_seconds=0.1) # Petit intervalle pour les tests
        svc._repository = mock_repo
        yield svc
        svc.stop()

def test_memory_service_cycle_and_stop(service):
    # Arrange
    service.start()
    
    # Act
    # Attendre un cycle
    time.sleep(0.2)
    service.stop()
    service.join(timeout=1)
    
    # Assert
    assert service._repository.apply_langevin_update.called
    assert not service.is_alive()

def test_evolve_memory_error_handling(service):
    # Arrange
    service._repository.apply_langevin_update.side_effect = Exception("DB Error")
    
    # Act
    #Appel direct pour tester le try/except
    service._evolve_memory()
    
    # Assert
    # Ne doit pas lever d'exception (capturée en print dans le code source)
    service._repository.apply_langevin_update.assert_called_once()
