# Design Doc: SLM-V3 & LoopRAG Implementation

**Auteur :** Antigravity  
**Date :** 2026-04-18  
**Statut :** Draft  
**Reviewers :** USER

---

## 1. Contexte et problème

La théorie **SuperLocalMemory V3 (SLM-V3)** exige des mécanismes de recherche et de maintenance mémorielle bien plus avancés que ceux fournis par les systèmes RAG standards :
- **Métrique de Fisher** : Obligation d'utiliser la variance dimensionnelle pour le rappel sémantique au lieu de la simple similitude cosinus.
- **Dynamiques de Langevin** : Besoin d'une gestion organique de l'oubli basée sur l'énergie stochastique plutôt qu'un "Time Decay" linéaire.
- **Boucle PDCA (LoopRAG)** : Nécessité d'une auto-correction des recherches pour éviter les échecs de contexte.

## 2. Objectifs

- **Must-have** : Implémenter l'approximation de variance par Monte Carlo (3 variantes par chunk).
- **Must-have** : Basculer la recherche Supabase vers la distance riemannienne de Fisher.
- **Must-have** : Mettre en place un démon Python pour l'évolution Langevin de l'énergie des chunks.
- **Must-have** : Fermer la boucle de recherche avec un audit de qualité et un re-routage (PDCA).

## 3. Proposition de solution

### Métrique de Fisher ($G(\mu)$)
Comme les modèles d'embedding (Gemini) sont déterministes, nous générons $\sigma^2$ en :
1. Produisant 3 variantes du texte (Original, Paraphrase, Résumé) via LLM.
2. Calculant la variance des embeddings de ces 3 variantes.
3. Utilisant SQL pour calculer la distance : $\sum \frac{(\mu_q - \mu_k)^2}{\sigma_k^2 + \epsilon}$.

### Dynamiques de Langevin (Moteur d'Oubli)
L'énergie d'un chunk évolue selon : $d\mu = 0.5 \nabla \log p(\mu) dt + dW_t$.
En pratique : `energy += (0.5 * utility_gradient * dt) + brownian_noise`.
Le Watchdog gérera un thread démon qui met à jour l'énergie de chaque chunk périodiquement.

### LoopRAG (Cycle PDCA)
L'outil `find_knowledge` devient cyclique :
- **Plan** : MCPO (Monte Carlo Prompt Optimization) pour générer des variantes de query.
- **Do** : Recherche Fisher multi-variante.
- **Check** : Appel LLM furtif pour vérifier l'alignement (`_check_quality`).
- **Act** : Si échec, dégrader le score des chunks et reboucler avec une query augmentée.

## 4. Alternatives considérées

### Option A — Utilisation de la distance L2 standard (rejetée)
**Raison du rejet :** Ne capture pas la densité d'information locale requise par le SLM-V3.

### Option B — Entraînement d'un modèle d'embedding bayésien (rejetée)
**Raison du rejet :** Trop coûteux en ressources et temps. L'approximation Monte Carlo via LLM est plus agile.

## 5. Compromis et risques

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Latence (LoopRAG) | Élevée | Moyenne | Cache des embeddings et parallélisation des appels LLM. |
| Instabilité de l'énergie (Langevin) | Moyenne | Faible | Fixation de bornes strictes (énergie entre 0.1 et 1.5). |

## 6. Plan d'implémentation

- [ ] Étape 1 — Finalisation du service `EmbeddingService` avec calcul de variance.
- [ ] Étape 2 — Intégration du `LangevinEngine` dans le background service.
- [ ] Étape 3 — Refonte de `find_knowledge` pour supporter les phases PDCA.
- [ ] Étape 4 — Mise à jour des fonctions SQL `search_knowledge_fisher`.

## 7. Questions ouvertes

- [ ] Quel seuil de "bruit brownien" ($dW_t$) est acceptable pour ne pas perdre trop vite l'information importante ?
