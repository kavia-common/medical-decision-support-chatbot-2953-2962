import os
import uuid
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from models.schemas import GuidelinesUploadResponse, GuidelinesQueryRequest, GuidelinesQueryResponse
from services.rag_service import RAGService
from utils.parsing import extract_text_from_file
from utils.safety import add_disclaimers

router = APIRouter()
rag = RAGService()

GUIDELINE_DIR = "./data/guidelines"
os.makedirs(GUIDELINE_DIR, exist_ok=True)

# PUBLIC_INTERFACE
@router.post(
    "/guidelines/upload",
    response_model=GuidelinesUploadResponse,
    summary="Upload medical guidelines",
    description="Uploads one or more guideline files (PDF/TXT) and indexes their content into the vector store."
)
async def upload_guidelines(files: List[UploadFile] = File(..., description="One or more guideline files")):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    added = 0
    indexed_names: List[str] = []
    for uf in files:
        ext = os.path.splitext(uf.filename)[1] or ""
        fname = f"{uuid.uuid4().hex}{ext}"
        path = os.path.join(GUIDELINE_DIR, fname)
        with open(path, "wb") as f:
            f.write(await uf.read())
        text, _ = extract_text_from_file(path, uf.content_type)
        chunks_added = rag.add_documents([(text, uf.filename)])
        added += chunks_added
        indexed_names.append(uf.filename)
    payload = {"files_indexed": indexed_names, "total_chunks": added}
    payload = add_disclaimers(payload)
    return payload

# PUBLIC_INTERFACE
@router.post(
    "/guidelines/query",
    response_model=GuidelinesQueryResponse,
    summary="Query uploaded guidelines",
    description="Queries the vector store and returns top results with scores and sources."
)
def query_guidelines(req: GuidelinesQueryRequest):
    results = rag.query(req.query, top_k=req.top_k)
    payload = {"query": req.query, "results": results}
    payload = add_disclaimers(payload)
    return payload
