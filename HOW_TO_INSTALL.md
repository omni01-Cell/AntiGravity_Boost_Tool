# AntiGravity Boost Tool - Installation Guide

Welcome to the AntiGravity Boost Tool development environment. This guide will help you get the system up and running in a few simple steps.

## 1. Prerequisites
- **Python 3.10+** (Recommended: 3.14 for development)
- **Supabase Account**
- **API Keys**:
    - `GEMINI_API_KEY` (Google AI)
    - `SUPABASE_URL` & `SUPABASE_KEY`
    - `DOCSTRANGE_API_KEY` (Document extraction)

## 2. Quick Setup

### Step 1: Clone and Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 2: Configure Environment
Create a `.env` file at the root of the project:
```env
SUPABASE_URL=your_url
SUPABASE_KEY=your_service_role_key
GEMINI_API_KEY=your_key
DOCSTRANGE_API_KEY=your_key
```

### Step 3: Database Initialization
Execute the entire content of [infrastructure/repositories/sql/DB.sql](infrastructure/repositories/sql/DB.sql) in your Supabase SQL Editor. This will:
- Enable the `vector` extension.
- Create the `knowledge_chunks` table.
- Deploy the SLM-V3 search and energy management functions.

## 3. Running the System

To start the automated ingestion service (Watchdog):
```powershell
.\AGBoost.bat start
```

To stop the service:
```powershell
.\AGBoost.bat stop
```

To run a manual ingestion check:
```powershell
py agboost_cli.py ingest
```

## 4. Agent Integration (Mandatory for Portability)

To enable the cognitive alignment of an AI agent (like Antigravity) on this project, you must import the rules and skills provided in the `.agent` directory.

### Step 4.1: Import Rules
Copy the content of [.agent/rules/rule_zero.md](.agent/rules/rule_zero.md) and [.agent/rules/# RAG Enforcement — Cognitive Memory Sys.md](.agent/rules/%23%20RAG%20Enforcement%20%E2%80%94%20Cognitive%20Memory%20Sys.md) into your agent's global rule file (e.g., `GEMINI.md` or system instructions).

### Step 4.2: Import Skills
Copy the directory [.agent/skills/AGBoost_init/](.agent/skills/AGBoost_init/) into your agent's global skills directory (e.g., `~/.gemini/antigravity/skills/`).

### Step 4.3: Absolute Rule 0
Once imported, the agent will automatically comply with **Rule 0**: every session will start with the `AGBoost_init` skill to synchronize its knowledge and resume its session context from [.GCC/](.GCC/).

---

For more details on the architecture and persistent memory system, refer to:
- [.agent/README.md](.agent/README.md)
- [.GCC/README.md](.GCC/README.md)
- [docs/recherche.md](docs/recherche.md)
