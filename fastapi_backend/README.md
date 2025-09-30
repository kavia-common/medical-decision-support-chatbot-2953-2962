# FastAPI Backend + React Template

This directory contains:
- A full FastAPI backend under `backend/`
- A lightweight React template under `src/` (optional UI)

Backend quickstart:
1) cd backend
2) cp .env.example .env  # fill in required vars for OneDrive if needed
3) python -m venv .venv && source .venv/bin/activate
4) pip install -r requirements.txt
5) uvicorn main:app --reload

Key endpoints:
- POST /chat
- POST /recommend
- GET /get_recommendation
- POST /upload_report
- POST /guidelines/upload
- POST /guidelines/query

Medical disclaimer:
This system provides information for educational purposes only and is not a substitute for professional medical advice. Always consult a qualified healthcare provider.

Environment variables:
See backend/.env.example for all required variables (OneDrive and vector store).

Frontend (React) notes:
- The UI now includes a minimal Chat panel that calls the FastAPI endpoints.
- Configure the API base URL by setting REACT_APP_API_BASE before starting:
  - Linux/macOS: REACT_APP_API_BASE=http://localhost:8000 npm start
  - Windows (PowerShell): set REACT_APP_API_BASE=http://localhost:8000 && npm start
- If not set, the UI defaults to http://localhost:8000.

Ocean Professional style:
The backend returns standardized disclaimers and safety warnings; the frontend can style them using the Ocean Professional theme: 
primary #2563EB, secondary #F59E0B, error #EF4444, background #f9fafb, surface #ffffff, text #111827.
