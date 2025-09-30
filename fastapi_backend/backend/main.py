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
    description="FastAPI backend providing PatientAgent chat, ClinicalAgent recommendations, OneDrive/local storage, and RAG over uploaded guidelines. For informational purposes only.",
    version="1.0.0",
    openapi_tags=get_openapi_tags()
)

# CORS
settings = get_settings()
origins = settings.CORS_ALLOWED_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
