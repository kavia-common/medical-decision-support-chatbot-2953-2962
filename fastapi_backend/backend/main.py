import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from routes.chat import router as chat_router
from routes.recommendations import router as rec_router
from routes.upload import router as upload_router
from routes.guidelines import router as guidelines_router
from utils.config import get_settings
from utils.logging import get_logger

# Initialize logger
logger = get_logger(__name__)

def get_openapi_tags():
    return [
        {"name": "Chat", "description": "Chat session endpoints with PatientAgent."},
        {"name": "Recommendations", "description": "ClinicalAgent recommendations and retrieval."},
        {"name": "Upload", "description": "Upload and parse medical reports."},
        {"name": "Guidelines", "description": "Upload and query medical guidelines for RAG."},
        {"name": "WebSocket", "description": "Reserved for future real-time features."}
    ]

app = FastAPI(
    title="Medical Decision Support Backend",
    description=(
        "FastAPI backend providing PatientAgent chat (/chat), ClinicalAgent recommendations, OneDrive/local storage, "
        "and RAG over uploaded guidelines. For informational purposes only."
    ),
    version="1.0.0",
    openapi_tags=get_openapi_tags()
)

# CORS
settings = get_settings()

# Start from env-provided origins if any
origins = list(settings.CORS_ALLOWED_ORIGINS or [])

# Always allow the Kavia preview frontend origin unless already present
kavia_frontend_origin = "https://vscode-internal-36118-beta.beta01.cloud.kavia.ai:4000"
if kavia_frontend_origin not in origins:
    origins.append(kavia_frontend_origin)

# If no origins are specified, default to the explicit Kavia origin only (avoid "*"
# when credentials are allowed to satisfy browser CORS requirements)
if not origins:
    origins = [kavia_frontend_origin]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # enable cookies/authorization headers if needed
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,
)

# Routers
app.include_router(chat_router, prefix="", tags=["Chat"])
app.include_router(rec_router, prefix="", tags=["Recommendations"])
app.include_router(upload_router, prefix="", tags=["Upload"])
app.include_router(guidelines_router, prefix="", tags=["Guidelines"])

@app.get("/", summary="Health check", description="Basic health check for the API. Returns status and a disclaimer.")
def root():
    return JSONResponse({
        "status": "ok",
        "service": "medical-decision-support-backend",
        "disclaimer": settings.MEDICAL_DISCLAIMER
    })

# PUBLIC_INTERFACE
@app.get("/websocket-info", summary="WebSocket usage help", description="This project may expose WebSocket endpoints in future releases for real-time chat. Currently, REST APIs are available.")
def websocket_info():
    return {"websocket": "No active WebSocket endpoints yet. Use REST APIs /chat, /recommend, /upload_report, /guidelines/*."}
