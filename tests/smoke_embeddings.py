from pathlib import Path

from app.rag.chunker import chunk_pages
from app.rag.embeddings import add_chunks, list_documents, search
from app.rag.loader import extract_pages
from app.config import settings

for pdf in sorted(Path("data/sample_docs").glob("*.pdf")):
    chunks = chunk_pages(extract_pages(pdf), pdf.name, settings.chunk_size, settings.chunk_overlap)
    add_chunks(chunks)

print("\nDOCUMENTS:", list_documents())

for q in [
    "What is the refund policy?",
    "How much attendance do I need for placement assistance?",
    "Can I combine the early-bird discount with a scholarship?",
    "What is the capital of France?",
]:
    print(f"\nQ: {q}")
    for r in search(q, top_k=2):
        m = r["metadata"]
        print(f"  {r['score']:.3f} | {m['source']} p{m['page']} | {r['text'][:90]}...")