# Architecture AGBoost V2 — Vue d'ensemble

> Document de référence visuelle. Reflète l'architecture cible définie dans `DESIGN_DOC_V2.md`.

---

## Vue Macro — Écosystème complet

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MACHINE LOCALE (Windows)                           │
│                                                                             │
│   ┌──────────────────────┐          ┌───────────────────────────────────┐  │
│   │   ANTIGRAVITY        │          │   AGBOOST SERVICE                 │  │
│   │   (Gemini CLI)       │◄────────►│   watchdog_service.py             │  │
│   │                      │   MCP    │   [processus invisible]           │  │
│   │  GEMINI.md (rules)   │          └───────────────┬───────────────────┘  │
│   │  skills/             │                          │                      │
│   │  └ starting-session  │                          ▼                      │
│   │  └ knowledge-sync    │               ┌──────────────────┐              │
│   │  └ gcc               │               │  books/          │              │
│   └──────────────────────┘               │  [PDF EPUB DOCX] │              │
│                                          └──────────────────┘              │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   │ HTTPS (REST)
                                   ▼
                      ┌────────────────────────┐
                      │  DOCSTRANGE (Nanonets) │
                      │  cloud parsing API     │
                      └────────────────────────┘
                                   │ Markdown
                                   ▼
                 ┌─────────────────────────────────────┐
                 │         SUPABASE (pgvector)         │
                 │   chunks · embeddings · importance  │
                 └─────────────────────────────────────┘
```

---

## Flux 1 — Initialisation de session (Session Init Protocol)

```
Antigravity démarre
        │
        ▼
┌───────────────────────────────────────┐
│  GEMINI.md — Session Init Protocol   │  ← règle absolue, non-contournable
│  "Exécute starting-session avant     │
│   toute autre action"                │
└───────────────┬───────────────────────┘
                │ invoque skill
                ▼
┌───────────────────────────────────────┐
│  Skill : starting-session             │
│                                       │
│  Gate 1 ─ ensure_watchdog_running()  │──► AGBoost déjà actif ?
│           MCP antigravity-knowledge  │      OUI → silencieux
│                                       │      NON → start() + log
│  Gate 2 ─ get_pending_items()        │──► Conflits knowledge ?
│           MCP antigravity-knowledge  │      OUI → skill knowledge-sync
│                                       │      NON → silencieux
│  Gate 3 ─ Lire .GCC/main.md         │──► Contexte session précédente ?
│                                       │      OUI → résumé 2-3 lignes
│                                       │      NON → silencieux
│  Gate 4 ─ Rapport de démarrage      │──► "[Session prête] ..."
└───────────────────────────────────────┘
                │
                ▼
      Session opérationnelle
```

---

## Flux 2 — Ingestion de document (Pipeline Zero-Touch)

```
Nouveau fichier déposé dans books/
              │
              ▼
┌─────────────────────────────────┐
│  BookManifest.isProcessed()    │
│  Vérification SHA-256          │
└──────────┬──────────────────────┘
           │
     ┌─────┴──────┐
     │ Déjà traité│──► SKIP (idempotent)
     └─────┬──────┘
           │ Nouveau
           ▼
┌─────────────────────────────────┐
│  Pré-traitement EPUB ?          │
│  .epub → ebooklib + weasyprint │
│  → .pdf temporaire              │
└──────────┬──────────────────────┘
           │ PDF / DOCX / TXT / MD
           ▼
┌─────────────────────────────────┐      ┌────────────────────────┐
│  DocStrangeConverter            │─────►│  docstrange.nanonets   │
│  POST /api/v1/convert           │      │  .com (cloud)          │
│  Authorization: Bearer $KEY     │◄─────│  → Markdown structuré  │
│  timeout: 120s                  │      └────────────────────────┘
└──────────┬──────────────────────┘
           │ Markdown brut
           ▼
┌─────────────────────────────────┐
│  Sanitizer Zero-Trust (3 lvls) │
│  L1 — Regex injections         │
│  L2 — Caractères invisibles    │
│  L3 — LLM validation sémant.   │
└──────────┬──────────────────────┘
           │ Markdown propre
           ▼
┌─────────────────────────────────────────────────────────┐
│  Classifier sémantique (LLM rapide)                     │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Cat. A      │  │  Cat. B      │  │  Cat. C      │  │
│  │  RÈGLES      │  │  SKILLS      │  │  THÉORIE     │  │
│  │  Standards   │  │  Méthodes    │  │  Gros volumes│  │
│  │  globaux     │  │  pratiques   │  │  temporaires │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
└─────────┼─────────────────┼─────────────────┼───────────┘
          │                 │                 │
          ▼                 ▼                 ▼
   .agent/rules/     pending/review/    Supabase pgvector
   (persistant)      (knowledge-sync)   (chunks + embedding
                                         + importance EMA)
          │                 │
          └────────┬────────┘
                   ▼
          BookManifest.markAsProcessed()
          processed_books.json mis à jour
```

---

## Flux 3 — Récupération de connaissance (RAG Query)

```
Antigravity reçoit une tâche technique
              │
              ▼
  ┌───────────────────────────┐
  │  GEMINI.md — Règle 63    │  ← "MUST call find_knowledge before any decision"
  └───────────┬───────────────┘
              │
              ▼
  ┌───────────────────────────────────────────┐
  │  MCP tool : find_knowledge(query)         │
  │  server   : antigravity-knowledge         │
  └───────────────────┬───────────────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │  Supabase pgvector     │
         │  Recherche hybride :   │
         │  cosine_similarity     │
         │  × importance_score    │
         │  × decay_factor (EMA)  │
         └────────────┬───────────┘
                      │ Top-K chunks
                      ▼
         ┌────────────────────────┐
         │  Antigravity applique  │
         │  les chunks à la tâche │
         └────────────┬───────────┘
                      │
                      ▼
  ┌───────────────────────────────────────────┐
  │  MCP tool : rate_knowledge_chunk(id, score)│
  │  1.0 = parfait · 0.5 = partiel · 0.0 = nul│
  │  → met à jour importance_score (EMA)      │
  └───────────────────────────────────────────┘
```

---

## Flux 4 — Résolution de conflit (Cohomologie)

```
Nouveau chunk catégorie A (Règle) ingéré
              │
              ▼
  ┌───────────────────────────────┐
  │  Detector de contradiction   │
  │  find_knowledge(nouveau_chunk)│
  │  → similarité > 0.85 ?       │
  └──────────┬────────────────────┘
             │
       ┌─────┴──────┐
       │ Conflit    │──────────────────────────────────────────────┐
       │ détecté    │                                              │
       └─────┬──────┘                                             │
             │ Non                                                 ▼
             ▼                                      ┌─────────────────────────┐
    Ingestion directe                               │  pending/review/        │
    en base                                         │  conflict_[id].json     │
                                                    │  { new, existing,       │
                                                    │    reason, similarity } │
                                                    └────────────┬────────────┘
                                                                 │
                                                                 ▼
                                                  Skill : knowledge-sync
                                                  ┌──────────────────────────┐
                                                  │  OVERWRITE  → remplacer  │
                                                  │  INSERT_BOTH → coexister │
                                                  │  DISCARD    → ignorer    │
                                                  └──────────────────────────┘
```

---

## Interface MCP — Outils exposés par AGBoost

```
mcp_server.py  (antigravity-knowledge)
│
├── ensure_watchdog_running()
│   Vérifie le PID dans agboost.pid.
│   Lance watchdog_service.py si mort/absent.
│   Retourne : { "status": "started" | "already_running" }
│
├── get_pending_items()
│   Liste les fichiers JSON dans pending/review/.
│   Retourne : [ { id, new_content, existing_content, reason } ]
│
├── find_knowledge(query: str, top_k: int = 5)
│   Embedding → recherche hybride Supabase.
│   Retourne : [ { chunk_id, content, score, source } ]
│
└── rate_knowledge_chunk(chunk_id: str, score: float)
    Met à jour importance_score via EMA.
    Retourne : { "ok": true }
```

---

## Structure des fichiers clés (V2)

```
AntiGravity_Boost_Tool/
│
├── agboost_cli.py          ← CLI : start / stop / ingest (différentiel)
├── watchdog_service.py     ← Surveille books/, déclenche ingest au démarrage
├── manifest.py             ← BookManifest : SHA-256, load/save/check
├── parser.py               ← DocStrangeConverter + fallback EPUB
├── classifier.py           ← Routage sémantique A/B/C
├── mcp_server.py           ← Serveur MCP (4 outils)
├── db_client.py            ← Client Supabase pgvector
│
├── books/                  ← Dossier surveillé (PDF, EPUB, DOCX)
├── pending/review/         ← Conflits en attente de résolution
├── processed_books.json    ← Manifeste SHA-256 (généré automatiquement)
├── .env                    ← DOCSTRANGE_API_KEY, SUPABASE_URL, etc.
│
└── docs/design/
    ├── 001-systeme-connaissance-adaptatif.md
    └── 002-architecture-v2.md   ← ce fichier
```

---

## Dépendances V2 (delta vs V1)

| Package           | Usage                            | Remplace       |
|-------------------|----------------------------------|----------------|
| `httpx`           | Appels REST DocStrange           | `docling`      |
| `ebooklib`        | Extraction EPUB → HTML           | —              |
| `weasyprint`      | HTML → PDF (fallback EPUB)       | —              |
| `python-dotenv`   | Chargement `.env`                | —              |
| `pydantic`        | Validation réponse API (Rule 63) | —              |
| `hashlib`         | SHA-256 manifeste (stdlib)       | —              |
