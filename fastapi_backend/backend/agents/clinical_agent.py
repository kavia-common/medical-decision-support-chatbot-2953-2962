from typing import Dict, Any, List
from utils.logging import get_logger
from services.rag_service import RAGService

logger = get_logger(__name__)

class ClinicalAgent:
    """ClinicalAgent that queries RAG store and produces simple test/treatment suggestions."""
    def __init__(self, rag_service: RAGService):
        self.rag = rag_service

    # PUBLIC_INTERFACE
    def generate_recommendations(self, notes: Dict[str, Any], query: str | None = None) -> Dict[str, Any]:
        """
        Use notes and optional query to retrieve top guideline references, then generate
        simple test/treatment suggestions with cautionary disclaimers.
        """
        text_context = " ".join([
            notes.get("chief_complaint") or "",
            " ".join(notes.get("symptoms") or []),
            notes.get("duration") or "",
            notes.get("additional_context") or ""
        ]).strip()

        retrieval_query = (query or text_context) or "general assessment"
        results = self.rag.query(retrieval_query, top_k=3)
        references = [r.get("source", "guideline") for r in results]

        suggestions: List[Dict[str, str]] = []
        symptoms = set([s.lower() for s in notes.get("symptoms", [])])

        if "fever" in symptoms:
            suggestions.append({"type": "test", "details": "CBC with differential", "rationale": "Evaluate infection/inflammation."})
            suggestions.append({"type": "test", "details": "Inflammatory markers (CRP/ESR)", "rationale": "Assess inflammatory response."})
        if "cough" in symptoms:
            suggestions.append({"type": "test", "details": "Chest X-ray", "rationale": "Assess pulmonary causes of cough."})
        if not suggestions:
            suggestions.append({"type": "other", "details": "Follow-up with primary care", "rationale": "General guidance based on limited data."})

        return {
            "recommendations": suggestions,
            "references": references
        }
