import os
import uuid
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from models.schemas import ReportUploadResponse
from utils.parsing import extract_text_from_file
from utils.safety import add_disclaimers
from services.rag_service import RAGService
from routes.recommendations import SESSION_NOTES

router = APIRouter()
rag = RAGService()

UPLOAD_DIR = "./data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# PUBLIC_INTERFACE
@router.post(
    "/upload_report",
    response_model=ReportUploadResponse,
    summary="Upload and analyze a medical report",
    description="Uploads a medical report (PDF/TXT), extracts text, and appends to session notes for subsequent analysis."
)
async def upload_report(
    file: UploadFile = File(..., description="Medical report file (PDF/TXT)"),
    session_id: str = Form(..., description="Session identifier")
):
    """
    Upload endpoint for medical reports.
    - Saves file
    - Extracts text
    - Updates in-memory session notes cache for demo purposes
    """
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")
    ext = os.path.splitext(file.filename)[1] or ""
    fname = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(UPLOAD_DIR, fname)
    with open(path, "wb") as f:
        f.write(await file.read())

    text, dtype = extract_text_from_file(path, file.content_type)
    # Update session notes
    notes = SESSION_NOTES.get(session_id, {})
    notes["report_text"] = (notes.get("report_text", "") + "\n" + text).strip() if text else notes.get("report_text")
    SESSION_NOTES[session_id] = notes

    payload = add_disclaimers({
        "session_id": session_id,
        "filename": file.filename,
        "extracted_text": text[:5000]  # limit size in response
    })
    return payload
