# medical-decision-support-chatbot-2953-2962

This workspace contains the FastAPI backend under `fastapi_backend/backend`.

Backend quickstart:
- cd fastapi_backend/backend
- cp .env.example .env
- python -m venv .venv && source .venv/bin/activate
- pip install -r requirements.txt
- uvicorn main:app --reload

APIs:
- POST /chat
- POST /recommend
- GET /get_recommendation
- POST /upload_report
- POST /guidelines/upload
- POST /guidelines/query