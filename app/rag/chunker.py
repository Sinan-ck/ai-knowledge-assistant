from app.utils.logger import get_logger

log = get_logger(__name__)


def _find_cut(text: str, start: int, end: int) -> int:
    """Pick a natural cut point near `end` (paragraph > sentence > space)."""
    if end >= len(text):
        return len(text)
    window_start = start + int((end - start) * 0.6)  # only look in last 40%
    for sep in ("\n\n", "\n", ". ", " "):
        idx = text.rfind(sep, window_start, end)
        if idx != -1:
            return idx + len(sep)
    return end


def split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    if overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    chunks, start = [], 0
    while start < len(text):
        end = _find_cut(text, start, min(start + chunk_size, len(text)))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def chunk_pages(pages: list[dict], doc_name: str, chunk_size: int, overlap: int) -> list[dict]:
    chunks = []
    for p in pages:
        for piece in split_text(p["text"], chunk_size, overlap):
            chunks.append({
                "id": f"{doc_name}::p{p['page']}::c{len(chunks)}",
                "text": piece,
                "metadata": {
                    "source": doc_name,
                    "page": p["page"],
                    "chunk_index": len(chunks),
                },
            })
    log.info(f"Created {len(chunks)} chunks from {doc_name} (size={chunk_size}, overlap={overlap})")
    return chunks
