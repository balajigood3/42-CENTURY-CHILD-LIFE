import numpy as np
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL, TOP_K
from core.chunking import chunk_text

class KnowledgeBase:
    def __init__(self, documents=None, encoder=None):
        self.encoder = encoder or SentenceTransformer(EMBEDDING_MODEL)
        self.records = []
        for doc in documents or []:
            for part_no, chunk in enumerate(chunk_text(doc["text"])):
                self.records.append({
                    "source": doc["source"],
                    "part": part_no + 1,
                    "text": chunk
                })
        self.embeddings = None
        if self.records:
            vectors = self.encoder.encode(
                [r["text"] for r in self.records],
                normalize_embeddings=True
            )
            self.embeddings = np.asarray(vectors, dtype="float32")

    def search(self, query, top_k=None):
        if not self.records:
            return []
        vector = self.encoder.encode([query], normalize_embeddings=True)
        vector = np.asarray(vector, dtype="float32")[0]
        scores = self.embeddings @ vector
        order = np.argsort(scores)[::-1][:min(top_k or TOP_K, len(scores))]
        return [
            {**self.records[i], "similarity": float(scores[i])}
            for i in order
        ]
