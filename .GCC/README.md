# Global Context Control (.GCC)

Ce répertoire contient la mémoire persistante de l'agent AntiGravity. Contrairement au contexte volatile d'une session de chat, le dossier `.GCC` assure une continuité logique sur le long terme.

## Structure
- `main.md` : Feuille de route globale et objectifs du projet.
- `branches/` : Raisonnements isolés pour des fonctionnalités spécifiques.
- `log.md` : Historique des décisions techniques majeures.

## Utilité
Le `.GCC` permet à n'importe quel agent de reprendre le travail exactement là où le précédent s'était arrêté. Il évite de répéter les mêmes questions et garantit que les standards d'architecture sont respectés à travers toutes les sessions.

## Maintenance
Le contenu de ce dossier est géré par l'agent via le skill `AGBoost_init`. Il ne doit pas être modifié manuellement sauf cas exceptionnel.
