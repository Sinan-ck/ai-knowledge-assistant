import chromadb
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.utils.logger import get_logger

log = get_logger(__name__)

_model = None
_collection = None


def _get_model() -> SentenceTransformer:
    """Load the embedding model once (first call downloads it)."""
    global _model
    if _model is None:
        log.info(f"Loading embedding model {settings.embedding_model}")
        _model = SentenceTransformer(settings.embedding_model)
    return _model


def _get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=str(settings.chroma_dir))
        _collection = client.get_or_create_collection(
            name="documents", metadata={"hnsw:space": "cosine"}
        )
    return _collection


def _embed(texts: list[str]) -> list[list[float]]:
    return _get_model().encode(texts, normalize_embeddings=True).tolist()


def add_chunks(chunks: list[dict]) -> int:
    """Store chunks. Re-processing a document replaces its old chunks."""
    if not chunks:
        return 0
    col = _get_collection()

    for source in {c["metadata"]["source"] for c in chunks}:
        delete_document(source)

    col.add(
        ids=[c["id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        embeddings=_embed([c["text"] for c in chunks]),
        metadatas=[c["metadata"] for c in chunks],
    )
    log.info(f"Stored {len(chunks)} chunks")
    return len(chunks)


def search(query: str, top_k: int | None = None) -> list[dict]:
    """Return the top_k most similar chunks with a 0-1 similarity score."""
    col = _get_collection()
    if col.count() == 0:
        return []
    k = min(top_k or settings.top_k, col.count())
    res = col.query(query_embeddings=_embed([query]), n_results=k)
    return [
        {"text": doc, "metadata": meta, "score": round(1 - dist, 4)}
        for doc, meta, dist in zip(
            res["documents"][0], res["metadatas"][0], res["distances"][0]
        )
    ]


def list_documents() -> list[dict]:
    """Return [{'source': 'file.pdf', 'chunks': 3}, ...]."""
    metas = _get_collection().get(include=["metadatas"])["metadatas"]
    counts: dict[str, int] = {}
    for m in metas:
        counts[m["source"]] = counts.get(m["source"], 0) + 1
    return [{"source": s, "chunks": n} for s, n in sorted(counts.items())]


def delete_document(source: str) -> int:
    col = _get_collection()
    ids = col.get(where={"source": source})["ids"]
    if ids:
        col.delete(ids=ids)
        log.info(f"Deleted {len(ids)} chunks of {source}")
    return len(ids)