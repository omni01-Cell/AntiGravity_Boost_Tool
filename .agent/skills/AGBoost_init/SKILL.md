---
name: AGBoost_init
description: Initialise chaque session de code en vérifiant et démarrant le pipeline AGBoost, en résolvant les conflits de connaissances (Cohomologie), et en restaurant le contexte persistant depuis .GCC/. À invoquer obligatoirement au tout début de chaque session selon la Rule 0.
---

# Skill : AGBoost Initialization & Knowledge Sync

<workflow_objective>
Garantir que le pipeline d'ingestion est actif, que les conflits de connaissances sont résolus et que le contexte historique (.GCC) est restauré avant toute intervention sur le code.
</workflow_objective>

## When to use this skill
- **OBLIGATOIREMENT** au début de chaque session (Rule 0).
- Avant toute décision technique ou lecture de code complexe.

## Workflow d'Initialisation (Gates)

<gate id="0" name="Rule Enforcement Sync">
  <instruction>
    S'assurer que le répertoire `.agent/rules/` existe et que `01_gcc_enforcement.md` est à jour depuis le répertoire du skill.
  </instruction>
  <verification>Le fichier est présent dans `.agent/rules/`.</verification>
  <fail_safe>Créer le dossier et copier le fichier si manquant.</fail_safe>
</gate>

<gate id="1" name="Pipeline AGBoost (Watchdog)">
  <instruction>
    Invoquer `ensure_watchdog_running` sur le serveur `antigravity-knowledge`.
  </instruction>
  <verification>`[AGBoost] Watchdog actif.`</verification>
  <fail_safe>Avertir l'utilisateur que l'ingestion automatique est suspendue.</fail_safe>
</gate>

<gate id="2" name="Synchronisation des Connaissances (Conflicts)">
  <instruction>
    Vérifier les items via `get_pending_items`. Si non vide, **INTERRUPTION OBLIGATOIRE**.
  </instruction>
  <verification>Aucun item en attente.</verification>
  <fail_safe>Demander une résolution (OVERWRITE, INSERT_BOTH, DISCARD) pour chaque conflit.</fail_safe>
</gate>

<gate id="3" name="Contexte Persistant (.GCC)">
  <instruction>
    Vérifier `.GCC/`. Lire `main.md` pour restaurer la feuille de route.
  </instruction>
  <verification>Historique et intention chargés.</verification>
  <fail_safe>Créer `.GCC/README.md` si absent pour expliquer le rôle du GCC.</fail_safe>
</gate>

<gate id="4" name="Rapport et Commandes">
  <instruction>Afficher le résumé d'initialisation et les commandes disponibles.</instruction>
  <verification>Résumé d'une ligne affiché.</verification>
</gate>

---

<instructions_specifiques>
- Le répertoire `.GCC` est votre mémoire à long terme.
- Utilisez `COMMIT` pour figer un raisonnement dans `log.md`.
- Utilisez `BRANCH` pour explorer une hypothèse sans polluer `main.md`.
</instructions_specifiques>

---

## Règle d'exécution
Ce skill est la fondation de la session. Si une étape échoue (ex: service non joignable), informez l'utilisateur mais ne bloquez pas le travail, sauf mention contraire explicite. 
La synchronisation de la règle GCC (Gate 0) doit être effectuée en priorité pour garantir la persistance du contexte.
