import os
import json
import time
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

from .search import Retriever


@dataclass
class EvalRecord:
    query: str
    sdk: str
    top_k: int
    latency_ms: float
    num_hits: int
    hits: List[Dict[str, Any]]


def load_seed_queries(path: str) -> List[Dict[str, str]]:
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def run_retrieval_eval(index_path: str, queries_path: str, top_k: int = 5) -> List[EvalRecord]:
    retriever = Retriever(index_path)
    queries = load_seed_queries(queries_path)
    records: List[EvalRecord] = []
    for q in queries:
        text = q.get("q", "").strip()
        sdk = q.get("sdk", "unknown")
        if not text:
            continue
        start = time.perf_counter()
        hits = retriever.search(text, top_k=top_k)
        latency_ms = (time.perf_counter() - start) * 1000.0
        records.append(
            EvalRecord(
                query=text,
                sdk=sdk,
                top_k=top_k,
                latency_ms=latency_ms,
                num_hits=len(hits),
                hits=[{
                    "rank": h["rank"],
                    "score": h["score"],
                    "citation": h.get("citation", ""),
                    "source": h.get("source"),
                    "url": h.get("url"),
                } for h in hits],
            )
        )
    return records


def save_eval(records: List[EvalRecord], out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(asdict(r), ensure_ascii=False) + "\n")


def main():
    index_path = os.environ.get("RAG_INDEX", os.path.join("rag", "index", "faiss.index"))
    queries_path = os.environ.get("RAG_QUERIES", os.path.join("data", "seed", "queries.jsonl"))
    out_path = os.environ.get("RAG_EVAL_OUT", os.path.join("rag", "eval_runs", "retrieval.jsonl"))
    top_k = int(os.environ.get("RAG_TOPK", "5"))
    records = run_retrieval_eval(index_path, queries_path, top_k=top_k)
    save_eval(records, out_path)
    print(f"Saved retrieval eval with {len(records)} queries to {out_path}")


if __name__ == "__main__":
    main()


