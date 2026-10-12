# AI Agent Web Application

This project implements a complete AI Agent Web Application.

## Phase 2 Completed: AI Agent Core
The core AI Agent is implemented with:
- Gemini LLM integration via `google-genai` SDK
- Native Tool Calling (Calculator tool example)
- Memory and Context Management
- Extensible Tool Registry

### How to Run CLI
```bash
cd backend
python -m app.agent.cli
```

### How to Run Tests
```bash
cd backend
pytest tests/
```

### How to Run Evaluations
```bash
python preparation/evals/evaluate.py
```
