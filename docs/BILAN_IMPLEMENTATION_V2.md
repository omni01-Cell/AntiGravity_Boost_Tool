# Bilan d'Implémentation — AGBoost V2

**Date** : 2026-04-13  
**Référence** : `DESIGN_DOC_V2.md`  
**Statut** : Implémentation complète — prêt pour installation des dépendances et tests

---

## 1. Fichiers produits

### Nouveaux fichiers

| Fichier | Rôle |
|---------|------|
| `manifest.py` | Tracking SHA-256 des livres traités (`BookManifest` + `computeSha256`) |
| `tests/test_manifest.py` | 9 tests unitaires pour `BookManifest` et `computeSha256` |
| `docs/design/002-architecture-v2.md` | Vue d'ensemble visuelle de l'architecture V2 |
| `docs/BILAN_IMPLEMENTATION_V2.md` | Ce document |

### Fichiers modifiés

| Fichier | Nature du changement |
|---------|----------------------|
| `parser.py` | Remplacement Docling → `DocStrangeConverter` |
| `agboost_cli.py` | `ingest_all` → `ingest` différentiel + `ensureRunning()` |
| `watchdog_service.py` | Scan de rattrapage au démarrage + vérification manifeste |
| `mcp_server.py` | Ajout outil `ensure_watchdog_running` |
| `requirements.txt` | `docling` retiré, nouvelles dépendances ajoutées |
| `.env.example` | `DOCSTRANGE_API_KEY` ajouté |
| `test_parser.py` | Mocks mis à jour + 3 tests `DocStrangeConverter` |

### Fichiers Antigravity produits

| Fichier | Rôle |
|---------|------|
| `~/.gemini/antigravity/skills/starting-session/SKILL.md` | Skill d'initialisation de session (4 gates) |
| `~/.gemini/GEMINI.md` | Section `## Session Initialization Protocol` ajoutée |

---

## 2. Ce qui a été implémenté vs le Design Doc

### Étape 1 — Manifeste d'ingestion ✅

`manifest.py` expose deux éléments publics :

- **`BookManifest`** — charge et persiste `processed_books.json`. Identifie un fichier par son hash SHA-256, pas son nom. Un fichier renommé ou copié ne génère pas de doublon. Un fichier remplacé par un contenu différent est détecté et réingéré.
- **`computeSha256(filepath)`** — lecture par blocs de 8 ko pour ne pas charger les gros PDFs en RAM.

### Étape 2 — Refactoring CLI ✅

`agboost_cli.py` :

- `ingest_all()` supprimée. Remplacée par `ingest()` qui interroge le manifeste avant de traiter chaque fichier.
- `_launchWatchdog()` extraite de `start()` pour être réutilisable sans effets de bord (pas de `print`).
- `ensureRunning()` ajoutée — retourne `"already_running"` ou `"started"` — conçue pour l'appel MCP sans sortie console.
- Le watchdog fait lui-même le scan de rattrapage à son démarrage (voir Étape 7), donc `start()` n'a pas besoin d'appeler `ingest()` séparément.

Interface CLI finale :
```
AGBoost start    → démarre le watchdog (qui scanne les manqués automatiquement)
AGBoost stop     → arrête le watchdog
AGBoost ingest   → ingestion manuelle différentielle (livres non encore traités)
```

### Étape 3 — Remplacement parser ✅

`parser.py` — `DocStrangeConverter` :

| Format | Traitement |
|--------|-----------|
| `.pdf`, `.docx`, `.pptx` | Envoi direct à l'API DocStrange (SDK `DocumentExtractor`) |
| `.md`, `.txt` | Lecture directe — pas d'appel API |
| `.epub` | Pré-conversion HTML → PDF via `ebooklib` + `weasyprint`, puis DocStrange |
| `.epub` (weasyprint absent) | Fallback : extraction texte directe via `ebooklib` + `BeautifulSoup` |

Tout le reste du pipeline (sanitizer L1/L2/L3, chunking, embedding Gemini, classification, Supabase) est **inchangé**.

### Étape 4 — MCP `ensure_watchdog_running` ✅

`mcp_server.py` — le nouvel outil délègue à `agboost_cli.ensureRunning()`. En cas d'erreur non anticipée, retourne `{ "status": "error", "detail": "..." }` plutôt que de lever une exception qui bloquerait le client MCP.

### Étape 5 — Meta-skill `starting-session` ✅

Créé dans `~/.gemini/antigravity/skills/starting-session/SKILL.md`.  
Format conforme aux skills existants (YAML frontmatter, gerund name, 3rd person description).  
4 gates séquentielles : AGBoost → knowledge-sync → GCC context → rapport de démarrage.

La règle d'enforcement dans `~/.gemini/GEMINI.md` (section `## Session Initialization Protocol`) rend l'exécution du skill non-contournable à chaque session.

### Étapes 6 & 7 — Tests + intégration watchdog ✅

`watchdog_service.py` :
- `_scanAndIngestPending()` appelé en premier dans `start_watchdog()` — résout le problème de perte silencieuse des fichiers ajoutés pendant l'absence du service.
- `DocumentHandler` reçoit le `BookManifest` à l'instanciation (injection de dépendance) plutôt qu'en variable globale.
- Les fichiers déjà traités sont ignorés silencieusement dans `on_created`.

Tests :
- `tests/test_manifest.py` — 9 cas (nominal, edge, persistence, schéma JSON, idempotence SHA-256).
- `test_parser.py` — mocks mis à jour pour `DocumentExtractor` + 3 cas `DocStrangeConverter` (PDF, .txt, .md).

---

## 3. Écarts par rapport au Design Doc

| Point | Design Doc | Implémenté | Raison |
|-------|-----------|------------|--------|
| EPUB → weasyprint | Obligatoire | Optionnel avec fallback | weasyprint a des dépendances natives complexes sur Windows (GTK/Cairo). Le fallback assure que le pipeline ne se bloque jamais. |
| `start()` → auto `ingest` | `start()` appelle `ingest()` | Le watchdog scanne au démarrage | Plus propre architecturalement : le watchdog est autonome. `start()` reste un simple lanceur. |

---

## 4. Ce qui reste à faire (hors scope V2)

Ces points ne font pas partie du périmètre validé mais sont à prévoir :

- [ ] **Nettoyage des PDF temporaires** en cas de crash pendant la conversion EPUB (fichiers `_converted.pdf` orphelins).
- [ ] **Retry automatique** pour les fichiers en `"error"` dans le manifeste (actuellement ils sont bloqués définitivement).
- [ ] **Test d'intégration** bout-en-bout : watchdog éteint → livre ajouté → redémarrage → vérifier ingestion dans Supabase.

---

## 5. Installation requise

```bash
# Installer les nouvelles dépendances
pip install -r requirements.txt

# Ajouter la clé DocStrange dans .env
# DOCSTRANGE_API_KEY=<clé obtenue sur docstrange.nanonets.com>
```
