from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import settings
from app.models.schemas import ChatRequest, ProcessRequest
from app.rag.chunker import chunk_pages
from app.rag.embeddings import add_chunks, delete_document, list_documents
from app.rag.loader import PDFProcessingError, extract_pages
from app.rag.pipeline import answer
from app.utils.logger import get_logger

log = get_logger(__name__)
router = APIRouter()


@router.get("/health")
def health():
    return {
        "status": "ok",
        "llm_model": settings.llm_model,
        "embedding_model": settings.embedding_model,
        "documents_indexed": len(list_documents()),
    }


@router.post("/documents/upload")
def upload(file: UploadFile = File(...)):
    name = Path(file.filename or "").name
    if not name.lower().endswith(".pdf"):
        raise HTTPException(400, "Only .pdf files are accepted.")

    limit = settings.max_upload_mb * 1024 * 1024
    data = file.file.read(limit + 1)
    if len(data) > limit:
        raise HTTPException(413, f"File exceeds {settings.max_upload_mb} MB.")
    if not data.startswith(b"%PDF"):
        raise HTTPException(400, "File does not look like a valid PDF.")

    (settings.upload_dir / name).write_bytes(data)
    log.info(f"Uploaded {name} ({len(data)} bytes)")
    return {"filename": name, "size_bytes": len(data), "next": "POST /documents/process"}


@router.post("/documents/process")
def process(req: ProcessRequest):
    if req.filename:
        targets = [settings.upload_dir / Path(req.filename).name]
    else:
        targets = sorted(settings.upload_dir.glob("*.pdf"))

    if not targets or not all(t.exists() for t in targets):
        raise HTTPException(404, "PDF not found in uploads. Upload it first.")

    results = []
    for pdf in targets:
        try:
            pages = extract_pages(pdf)
            chunks = chunk_pages(pages, pdf.name, settings.chunk_size, settings.chunk_overlap)
            add_chunks(chunks)
            results.append({"filename": pdf.name, "pages": len(pages), "chunks": len(chunks)})
        except PDFProcessingError as e:
            raise HTTPException(422, str(e))
    return {"processed": results}


@router.get("/documents")
def documents():
    return {"documents": list_documents()}


@router.delete("/documents/{source}")
def remove(source: str):
    n = delete_document(source)
    if n == 0:
        raise HTTPException(404, f"No indexed document named '{source}'.")
    return {"deleted": source, "chunks_removed": n}


@router.post("/chat")
def chat(req: ChatRequest):
    try:
        return answer(req.question, req.top_k)
    except Exception as e:
        log.error(f"Chat failed: {e}")
        raise HTTPException(502, "The language model is unavailable. Is Ollama running?")
