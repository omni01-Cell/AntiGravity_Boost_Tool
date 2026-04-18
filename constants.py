# Paramètres globaux du système cognitif AntiGravity

# --- Modèles IA (Identifiers) ---
DEFAULT_COGNITIVE_MODEL = "gemini-3.1-pro-preview"
DEFAULT_EMBEDDING_MODEL = "gemini-embedding-001"
DEFAULT_GENERATIVE_MODEL = "gemini-3.1-flash-lite-preview"

# --- Géométrie de l'Information (Fisher) ---
FISHER_EPSILON = 0.0001
SIMILARITY_THRESHOLD = 0.82
EMBEDDING_DIM = 768
MONTE_CARLO_VARIANTS = 3

# --- Dynamiques de Langevin (Mémoire) ---
LANGEVIN_DT = 0.1
LANGEVIN_NOISE_AMPLITUDE = 0.02
STORAGE_COST = 0.05
ENERGY_MIN = 0.1
ENERGY_MAX = 1.5
CLEANUP_THRESHOLD = 0.15

# --- Apprentissage PDCA (LoopRAG) ---
EMA_ALPHA = 0.3
CONTRADICTION_CONFIDENCE_THRESHOLD = 0.75
MAX_LOOPRAG_RETRIES = 3

# --- Infrastructure ---
BOOKS_WATCH_DIR = "./books"
SUPPORTED_EXTENSIONS = (".pdf", ".md", ".txt", ".docx", ".epub")
QUARANTINE_DIR = "./pending/quarantine"
REVIEW_DIR = "./pending/review"
