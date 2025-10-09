import json
import os
from typing import List, Dict, Tuple, Optional

import faiss
from sentence_transformers import SentenceTransformer
import numpy as np


class Retriever:
    def __init__(self, index_path: str, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        self.index = faiss.read_index(index_path)
        self.model = SentenceTransformer(model_name)
        meta_path = os.path.splitext(index_path)[0] + ".meta.json"
        with open(meta_path, "r", encoding="utf-8") as f:
            self.meta = json.load(f)

    def _format_citation(self, meta: Dict) -> str:
        title = meta.get("title", "") or "Untitled"
        url = meta.get("url", "") or ""
        year = meta.get("year")
        if year is None:
            return f"{title} {url}".strip()
        return f"{title} ({year}) {url}".strip()

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        emb = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(emb)
        scores, idxs = self.index.search(emb, top_k)
        results: List[Dict] = []
        for rank, (score, idx) in enumerate(zip(scores[0], idxs[0])):
            if idx == -1:
                continue
            meta = self.meta[idx]
            results.append({
                "rank": rank,
                "score": float(score),
                "text": meta["text"],
                "source": meta.get("source"),
                "title": meta.get("title"),
                "url": meta.get("url"),
                "year": meta.get("year"),
                "citation": self._format_citation(meta),
            })
        return results


def demo():
    index_path = os.environ.get("RAG_INDEX", "/workspace/rag/index/faiss.index")
    retriever = Retriever(index_path)
    while True:
        try:
            q = input("query> ").strip()
            if not q:
                continue
            hits = retriever.search(q, top_k=5)
            for h in hits:
                print(f"[{h['score']:.3f}] {h.get('title','')} - {h.get('url','')}")
                print(h["text"][:300].replace("\n"," ") + "...")
                print()
        except (EOFError, KeyboardInterrupt):
            break


if __name__ == "__main__":
    demo()



