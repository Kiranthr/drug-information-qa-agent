# 💊 Drug Information Q&A Agent

> A professional, medical-grade Retrieval-Augmented Generation (RAG) system providing evidence-grounded drug answers strictly referenced from official regulatory documentation (FDA/DailyMed package inserts). Built for the Cognizant/GITAM Hackathon.

---

## 🌟 Key Features

- **Evidence-Grounded RAG:** Answers questions strictly using ingested official drug labels (FDA Package Inserts, DailyMed).
- **Verifiable Source Citations:** Every answer cites document titles, sections, and page numbers with extractable excerpts.
- **4-Shield Medical Safety Guardrails:**
  - **Emergency & Overdose Triage:** Immediate crisis detection with direct routing to Poison Control (1-800-222-1222) and emergency services (911/112).
  - **No Prescribing / Dosage Alteration Refusal:** Strict refusal to alter medication doses or prescribe, redirecting patients to licensed healthcare professionals.
  - **Uncertainty & Hallucination Gate:** Transparently reports when facts are absent from the document repository rather than fabricating answers.
  - **Universal Medical Disclaimer:** Transparent distinction between informational guidance and clinical medical advice.
- **6 Supported Initial Medicines:**
  1. **Amoxicillin** (Antibacterial)
  2. **Metformin** (Antidiabetic)
  3. **Paracetamol / Acetaminophen** (Analgesic / Antipyretic)
  4. **Atorvastatin** (Lipid-lowering / Statin)
  5. **Lisinopril** (ACE inhibitor / Antihypertensive)
  6. **Ibuprofen** (NSAID)
- **Document Ingestion Engine:** Dynamic PDF upload capability to expand the knowledge base to any new medicine with automatic semantic chunking and vector indexing.
- **Modern Responsive UI:** Built with React 18, Vite, Tailwind CSS, Lucide icons, and real-time citation cards.

---

## 🏗️ System Architecture

```
[ Frontend: React + Vite + Tailwind CSS ]
                  │
                  ▼  REST API (HTTP/JSON)
[ Backend: FastAPI (Python 3.11) ]
  ├── Medical Safety Guardrails Engine (Emergency / Dosage / Refusal)
  ├── RAG Retrieval Service (Query Analysis + Semantic Similarity)
  ├── Document Ingestion Engine (PyMuPDF + Semantic Chunker)
  └── LLM Provider Service (Google Gemini 2.5 Flash / Offline Fallback)
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
 [ SQLite Database ]    [ ChromaDB Vector Store ]
 (Medicines, Docs,      (Chunk Embeddings,
  Audit Logs, Sessions)   Page & Section Metadata)
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.11** (recommended for AI/ML library stability)
- **Node.js 18+** & **npm**
- **Google Gemini API Key** (optional; free from [Google AI Studio](https://aistudio.google.com/))

### 1. Backend Setup
```bash
# Navigate to backend and create virtual environment
py -3.11 -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
.\venv\Scripts\activate.bat

# Install dependencies
pip install -r backend/requirements.txt

# Configure environment variables
copy .env.example .env

# Run database & initial seed data script
python scripts/seed_database.py

# Start FastAPI backend
python backend/run_backend.py
```
Backend API will be live at `http://127.0.0.1:8000` with interactive Swagger docs at `http://127.0.0.1:8000/docs`.

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend will be live at `http://localhost:5173`.

---

## 🧪 Testing & Verification
```bash
# Run backend test suite (Safety guardrails, PDF parsing, RAG pipeline)
pytest backend/tests/ -v
```

---

## ⚖️ Medical Disclaimer
*This software is an informational tool created for educational and demonstration purposes. It does not provide medical advice, diagnosis, or treatment. Always seek the advice of a physician or qualified healthcare provider with any questions you may have regarding a medical condition or medication.*
