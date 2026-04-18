import sys
import os
import time
from datetime import datetime, timezone
from pathlib import Path

# Injection du répertoire racine dans le sys.path pour permettre les imports relatifs
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from infrastructure.repositories.document_manifest import DocumentManifest, calculate_sha256
from core.services.ingestion_service import IngestionService
from core.services.memory_service import MemoryService
from constants import BOOKS_WATCH_DIR, SUPPORTED_EXTENSIONS

class BookEventHandler(FileSystemEventHandler):
    """Gère les événements du système de fichiers pour les livres."""
    
    def __init__(self, manifest: DocumentManifest, ingestion_service: IngestionService):
        self._manifest = manifest
        self._ingestion = ingestion_service

    def on_created(self, event) -> None:
        if event.is_directory: return
        self._process_file(event.src_path)

    def _process_file(self, filepath: str) -> None:
        if not filepath.lower().endswith(SUPPORTED_EXTENSIONS): return
        
        # Attente pour s'assurer que le fichier est totalement copié
        time.sleep(2)
        
        sha256 = calculate_sha256(filepath)
        if self._manifest.has_been_processed(sha256):
            return

        filename = os.path.basename(filepath)
        print(f"[Watcher] Nouveau document détecté : {filename}")
        
        try:
            stats = self._ingestion.process_file(filepath)
            status = "success" if stats["inserted"] > 0 else "error"
            self._manifest.mark_as_processed({
                "filename": filename,
                "sha256": sha256,
                "status": status,
                "processed_at": datetime.now(timezone.utc).isoformat()
            })
            print(f"[Watcher] Ingestion terminée : {stats['inserted']} insérés.")
        except Exception as e:
            print(f"[Watcher-Error] Échec du pipeline pour {filename} : {e}")

def run_book_watcher() -> None:
    """Démarre le service de surveillance et de maintenance mémorielle."""
    os.makedirs(BOOKS_WATCH_DIR, exist_ok=True)
    
    manifest = DocumentManifest("processed_books.json")
    manifest.remove_errors()
    
    ingestion_service = IngestionService()
    
    # Démarrage du moteur de Langevin
    memory_service = MemoryService(interval_seconds=3600)
    memory_service.start()
    
    observer = Observer()
    handler = BookEventHandler(manifest, ingestion_service)
    observer.schedule(handler, BOOKS_WATCH_DIR, recursive=False)
    
    print(f"[AntiGravity] Système de surveillance actif sur {BOOKS_WATCH_DIR}")
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        memory_service.stop()
        print("\n[AntiGravity] Arrêt du système.")
    
    observer.join()

if __name__ == "__main__":
    run_book_watcher()
