import os
import json
from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from utils.config import get_settings
from utils.logging import get_logger

logger = get_logger(__name__)

class RAGService:
    """Simple RAG service backed by TF-IDF vectors with cosine similarity."""
    def __init__(self):
        self.settings = get_settings()
        self.path = self.settings.VECTOR_STORE_PATH
        os.makedirs(self.path, exist_ok=True)
        self.texts: List[str] = []
        self.sources: List[str] = []
        self.vectorizer: TfidfVectorizer | None = None
        self.matrix = None
        self._load()

    def _persist(self):
        with open(os.path.join(self.path, "store.json"), "w", encoding="utf-8") as f:
            json.dump({"texts": self.texts, "sources": self.sources}, f)

    def _load(self):
        fp = os.path.join(self.path, "store.json")
        if os.path.exists(fp):
            try:
                data = json.load(open(fp, "r", encoding="utf-8"))
                self.texts = data.get("texts", [])
                self.sources = data.get("sources", [])
                self._rebuild()
                logger.info(f"Loaded vector store with {len(self.texts)} chunks.")
            except Exception as e:
                logger.error(f"Failed to load vector store: {e}")

    def _rebuild(self):
        if self.texts:
            self.vectorizer = TfidfVectorizer(stop_words="english")
            self.matrix = self.vectorizer.fit_transform(self.texts)
        else:
            self.vectorizer = None
            self.matrix = None

    # PUBLIC_INTERFACE
    def add_documents(self, docs: List[Tuple[str, str]]) -> int:
        """
        Add a list of (text, source) tuples to the store.
        Returns number of chunks added.
        """
        count = 0
        for text, source in docs:
            chunks = self._chunk_text(text)
            for ch in chunks:
                self.texts.append(ch)
                self.sources.append(source)
                count += 1
        self._rebuild()
        self._persist()
        return count

    def _chunk_text(self, text: str, max_len: int = 800) -> List[str]:
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        chunks: List[str] = []
        for p in paragraphs:
            if len(p) <= max_len:
                chunks.append(p)
            else:
                # simple split by sentences
                sentences = [s.strip() for s in p.split(".") if s.strip()]
                buf = ""
                for s in sentences:
                    if len(buf) + len(s) + 1 <= max_len:
                        buf = (buf + " " + s).strip()
                    else:
                        if buf:
                            chunks.append(buf)
                        buf = s
                if buf:
                    chunks.append(buf)
        if not chunks and text:
            chunks = [text[:max_len]]
        return chunks

    # PUBLIC_INTERFACE
    def query(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Return top_k results with cosine similarity scores and sources."""
        if not self.texts or self.vectorizer is None or self.matrix is None:
            return []
        q_vec = self.vectorizer.transform([query])
        scores = (self.matrix @ q_vec.T).toarray().ravel()  # cosine proxy due to tf-idf normalization
        idxs = np.argsort(-scores)[:top_k]
        results = []
        for i in idxs:
            results.append({"text": self.texts[i], "score": float(scores[i]), "source": self.sources[i]})
        return results
