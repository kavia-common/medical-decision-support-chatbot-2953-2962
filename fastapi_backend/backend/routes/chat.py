from fastapi import APIRouter, HTTPException
from models.schemas import ChatRequest, ChatResponse
from agents.patient_agent import PatientAgent
from services.storage_service import StorageService
from utils.safety import add_disclaimers
from routes.recommendations import SESSION_NOTES

router = APIRouter()

patient_agent = PatientAgent()
storage = StorageService()

# PUBLIC_INTERFACE
@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Send a message in a chat session",
    description="Processes a patient message, updates structured notes, and stores session notes to OneDrive (with local fallback)."
)
async def chat(req: ChatRequest):
    """
    FastAPI entrypoint for chat.
    - session_id: string to group messages
    - message: role + content
    Returns PatientAgent reply and current notes; stores notes.
    """
    if not req.session_id or not req.message or not req.message.content:
        raise HTTPException(status_code=400, detail="session_id and message are required")

    result = patient_agent.process_message(req.session_id, req.message.content)
    # Update in-memory notes cache for recommendation flow
    SESSION_NOTES[req.session_id] = result["notes"]

    # Save notes to storage (OneDrive or local)
    await storage.save_session_notes(req.session_id, result["notes"])

    payload = {"session_id": req.session_id, "reply": result["reply"], "notes": result["notes"]}
    payload = add_disclaimers(payload)
    return payload
