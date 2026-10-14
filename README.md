# MediBot AI — Healthcare Information Assistant

MediBot AI is an educational healthcare information chatbot designed to provide accurate, safe, and reference-backed answers to general health, wellness, first aid, and medication awareness questions. It features a complete **Retrieval-Augmented Generation (RAG)** pipeline backed by **ChromaDB** and **Sentence Transformers**, along with built-in **emergency medical safety guardrails**.

> [!IMPORTANT]
> **Medical Safety Notice**: MediBot AI is strictly an educational tool. It does **not** provide clinical diagnosis, prognosis, or personalized treatment plans. In life-threatening emergencies, users are immediately directed to emergency services (e.g., 911 / 112).

---

## 🌟 Key Features

- **Educational Healthcare Q&A**: Answers questions regarding:
  - Common chronic diseases & evidence-based prevention (Type 2 Diabetes, Hypertension, Flu/Cold)
  - General symptoms and red flag indicators
  - Nutrition, hydration, restorative sleep, and physical exercise
  - Basic first aid protocols (minor burns, sprains R.I.C.E., minor cuts, epistaxis/nosebleeds)
  - General medication precautions, antibiotic stewardship, and analgesic safety
- **Emergency Safety Triage**: Automatically scans incoming queries for acute/life-threatening symptoms (e.g., crushing chest pain, anaphylaxis, stroke symptoms, respiratory distress) and outputs immediate emergency contact guidance without delay.
- **RAG Knowledge Retrieval**: Splits, embeds, and indexes trusted healthcare documents into **ChromaDB** using **Sentence Transformers** (`all-MiniLM-L6-v2`).
- **Source Attribution & Citations**: Every retrieved answer cites the verified source document name and page number.
- **Honest Uncertainty**: When reliable context is unavailable in the database, the bot explicitly communicates uncertainty rather than hallucinating medical facts or citations.
- **Multi-Provider AI Architecture**: Configurable to run with **Google Gemini**, **OpenAI**, **Hugging Face**, or in **Offline Extractive Mode** (runs completely locally with zero API keys required).
- **Document Ingestion Endpoint**: Upload and index permitted PDF or TXT files with file-type validation, size restrictions, and optional admin key security.
- **Containerized Deployment**: Ready to launch with Docker and Docker Compose.

---

## 🛠️ Tech Stack

- **Frontend**: HTML5, Vanilla CSS3 (Healthcare White & Teal theme), and Vanilla JavaScript
- **Backend**: Python 3.10, Flask
- **Vector Database**: ChromaDB (with local persistent storage)
- **Embeddings**: Sentence Transformers (`all-MiniLM-L6-v2`, 384-dimensional)
- **Document Extraction**: PyMuPDF (`fitz`) for PDF documents and UTF-8 text loader
- **Testing**: Pytest (20 unit and integration tests covering endpoints, safety, validation, and retrieval)
- **Containerization**: Docker & Docker Compose

---

## 📁 Repository Structure

```text
Ai-agent/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Flask app factory with vector store & LLM init
│   │   ├── config.py            # Environment configuration & limits
│   │   ├── safety.py            # Emergency detection & medical guardrails
│   │   ├── routes.py            # Endpoints: /chat, /documents, /health, /
│   │   ├── rag/
│   │   │   ├── chunking.py      # Document chunking with overlap
│   │   │   ├── document_loader.py # PDF and TXT text & page extraction
│   │   │   ├── retriever.py     # Similarity scoring & citation formatting
│   │   │   └── vector_store.py  # ChromaDB persistent client wrapper
│   │   └── llm/
│   │       ├── prompts.py       # Clinical safety system prompts
│   │       └── provider.py      # Multi-provider (Gemini/OpenAI/HF/Offline)
│   ├── static/
│   │   ├── css/style.css        # Clean White & Teal responsive styling
│   │   └── js/app.js            # Chatbot interaction, loading, citations
│   ├── templates/
│   │   └── index.html           # Single-page responsive chatbot interface
│   ├── uploads/                 # Temporary directory for uploaded files
│   ├── app.py                   # Server entrypoint
│   └── requirements.txt         # Python dependencies
├── knowledge_base/              # Reusable public health educational documents
│   ├── basic_first_aid.txt
│   ├── common_diseases_and_prevention.txt
│   ├── general_symptoms_and_causes.txt
│   ├── medication_safety_and_precautions.txt
│   └── nutrition_hydration_sleep_exercise.txt
├── finetuning/
│   ├── README.md                # Comprehensive RAG vs. Fine-tuning comparison
│   └── lora_finetune_example.py # Lightweight PEFT / LoRA fine-tuning demo script
├── tests/
│   ├── conftest.py              # Pytest configuration and fixtures
│   ├── test_chat_validation.py  # Input sanitization and size limits
│   ├── test_document_upload.py  # File type, size, and admin authorization tests
│   ├── test_emergency_detection.py # Acute symptom triage tests
│   ├── test_health.py           # Health endpoint and secret-leak checks
│   ├── test_provider_fallback.py # Offline mode and uncertainty handling
│   └── test_retrieval.py        # Vector search and citation tests
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10+
- Git
- Docker & Docker Compose (optional, for containerized run)

### 2. Environment Setup
Clone the repository and copy the example environment configuration:
```bash
git clone https://github.com/prathapanijayasri/Ai-agent.git
cd Ai-agent
cp .env.example .env
```

Install python dependencies:
```bash
pip install -r backend/requirements.txt
```

### 3. Configuring the AI Provider (Optional)
By default, MediBot AI operates in **Offline Extractive Mode** (`LLM_PROVIDER=auto` or `offline`). It synthesizes verified knowledge directly from the local ChromaDB database with zero external API fees or internet dependencies.

If you wish to use a cloud LLM, update `.env`:
- **Google Gemini**: Set `GEMINI_API_KEY=your_key`
- **OpenAI**: Set `OPENAI_API_KEY=your_key`
- **Hugging Face**: Set `HUGGINGFACE_API_KEY=your_key`

### 4. Running Locally
Start the Flask application:
```bash
python backend/app.py
```
Open your web browser and navigate to:
```
http://localhost:5000
```
*(On initial launch, MediBot AI automatically indexes all sample healthcare guides from `knowledge_base/` into ChromaDB).*

---

## 🐳 Docker Deployment

The application includes a production-ready Dockerfile and Docker Compose configuration with persistent volume mapping for ChromaDB.

### Start Application with Docker Compose:
```bash
docker compose up --build
```

### Stop the Container:
```bash
docker compose down
```

The ChromaDB vector index is persistently preserved in the `chroma_data` Docker volume across restarts.

---

## 🧪 Running Automated Tests

A comprehensive test suite of 20 tests verifies application health, safety guardrails, input validation, upload security, and retrieval:

```bash
python -m pytest -v
```

Expected output:
```text
tests/test_chat_validation.py::test_chat_empty_payload PASSED
tests/test_chat_validation.py::test_chat_empty_message PASSED
tests/test_chat_validation.py::test_chat_oversized_message PASSED
tests/test_chat_validation.py::test_chat_valid_message PASSED
tests/test_document_upload.py::test_document_upload_unauthorized PASSED
tests/test_document_upload.py::test_document_upload_success_with_key PASSED
tests/test_document_upload.py::test_document_upload_invalid_extension PASSED
tests/test_emergency_detection.py::test_emergency_symptoms_flagged[...] PASSED (6 cases)
tests/test_emergency_detection.py::test_emergency_endpoint_response PASSED
tests/test_health.py::test_health_endpoint_success PASSED
tests/test_health.py::test_health_endpoint_does_not_leak_secrets PASSED
tests/test_provider_fallback.py::test_offline_provider_fallback_with_context PASSED
tests/test_provider_fallback.py::test_offline_provider_honest_uncertainty PASSED
tests/test_retrieval.py::test_retrieval_finds_relevant_knowledge PASSED
tests/test_retrieval.py::test_retrieval_flags_unreliable_for_out_of_domain PASSED
======================= 20 passed =======================
```

---

## 📡 API Endpoints

### 1. `POST /chat`
Answers healthcare inquiries using emergency triage and RAG retrieval.
- **Request**:
  ```json
  {
    "message": "What is the recommended daily water intake for adults?"
  }
  ```
- **Response**:
  ```json
  {
    "response": "...",
    "is_emergency": false,
    "reliable_context": true,
    "sources": [
      {
        "source": "nutrition_hydration_sleep_exercise.txt",
        "page": 1,
        "snippet": "General guideline: Approximately 2.0 to 2.5 liters of fluid per day..."
      }
    ],
    "provider": "Extractive RAG (Offline Mode)"
  }
  ```

### 2. `POST /documents`
Uploads and indexes permitted healthcare documents (`.pdf` or `.txt`, max 10MB).
- **Headers**: `X-Admin-Key: <ADMIN_API_KEY>` *(if configured)*
- **Body**: `multipart/form-data` with `file`
- **Response**:
  ```json
  {
    "success": true,
    "filename": "clinical_guideline.pdf",
    "chunks_ingested": 14,
    "total_indexed_chunks": 42
  }
  ```

### 3. `GET /health`
Reports service status without exposing keys or internal secrets:
- **Response**:
  ```json
  {
    "status": "healthy",
    "service": "MediBot AI — Healthcare Information Assistant",
    "version": "1.0.0",
    "indexed_chunks": 28,
    "llm_provider": "Extractive RAG (Offline Mode)"
  }
  ```

---

## 🔬 Model Adaptation: RAG vs. Fine-Tuning

| Feature | RAG (Active in MediBot AI) | Fine-Tuning (LoRA Example) |
| :--- | :--- | :--- |
| **Model Weights** | Unchanged (Frozen) | Low-rank adapter weights adjusted |
| **Source Attribution** | Direct document name & page number | No native source citation |
| **Updating Knowledge** | Instant (add/replace file in database) | Requires new dataset & re-training |
| **Hallucination Risk** | Minimized (grounded in context) | Moderate (can confabulate facts) |
| **Compute Requirements** | Runs on commodity CPU | GPU recommended for training |

To view the educational LoRA fine-tuning script:
```bash
python finetuning/lora_finetune_example.py
```
*(See [finetuning/README.md](file:///c:/Users/mahes/Ai-agent/finetuning/README.md) for full architectural trade-offs).*

---

## 🌿 Git & GitHub Workflow

Follow standard Git practices when working with this repository:

1. **Check branch status**:
   ```bash
   git status
   git branch
   ```
2. **Create a feature branch**:
   ```bash
   git checkout -b feat/your-feature-name
   ```
3. **Commit changes with descriptive messages**:
   ```bash
   git add .
   git commit -m "feat: your concise commit message"
   ```
4. **Push branch to GitHub**:
   ```bash
   git push origin feat/your-feature-name
   ```
5. **Open a Pull Request (PR)**:
   - Navigate to the repository on GitHub (`https://github.com/prathapanijayasri/Ai-agent`).
   - Click **Compare & pull request**.
   - Review differences, provide a summary of changes, and submit for peer review.

---

## ⚠️ Limitations & Medical Safety

1. **No Patient Diagnosis**: MediBot AI cannot review lab results, diagnose complex conditions, or provide individualized medical opinions.
2. **Prescription Integrity**: MediBot AI will never advise changing, discontinuing, or altering prescribed medication dosages.
3. **Emergency Situations**: For acute chest pain, stroke symptoms, uncontrolled bleeding, poisoning, or severe difficulty breathing, immediately contact your local emergency services (911 / 999 / 112).
4. **Data Privacy**: Uploaded documents should not contain Personally Identifiable Information (PII) or Protected Health Information (PHI).
