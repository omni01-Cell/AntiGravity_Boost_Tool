import sys
import os
import subprocess
import psutil
from typing import Optional
from core.services.ingestion_service import IngestionService
from infrastructure.repositories.document_manifest import DocumentManifest, calculate_sha256
from constants import BOOKS_WATCH_DIR, SUPPORTED_EXTENSIONS

# Reconfiguration des encodages pour Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PID_FILE = os.path.join(PROJECT_ROOT, "agboost.pid")
LOG_FILE = os.path.join(PROJECT_ROOT, "agboost.log")

def find_active_pid() -> Optional[int]:
    """Récupère le PID du processus actif s'il existe."""
    if not os.path.exists(PID_FILE):
        return None
    with open(PID_FILE, "r") as f:
        try:
            pid = int(f.read().strip())
            return pid if psutil.pid_exists(pid) else None
        except (ValueError, psutil.NoSuchProcess):
            return None

def ensure_running() -> str:
    """Garantit que le service est actif. Retourne 'already_running' ou 'started'."""
    if find_active_pid():
        return "already_running"
    
    _launch_watcher()
    return "started"

def start_service() -> None:
    """Démarre le service watcher en arrière-plan."""
    pid = find_active_pid()
    if pid:
        print(f"[!] AGBoost est déjà en cours d'exécution (PID: {pid}).")
        return

    print("[*] Démarrage de AntiGravity Watchdog...")
    new_pid = _launch_watcher()
    print(f"[OK] Système lancé. PID: {new_pid} | Logs: {LOG_FILE}")

def stop_service() -> None:
    """Arrête proprement le service et ses processus enfants."""
    pid = find_active_pid()
    if not pid:
        print("[?] AGBoost n'est pas en cours d'exécution.")
        return

    print(f"[*] Arrêt du service (PID: {pid})...")
    try:
        p = psutil.Process(pid)
        for child in p.children(recursive=True):
            child.terminate()
        p.terminate()
        p.wait(timeout=3)
        print("[OK] Service arrêté.")
    except Exception as e:
        print(f"[!] Erreur lors de l'arrêt: {e}")
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)

def run_manual_ingestion() -> None:
    """Lance une ingestion différentielle manuelle via IngestionService."""
    if not os.path.exists(BOOKS_WATCH_DIR):
        print(f"[-] Dossier {BOOKS_WATCH_DIR} introuvable.")
        return

    manifest = DocumentManifest("processed_books.json")
    manifest.remove_errors()
    service = IngestionService()
    
    files = [f for f in os.listdir(BOOKS_WATCH_DIR) if f.lower().endswith(SUPPORTED_EXTENSIONS)]
    pending = [f for f in files if not manifest.has_been_processed(calculate_sha256(os.path.join(BOOKS_WATCH_DIR, f)))]

    if not pending:
        print("[OK] Aucun nouveau document à ingérer.")
        return

    print(f"[*] {len(pending)} nouveau(x) document(s) détecté(s).")
    for filename in pending:
        _ingest_single_file(os.path.join(BOOKS_WATCH_DIR, filename), manifest, service)

def _ingest_single_file(filepath: str, manifest: DocumentManifest, service: IngestionService) -> None:
    print(f">> Traitement de {os.path.basename(filepath)}...")
    try:
        stats = service.process_file(filepath)
        sha256 = calculate_sha256(filepath)
        manifest.mark_as_processed({
            "filename": os.path.basename(filepath),
            "sha256": sha256,
            "status": "success",
            "processed_at": "now()"
        })
        print(f"   [OK] {stats['inserted']} chunks insérés.")
    except Exception as e:
        print(f"   [!] Échec: {e}")

def _launch_watcher() -> int:
    """Lance book_watcher.py en arrière-plan."""
    script_path = os.path.join(PROJECT_ROOT, "presentation", "watchers", "book_watcher.py")
    
    # Injection du PROJECT_ROOT dans le PYTHONPATH pour éviter les ModuleNotFoundError
    env = os.environ.copy()
    env["PYTHONPATH"] = PROJECT_ROOT + os.pathsep + env.get("PYTHONPATH", "")
    
    with open(LOG_FILE, "a") as log:
        process = subprocess.Popen(
            [sys.executable, "-u", script_path],
            cwd=PROJECT_ROOT,
            env=env,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            stdout=log,
            stderr=subprocess.STDOUT
        )
    with open(PID_FILE, "w") as f:
        f.write(str(process.pid))
    return process.pid

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: py agboost_cli.py [start|stop|ingest]")
        sys.exit(1)

    commands = {"start": start_service, "stop": stop_service, "ingest": run_manual_ingestion}
    cmd = sys.argv[1].lower()
    
    if cmd in commands:
        commands[cmd]()
    else:
        print(f"Commande inconnue: {cmd}")
