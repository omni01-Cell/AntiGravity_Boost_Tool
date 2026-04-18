# AntiGravity Boost Tool (Cognitive Memory RAG)

## 📌 Origine et Problématique
L'objectif est d'atteindre une qualité de code de niveau "Big Tech" en alimentant l'agent Antigravity avec un grand volume de connaissances issues de livres spécialisés (PDF, EPUB). Cependant, plusieurs limites se posent :
- **Goulot d'étranglement manuel** : Convertir tous ces livres en Markdown à la main brise le flux de développement "Zero-Touch".
- **Surcharge cognitive** : Saturer la mémoire (le contexte du LLM) avec des fichiers `SKILL.md` ou `.agent/rules/` contenant des informations massives ou temporaires détruit les performances et augmente la latence.
- **Besoin de classification stricte** : Il faut pouvoir sémantiquement séparer ce qui tient de la **Règle** architecturale absolue, du **Skill** actionnable ou de la **Connaissance Théorique** générale.

## 💡 Architecture de la Solution (L'Écosystème Automatisé)

Pour résoudre ces problèmes, l'architecture repose sur un Pipeline d'Ingestion couplé au protocole MCP, avec un modèle asymétrique spécifiquement conçu pour surpasser les limitations des LLMs (impossibilité de "push" serveur, et paresse cognitive).

### Phase 1 : Watchdog & Extraction (Ingestion Zero-Touch)
Un script Python local (Watchdog) surveille un dossier en arrière-plan. Tout nouveau document (PDF, EPUB) déposé déclenche une conversion automatique et propre via **Docling** (qui préserve parfaitement tableaux, code et formules).

### Phase 2 : Routage Sémantique Automatisé
Le Markdown brut passe par un LLM classificateur rapide qui juge et route l'information extraite en trois catégories :
- **Catégorie A - Règles (Standards Globaux)** : Formatées pour être placées dans `.agent/rules/` pour persistance.
- **Catégorie B - Skills (Méthodes Pratiques)** : Formatées en `SKILL.md`.
- **Catégorie C - Théorie (Connaissances Temporaires/Gros volumes)** : Transformées en `JSONL` et ingérées dans une base de données Vectorielle (Supabase) via un système hybride AssoMem.

### Phase 3 : Modèle "Meta-Skill" (Le Pull System pour contourner l'asymétrie)
Puisque le serveur (l'outil externe) ne peut pas écrire directement sur le Workspace du client (Antigravity), Antigravity doit s'auto-mettre à jour :
- Le serveur stocke les nouveaux Skills et Règles en attente.
- Antigravity possède un "Meta-Skill" (`knowledge-sync`) qui lui permet d'interroger le serveur (outil MCP `get_pending_items`), de télécharger les nouveautés, et de les écrire localement dans ses propres dossiers `.agent/`.

### Phase 4 : Prompting de Contrainte (Vaincre la Paresse Cognitive)
Par nature, un LLM a toujours tendance à puiser dans ses poids neuronaux statistiques plutôt que de faire l'effort d'utiliser un outil externe pour lire une DB. Pour l'obliger à utiliser le RAG :
- Une Règle d'ancrage stricte (`00_rag_enforcement.md`) établit une "barrière de validation mathématique". 
- La règle stipule qu'**avant** toute décision technique, il est **strictement interdit** à l'agent de se limiter à ses connaissances internes. Il a l'obligation procédurale d'invoquer une vérification via l'outil MCP de la base vectorielle.

## ✨ Sécurité et Amélioration Continue (LoopRAG)
1. **Zero-Trust Ingestion** : Prévenir les Injections de Prompt lors du scan des documents tiers via un Sanitizer à 3 niveaux (Regex & LLM).
2. **Cohomologie Cognitive** : L'IA détecte activement (en mode "Thinking") si un nouveau document ingéré apporte une règle qui *contredit* une règle existante, et le met en "pending" pour éviter la dissonance cognitive.
3. **Pondération Adaptative** : L'outil évalue à chaque utilisation la pertinence d'un fragment de savoir (Moyenne Mobile Exponentielle). Ce qui est utilisé survit, l'obsolète s’efface peu à peu (Fin du "Memory Fade").