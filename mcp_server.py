import os
from mcp.server.fastmcp import FastMCP
from presentation.mcp.knowledge_tool import KnowledgeTool
from infrastructure.repositories.knowledge_repository import KnowledgeRepository
from constants import REVIEW_DIR

# Initialisation du Serveur MCP
mcp = FastMCP("Antigravity Knowledge")
_tool = KnowledgeTool()
_repo = KnowledgeRepository()

@mcp.tool()
def find_knowledge(query: str, count: int = 5) -> list:
    """Recherche des connaissances via la boucle LoopRAG (PDCA)."""
    return _tool.find_knowledge(query, count)

@mcp.tool()
def rate_knowledge_chunk(chunk_id: str, score: float) -> str:
    """Évalue la pertinence d'un chunk pour affiner la mémoire (EMA)."""
    try:
        _repo.update_importance({"chunk_id": chunk_id, "score": score})
        return "Évaluation enregistrée."
    except Exception as e:
        return f"Erreur : {e}"

@mcp.tool()
def get_pending_items() -> list:
    """Récupère les conflits en attente de revue humaine."""
    items = []
    if not os.path.exists(REVIEW_DIR):
        return items
        
    for filename in os.listdir(REVIEW_DIR):
        if filename.endswith(".json"):
            path = os.path.join(REVIEW_DIR, filename)
            with open(path, "r", encoding="utf-8") as f:
                import json
                data = json.load(f)
                data["_filename"] = filename
                items.append(data)
    return items

@mcp.tool()
def ensure_watchdog_running() -> dict:
    """Démarre ou vérifie le pipeline AGBoost."""
    try:
        from agboost_cli import ensure_running
        return {"status": ensure_running()}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

if __name__ == "__main__":
    mcp.run()
