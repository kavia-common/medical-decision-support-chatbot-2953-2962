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
    description=(
        "Processes a patient message, updates structured notes, and stores session notes to OneDrive (with local fallback). "
        "Use this endpoint by POSTing JSON: { 'session_id': 'abc123', 'message': { 'role': 'patient', 'content': 'text' } }."
    ),
    operation_id="post_chat_message"
)
async def chat(req: ChatRequest):
    """
    FastAPI entrypoint for chat.

    Request body:
    - session_id (str): unique identifier grouping the user session
    - message (object):
        - role (str): sender role, e.g., 'patient'
        - content (str): message text from the patient

    Returns:
    - ChatResponse: {
        "session_id": str,
        "reply": str,       # assistant reply message
        "notes": dict       # structured notes extracted from the message
      }
      The response also includes standardized "disclaimer" and "safety_warnings" fields.

    Notes:
    - This route is asynchronous and persists structured notes using the configured storage provider.
    - Ensure clients call the FastAPI server base URL (e.g., http://localhost:8000/chat). If you see "Cannot POST /chat",
      it likely means the request went to a frontend dev server or preview proxy instead of FastAPI.
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
