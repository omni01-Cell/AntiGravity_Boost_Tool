# Design Doc — AGBoost V2 : Ingestion Résiliente & Conversion Cloud

**Statut** : Approuvé  
**Auteur** : Leandre  
**Date** : 2026-04-13  
**Règle déclenchante** : Rule 52 — tout changement significatif d'architecture exige un Design Doc préalable.

---

## 1. Contexte et Problèmes Identifiés

### 1.1 Ingestion morte si le Watchdog est éteint

Le Watchdog surveille `books/` en temps réel, mais s'il est arrêté (crash, redémarrage PC, fin de session), tout livre déposé pendant son absence est **silencieusement ignoré**. La seule solution actuelle est `ingest-all`, qui retraite aveuglément tous les fichiers — y compris ceux déjà ingérés — gaspillant du temps et des ressources.

**Impact** : Rupture du principe Zero-Touch. L'utilisateur doit intervenir manuellement et se souvenir de lancer la commande.

### 1.2 Antigravity ne démarre pas AGBoost automatiquement

AGBoost tourne en processus invisible (`CREATE_NO_WINDOW`). À chaque nouvelle session de code, l'agent Antigravity opère sans savoir si le Watchdog est actif. Il n'existe aucun mécanisme pour qu'il le vérifie ou le démarre de lui-même.

**Impact** : Le pipeline d'ingestion est mort par défaut à chaque session, sauf si l'utilisateur pense à lancer `AGBoost start` manuellement.

### 1.3 Docling est trop coûteux en ressources locales

Docling est un outil d'extraction puissant mais gourmand : il charge des modèles ML localement pour chaque conversion. Sur un processeur 2015 (sans GPU), traiter un livre de 200–300 pages peut prendre plusieurs minutes et bloquer la machine.

**Impact** : Le traitement de livres volumineux est inenvisageable en pratique sur la machine cible.

---

## 2. Proposition

### 2.1 Remplacement de `ingest-all` par `ingest` (idempotent et différentiel)

**Supprimer** la commande `ingest-all`.  
**Introduire** une commande `ingest` (ou via le Watchdog au démarrage) qui :

1. Lit un **manifeste** (`processed_books.json`) stocké à la racine du projet.
2. Compare le contenu du dossier `books/` avec les entrées du manifeste.
3. Traite **uniquement les fichiers absents du manifeste**.
4. Met à jour le manifeste après chaque ingestion réussie.

Structure du manifeste :

```json
{
  "processed": [
    {
      "filename": "clean_code.pdf",
      "sha256": "a3f1...",
      "processed_at": "2026-04-13T10:22:00Z",
      "status": "success"
    }
  ]
}
```

L'identité d'un fichier est son **hash SHA-256** (pas seulement son nom), ce qui détecte un remplacement silencieux de fichier.

**Conséquences sur le CLI** :

| Avant (V1)      | Après (V2)              |
|-----------------|-------------------------|
| `AGBoost start` | `AGBoost start`         |
| `AGBoost stop`  | `AGBoost stop`          |
| `AGBoost ingest-all` | `AGBoost ingest`   |

Au démarrage du Watchdog (`AGBoost start`), une passe différentielle est automatiquement exécutée pour rattraper les fichiers ajoutés pendant l'absence du service.

### 2.2 Auto-lancement par Antigravity via MCP

Exposer un outil MCP `ensure_watchdog_running` dans `mcp_server.py`.

**Comportement** :
1. Vérifie si le PID dans `agboost.pid` correspond à un processus vivant.
2. Si non, appelle en interne `agboost_cli.start()`.
3. Retourne `{ "status": "started" | "already_running" }`.

Antigravity invoque cet outil **au début de chaque session** (via son meta-skill `session-init`). L'utilisateur n'a plus jamais à y penser.

```
Session Antigravity démarrée
  └─> MCP: ensure_watchdog_running()
        ├─ PID vivant ? → { status: "already_running" }
        └─ PID mort/absent ? → start() → { status: "started" }
```

### 2.3 Remplacement de Docling par DocStrange (Nanonets)

**DocStrange** ([docstrange.nanonets.com](https://docstrange.nanonets.com)) est un service cloud de parsing documentaire par Nanonets, optimisé pour les pipelines LLM/RAG.

**Pourquoi DocStrange plutôt que Docling en local :**

| Critère                   | Docling (local)         | DocStrange (cloud)           |
|---------------------------|-------------------------|------------------------------|
| Charge processeur         | Très élevée (modèles ML)| Nulle (déportée sur le cloud)|
| Qualité sur scans         | Bonne                   | Meilleure (OCR avancé)       |
| Support EPUB              | Oui                     | Non confirmé (PDF/DOCX/PPTX) |
| Tier gratuit              | N/A (open source local) | 10 000 docs/mois             |
| Intégration               | Python natif            | REST API + SDK Python        |
| Maintenance locale        | Dépendances lourdes     | Zéro dépendance ML locale    |

**Interface API** (REST, Bearer token) :

```python
# Exemple d'appel dans parser.py
import httpx

def convertToMarkdown(file_path: str, api_key: str) -> str:
    with open(file_path, "rb") as f:
        response = httpx.post(
            "https://docstrange.nanonets.com/api/v1/convert",
            headers={"Authorization": f"Bearer {api_key}"},
            files={"file": f},
            data={"output_format": "markdown"},
            timeout=120.0,
        )
    response.raise_for_status()
    return response.json()["markdown"]
```

La clé API est lue depuis une variable d'environnement `DOCSTRANGE_API_KEY` définie dans un fichier `.env` à la racine du projet (chargé via `python-dotenv`). Le fichier `.env` est exclu du contrôle de version (`.gitignore`).

**Point de vigilance EPUB** : DocStrange ne supporte pas officiellement l'EPUB. Stratégie de fallback retenue :
- Pré-conversion EPUB → PDF avec `ebooklib` + `weasyprint` (léger, sans ML) avant envoi à l'API.
- Cette pré-conversion est transparente : `DocStrangeConverter` la déclenche automatiquement si l'extension est `.epub`.

---

## 3. Alternatives Considérées

### 3.1 Alternative à DocStrange : Mistral Document API

Mistral propose une API d'OCR/parsing documentaire (`mistral-ocr`). Rejetée car :
- Moins mature que DocStrange pour la sortie Markdown structurée.
- Coût à l'usage moins prévisible (pas de tier gratuit généreux).

### 3.2 Alternative au manifeste JSON : SQLite

Une table SQLite (`books_manifest`) est plus robuste pour les requêtes complexes mais introduit une dépendance supplémentaire. Rejetée pour V2 : le JSON est suffisant et sans dépendance.

### 3.3 Alternative à `ensure_watchdog_running` MCP : tâche planifiée Windows

Utiliser le Planificateur de tâches Windows pour lancer AGBoost au démarrage de session Windows. Rejeté car :
- Couplage à l'OS, non portable.
- Antigravity perd la visibilité sur l'état du service.
- Moins cohérent avec l'architecture MCP existante.

---

## 4. Trade-offs

| Décision                              | Gain                                     | Coût / Risque                                      |
|---------------------------------------|------------------------------------------|----------------------------------------------------|
| Manifeste SHA-256                     | Idempotence robuste, détecte les doublons| Lecture/écriture disque à chaque démarrage (négligeable)|
| DocStrange cloud                      | Zéro charge CPU locale                   | Dépendance réseau, limites d'API, clé à gérer      |
| `ensure_watchdog_running` via MCP     | Session auto-réparante, Zero-Touch total | Antigravity doit appeler le meta-skill (à documenter dans session-init)|
| Suppression de `ingest-all`           | Simplification du CLI, cohérence         | Rupture de l'interface V1 (migration à documenter) |

---

## 5. Plan d'Implémentation

### Étape 1 — Manifeste d'ingestion
- [ ] Créer `BookManifest` (classe, `manifest.py`) : `load()`, `save()`, `isProcessed(sha256)`, `markAsProcessed(entry)`.
- [ ] Intégrer dans `watchdog_service.py` : filtrer les fichiers déjà présents dans le manifeste avant traitement.
- [ ] Intégrer dans le nouveau `ingest` CLI.

### Étape 2 — Refactoring CLI
- [ ] Dans `agboost_cli.py` : renommer `ingest_all()` → `ingest()`, logique différentielle via `BookManifest`.
- [ ] Mettre à jour `AGBoost.bat` si nécessaire.
- [ ] Au démarrage (`start()`), déclencher automatiquement une passe `ingest()`.

### Étape 3 — Remplacement du parser
- [ ] Dans `parser.py` : remplacer l'appel Docling par `DocStrangeConverter`.
- [ ] Créer `DocStrangeConverter` : appel REST, gestion timeout, gestion des erreurs HTTP, fallback EPUB.
- [ ] Lire `DOCSTRANGE_API_KEY` depuis l'environnement (`.env` + `python-dotenv`).
- [ ] Valider la réponse API avec Pydantic avant utilisation (Rule 63).

### Étape 4 — Outil MCP `ensure_watchdog_running`
- [ ] Ajouter la fonction dans `mcp_server.py`.

### Étape 5 — Meta-skill `session-init` (à créer)
Le meta-skill n'existe pas encore. Il doit être créé dans le workspace Antigravity.

**Comportement attendu** :
```
Au démarrage de chaque session de code :
  1. Appeler MCP: ensure_watchdog_running()
  2. Logger le résultat ("started" ou "already_running")
  3. Continuer la session normalement
```

**Fichier à créer** : `.agent/skills/session-init.md` (ou équivalent selon la convention Antigravity)

Contenu minimal du skill :
```markdown
# session-init

À exécuter au début de chaque session de travail.

## Étapes
1. Invoquer l'outil MCP `ensure_watchdog_running`.
2. Si le résultat est `started` : logger "AGBoost Watchdog démarré automatiquement."
3. Si le résultat est `already_running` : ne rien logger (silencieux).
```

### Étape 6 — Tests
- [ ] Mettre à jour `test_parser.py` : mocker l'appel HTTP DocStrange (pas le vrai service).
- [ ] Ajouter tests unitaires pour `BookManifest` (idempotence, détection SHA-256).
- [ ] Tester le scénario "watchdog éteint + livre ajouté + redémarrage → ingestion automatique".
- [ ] Tester le fallback EPUB → PDF → DocStrange.

---

## 6. Décisions Actées

| Question                                                        | Décision                                              |
|-----------------------------------------------------------------|-------------------------------------------------------|
| Support EPUB                                                    | Conservé via pré-conversion EPUB → PDF (`ebooklib` + `weasyprint`) |
| Stockage de la clé API DocStrange                               | Fichier `.env` local, exclu du VCS                    |
| Meta-skill `session-init`                                       | À créer (inexistant) — voir Étape 5                   |
