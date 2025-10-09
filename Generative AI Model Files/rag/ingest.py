import os
import re
import json
from pathlib import Path
from typing import List, Dict

from sentence_transformers import SentenceTransformer
import faiss


def split_into_chunks(text: str, max_chars: int = 1000, overlap: int = 150) -> List[str]:
    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + max_chars)
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
        if start < 0:
            start = 0
    return chunks


def load_documents(manifest_path: str) -> List[Dict]:
    with open(manifest_path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def build_faiss_index(chunks: List[Dict], model_name: str, index_path: str) -> None:
    model = SentenceTransformer(model_name)
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    faiss.normalize_L2(embeddings)
    index.add(embeddings)
    faiss.write_index(index, index_path)
    meta_path = Path(index_path).with_suffix(".meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False)


def main():
    data_dir = os.environ.get("RAG_DATA_DIR", "/workspace/data/seed")
    manifest = os.path.join(data_dir, "manifest.jsonl")
    out_dir = os.environ.get("RAG_INDEX_DIR", "/workspace/rag/index")
    os.makedirs(out_dir, exist_ok=True)
    index_path = os.path.join(out_dir, "faiss.index")

    model_name = os.environ.get("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    docs = load_documents(manifest)
    chunks: List[Dict] = []
    for d in docs:
        text = d.get("text", "")
        for i, ch in enumerate(split_into_chunks(text)):
            chunks.append({
                "id": f"{d.get('id','doc')}-{i}",
                "text": ch,
                "source": d.get("source"),
                "title": d.get("title"),
                "url": d.get("url"),
                "year": d.get("year"),
            })

    build_faiss_index(chunks, model_name, index_path)
    print(f"Built index at {index_path} with {len(chunks)} chunks")


if __name__ == "__main__":
    main()



