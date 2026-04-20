# Current task context

## Objective
Installer les dépendances, transférer le skill dans le dossier global, et configurer le MCP pour AGBoost.

## Decisions made
- [2026-04-20] Réécriture de la Gate 1 pour inclure : vérification PID via `agboost.pid`, lancement via `agboost_cli.py start` / `AGBoost.bat start`, et conservation de l'appel MCP `ensure_watchdog_running` en optionnel.
- [2026-04-20] Création d'un virtual environment (`.venv`) pour installer les dépendances (système géré par Debian).
- [2026-04-20] Copie du skill `AGBoost_init` vers le dossier global `~/.gemini/skills/AGBoost_init/`.
- [2026-04-20] Configuration de `mcp_config.json` pour déclarer le serveur `antigravity-knowledge` via le python du `.venv`.

## Current status
- ✅ Done: Gate 1 corrigée dans `.agent/skills/AGBoost_init/SKILL.md`
- ✅ Done: Installation du plugin (dépendances Python installées dans `.venv`).
- ✅ Done: Transfert du skill dans `~/.gemini/skills/AGBoost_init/`.
- ✅ Done: Configuration du serveur MCP dans `~/.gemini/antigravity/mcp_config.json`.
- ✅ Done: Skills and workflows moved from Desktop to global directories.
- ✅ Done: Global `AGBoost_init` overwritten with the updated local version from `.agent/skills/`.
- ⏳ Pending: aucun

## Next action
Attente de la prochaine instruction.

## Abandoned branches
(aucune)

## Supabase chunks used
(aucun)
