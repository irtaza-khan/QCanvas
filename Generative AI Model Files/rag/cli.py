import os
import json
from typing import List

import typer
from rich.console import Console
from rich.markdown import Markdown

from .search import Retriever


app = typer.Typer()
console = Console()


def build_context_block(hits: List[dict], max_chars: int = 1600) -> str:
    out = []
    total = 0
    for h in hits:
        chunk = f"Source: {h.get('title','')} | {h.get('url','')}\n{h['text']}\n---\n"
        if total + len(chunk) > max_chars:
            break
        out.append(chunk)
        total += len(chunk)
    return "\n".join(out)


@app.command()
def ask(question: str, top_k: int = 5):
    """Retrieve top-k contexts for a question and print them for grounding."""
    index_path = os.environ.get("RAG_INDEX", "/workspace/rag/index/faiss.index")
    retriever = Retriever(index_path)
    hits = retriever.search(question, top_k=top_k)
    context = build_context_block(hits)
    console.print(Markdown(f"### Retrieved Contexts\n\n{context}"))


if __name__ == "__main__":
    app()



