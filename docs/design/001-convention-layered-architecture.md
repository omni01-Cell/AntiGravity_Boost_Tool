# Design Doc: Convention & Layered Architecture Refactoring

**Auteur :** Antigravity  
**Date :** 2026-04-18  
**Statut :** Draft  
**Reviewers :** USER

---

## 1. Contexte et problème

Le projet **AntiGravity Boost Tool** a été développé rapidement pour atteindre une preuve de concept fonctionnelle. Cependant, il présente une dette technique importante qui entrave sa maintenance et son évolution :
- **Violation du SRP** : Des fonctions comme `process_document` gèrent toute la chaîne de valeur (extraction -> sanitisation -> embedding -> BDD).
- **Naming non-conforme** : Utilisation du `camelCase` (Python standard is `snake_case`) et manque de verbes infinitifs.
- **Couplage Infrastructure** : La logique métier est polluée par des appels directs à Supabase et aux APIs GenAI.
- **Typage faible** : Absence de types de retour et d'interfaces claires.

## 2. Objectifs

- **Must-have** : 100% de conformité avec les règles `user_global`.
- **Must-have** : Séparation stricte en couches (Presentation, Domain, Infrastructure).
- **Must-have** : Fonctions de moins de 20 lignes et maximum 2 arguments.
- **Out of scope** : Modification de la base de données (déjà migrée pour SLM-V3).

## 3. Proposition de solution

### Architecture en Couches
1. **Domain (Pure Python)** : Contient les entités (`KnowledgeChunk`) et les services métier (`InferenceService`, `SanitizationService`). Aucun import de framework UI ou DB externe.
2. **Infrastructure** : 
   - `repositories/` : Encapsule les accès Supabase.
   - `handlers/` : Clients pour Gemini et DocStrange.
3. **Presentation** : `watchdog/` pour la surveillance de fichiers et `mcp/` pour l'exposition des outils.

### Naming & Conventions
- Rename `convertToMarkdown` -> `convert_to_markdown`.
- Rename `isProcessed` -> `has_been_processed`.
- Utilisation systématique de `TypedDict` pour les paramètres complexes (> 2 args).

## 4. Alternatives considérées

### Option A — Refactoring incrémental (rejetée)
Modifier les fichiers en place sans changer l'arborescence.  
**Raison du rejet :** Trop complexe de garantir le découplage sans une structure de dossiers claire.

### Option B — Migration vers une architecture en services (retenue)
Création de répertoires dédiés par couche et migration progressive de la logique.

## 5. Compromis et risques

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Rupture de compatibilité | Élevée | Moyenne | Tests de régression E2E après chaque étape. |
| Complexité de fichiers | Moyenne | Faible | Utilisation d'un manifest central. |

## 6. Plan d'implémentation

- [ ] Étape 1 — Création de l'arborescence `core/`, `infrastructure/`, `presentation/`.
- [ ] Étape 2 — Migration du Repository Supabase (`repositories/knowledge_repository.py`).
- [ ] Étape 3 — Migration du Service d'Ingestion (`core/services/ingestion_service.py`).
- [ ] Étape 4 — Migration du Watchdog (`presentation/watchers/book_watcher.py`).

## 7. Questions ouvertes

- [ ] Souhaitez-vous conserver les imports globaux ou privilégier l'injection de dépendances ?
