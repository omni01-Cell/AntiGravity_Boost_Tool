import threading
import time
from infrastructure.repositories.knowledge_repository import KnowledgeRepository
from constants import LANGEVIN_DT, LANGEVIN_NOISE_AMPLITUDE, STORAGE_COST

class MemoryService(threading.Thread):
    """
    Service d'évolution mémorielle (Langevin Engine).
    Gère le cycle de vie stochastique des connaissances en arrière-plan.
    """

    def __init__(self, interval_seconds: int = 3600):
        super().__init__(daemon=True)
        self._repository = KnowledgeRepository()
        self._interval = interval_seconds
        self._stop_event = threading.Event()

    def run(self) -> None:
        """Boucle principale du moteur de Langevin."""
        print(f"[MemoryService] Langevin Engine démarré (cycle: {self._interval}s)")
        while not self._stop_event.is_set():
            self._evolve_memory()
            self._stop_event.wait(self._interval)

    def stop(self) -> None:
        """Arrête proprement le service."""
        self._stop_event.set()

    def _evolve_memory(self) -> None:
        """Déclenche la mise à jour stochastique des énergies via le repository."""
        try:
            self._repository.apply_langevin_update(
                dt=LANGEVIN_DT,
                noise=LANGEVIN_NOISE_AMPLITUDE,
                cost=STORAGE_COST
            )
            print("[MemoryService] Cycle de Langevin complété avec succès.")
        except Exception as e:
            print(f"[MemoryService-Error] Échec du cycle : {e}")
