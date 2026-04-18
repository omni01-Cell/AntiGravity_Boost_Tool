# AntiGravity Boost Tool 🚀
### Cognitive Memory RAG (SLM-V3 Architecture)

AntiGravity Boost Tool is an autonomous knowledge ingestion and synchronization pipeline designed to bridge the gap between static documentation (PDF, EPUB) and agentic AI systems. It implements a **Zero-Touch** workflow that converts, classifies, and stores expert knowledge into a vector database while managing cognitive consistency (Cohomology) and memory decay (Langevin Dynamics).

## 💡 Key Features

- **Zero-Touch Ingestion**: Background watchdog monitors document drops and automates the entire extraction pipeline.
- **Cognitive Routing**: Intelligent classification of knowledge into **Rules** (Global Standards), **Skills** (Practical Methods), or **Theory** (AssoMem Hybrid RAG).
- **Secure by Design**: Three-level Zero-Trust sanitizer to prevent prompt injection during document parsing.
- **Cohomology Classifier**: Active detection of rule contradictions before ingestion to prevent "cognitive dissonance".
- **Dynamic Memory**: Adaptive weighting (EMA) and stochastic decay to prioritize active knowledge and phase out obsolete theory.

## 🏗️ Architecture

1. **Watchdog (Python)**: Real-time filesystem observer using `watchdog` and `Docling` for high-fidelity extraction.
2. **Classifier (GenAI)**: Semantic router that formats data for the specific needs of an agentic assistant.
3. **Storage (Supabase/PostgreSQL)**: `pgvector` backend with custom Fisher Information metrics for high-precision retrieval.
4. **MCP Server**: Gateway for AI agents to query, rate, and sync knowledge.

## 🚀 Quick Start

### Installation

```powershell
# Clone the repository
git clone https://github.com/YOUR_USERNAME/AntiGravity_Boost_Tool.git
cd AntiGravity_Boost_Tool

# Setup environment
cp .env.example .env
# Edit .env with your Supabase and Gemini API keys
```

### Running the Pipeline

To start the automated background ingestion service:

```powershell
./AGBoost.bat start
```

Drop any PDF or EPUB file into the `books/` directory. The system will process it automatically.

---

## 🇫🇷 Origine du Projet

Né du besoin de saturer l'agent Antigravity avec un volume massif de connaissances théoriques sans briser le "flux de développement", cet outil automatise la transformation de livres spécialisés en savoir actionnable pour l'IA.

## ⚖️ License

Apache 2.0
