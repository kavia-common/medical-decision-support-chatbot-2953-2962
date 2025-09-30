from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from models.schemas import RecommendationRequest, RecommendationResponse, RecommendationItem
from agents.clinical_agent import ClinicalAgent
from services.rag_service import RAGService
from utils.safety import add_disclaimers

router = APIRouter()

rag = RAGService()
clinical_agent = ClinicalAgent(rag)

# In-memory session notes cache for demonstration; in production use a DB
SESSION_NOTES: dict[str, dict] = {}

# PUBLIC_INTERFACE
@router.post(
    "/recommend",
    response_model=RecommendationResponse,
    summary="Generate clinical recommendations",
    description="Generates suggestions for tests/treatments using ClinicalAgent and RAG over guidelines. Includes proper disclaimers."
)
def recommend(req: RecommendationRequest):
    """
    FastAPI entrypoint to generate recommendations.
    Parameters:
    - session_id: string
    - query: optional string
    Returns list of RecommendationItems and references
    """
    notes = SESSION_NOTES.get(req.session_id, {})
    result = clinical_agent.generate_recommendations(notes, req.query)
    payload = {
        "session_id": req.session_id,
        "recommendations": [RecommendationItem(**r).dict() for r in result["recommendations"]],
        "references": result["references"]
    }
    payload = add_disclaimers(payload)
    return payload

# PUBLIC_INTERFACE
@router.get(
    "/get_recommendation",
    response_model=RecommendationResponse,
    summary="Retrieve last recommendations for a session",
    description="Returns the last generated recommendations for a given session_id."
)
def get_recommendation(session_id: str = Query(..., description="Session identifier")):
    """
    Fetch previously generated recommendations for a session. Here we re-generate
    based on current notes cache for demonstration purposes.
    """
    notes = SESSION_NOTES.get(session_id, {})
    result = clinical_agent.generate_recommendations(notes, None)
    payload = {
        "session_id": session_id,
        "recommendations": result["recommendations"],
        "references": result["references"]
    }
    payload = add_disclaimers(payload)
    return payload
