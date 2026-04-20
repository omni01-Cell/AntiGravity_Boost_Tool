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
    1. Vérifier si AGBoost est déjà en cours d'exécution :
       - Chercher le fichier `agboost.pid` à la racine du projet.
       - Si le fichier existe, lire le PID et vérifier que le processus est actif (ex: `ps -p <PID>` sur Linux, ou `tasklist /FI "PID eq <PID>"` sur Windows).
       - Si le processus est actif → le pipeline tourne déjà, passer à la Gate 2.
    2. Si le processus n'est PAS actif (PID absent, fichier manquant, ou processus mort) :
       - Lancer le pipeline avec la commande :
         - **Linux** : `python agboost_cli.py start` (depuis la racine du projet)
         - **Windows** : `AGBoost.bat start`
       - Vérifier que le PID a été écrit dans `agboost.pid` et que le processus est vivant.
    3. Si le serveur MCP `antigravity-knowledge` est disponible, invoquer `ensure_watchdog_running` comme vérification complémentaire.
  </instruction>
  <verification>Le fichier `agboost.pid` existe et contient un PID d'un processus actif, OU la commande `start` a retourné `[OK]`.</verification>
  <fail_safe>Si le lancement échoue, avertir l'utilisateur que l'ingestion automatique est suspendue et continuer la session sans bloquer.</fail_safe>
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
