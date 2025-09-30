from typing import Tuple
from pdfminer.high_level import extract_text

# PUBLIC_INTERFACE
def extract_text_from_file(file_path: str, content_type: str | None = None) -> Tuple[str, str]:
    """
    Extract text from uploaded file. Supports PDF or plain text.
    Returns (extracted_text, detected_type)
    """
    if content_type and "pdf" in content_type.lower():
        text = extract_text(file_path) or ""
        return text, "pdf"
    # fallback: try pdf by extension
    if file_path.lower().endswith(".pdf"):
        text = extract_text(file_path) or ""
        return text, "pdf"
    # otherwise treat as text
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read(), "text"
