# FastAPI Backend - Medical Decision Support Chatbot

This backend provides REST APIs for:
- POST /chat: Patient chat session handling (PatientAgent)
- POST /recommend: Clinical recommendations generation (ClinicalAgent)
- GET /get_recommendation: Retrieve generated recommendations by session_id
- POST /upload_report: Upload and parse a medical report (PDF/TXT)
- POST /guidelines/upload: Upload medical guidelines documents into the vector store (RAG)
- POST /guidelines/query: Query over uploaded guidelines (RAG)

Architecture:
- agents/
  - patient_agent.py: Conversational logic and session note creation
  - clinical_agent.py: RAG-powered analysis and recommendations with disclaimers
- services/
  - storage_service.py: OneDrive integration with local fallback
  - rag_service.py: Simple vector DB service (Chroma-like in-memory) and embeddings
- routes/: FastAPI routes
- models/: Pydantic models
- utils/: helpers for logging, config, parsing, safety

OpenAPI docs are available at /docs and /openapi.json.

Environment:
- Uses .env variables for configuration; see .env.example for required settings.

Running:
- Install Python deps: pip install -r requirements.txt
- Start: uvicorn main:app --reload

Notes:
- This backend is independent from the React template present in this folder. The React content is a placeholder; API runs on FastAPI.
- Medical Safety: This system is for informational purposes only and is not a substitute for professional medical advice. See disclaimers in responses.

Ocean Professional Style:
- While primarily backend, response payloads include consistent disclaimers and styling notes for the frontend to reflect the Ocean Professional theme.
