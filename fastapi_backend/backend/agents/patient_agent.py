from typing import Dict, Any
import re
from utils.logging import get_logger

logger = get_logger(__name__)

class PatientAgent:
    """Simple rule-based PatientAgent that structures notes from patient messages."""
    def __init__(self):
        pass

    # PUBLIC_INTERFACE
    def process_message(self, session_id: str, content: str) -> Dict[str, Any]:
        """
        Process the patient's message, extract basic entities, and update structured notes.
        This is a simplified extractor; in production, use NLP/LLM with safety filters.
        """
        logger.info(f"Processing message for session {session_id}")
        notes = {
            "chief_complaint": self._extract_chief_complaint(content),
            "symptoms": self._extract_symptoms(content),
            "duration": self._extract_duration(content),
            "medications": self._extract_medications(content),
            "allergies": self._extract_allergies(content),
            "additional_context": content.strip(),
        }
        reply = self._generate_reply(notes)
        return {"reply": reply, "notes": notes}

    def _extract_chief_complaint(self, text: str) -> str:
        # naive heuristic: first sentence up to 100 chars
        sentence = re.split(r"[.!?]", text.strip())[0]
        return sentence[:100].strip()

    def _extract_symptoms(self, text: str) -> list[str]:
        keywords = ["fever", "cough", "pain", "nausea", "vomit", "headache", "fatigue", "sore throat", "shortness of breath"]
        found = [k for k in keywords if k in text.lower()]
        return list(set(found))

    def _extract_duration(self, text: str) -> str | None:
        m = re.search(r"(\d+)\s*(day|days|week|weeks|month|months)", text.lower())
        return m.group(0) if m else None

    def _extract_medications(self, text: str) -> list[str]:
        meds_markers = ["taking", "on", "using"]
        meds = []
        for mk in meds_markers:
            if mk in text.lower():
                # naive: take tokens after marker
                parts = text.lower().split(mk, 1)[-1]
                tokens = re.split(r"[,.]", parts)
                meds.extend([t.strip() for t in tokens if t.strip()])
        return meds[:5]

    def _extract_allergies(self, text: str) -> list[str]:
        if "allerg" in text.lower():
            seg = text.lower().split("allerg", 1)[-1]
            tokens = re.split(r"[,:;.]", seg)
            return [t.strip() for t in tokens if t.strip()][:5]
        return []

    def _generate_reply(self, notes: Dict[str, Any]) -> str:
        reply = "Thanks for sharing. I've noted your concerns. "
        if notes.get("symptoms"):
            reply += f"Reported symptoms include: {', '.join(notes['symptoms'])}. "
        if notes.get("duration"):
            reply += f"Duration mentioned: {notes['duration']}. "
        reply += "Please remember this service is informational and not a substitute for professional medical advice."
        return reply
