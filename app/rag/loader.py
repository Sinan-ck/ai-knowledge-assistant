import re
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from app.utils.logger import get_logger

log = get_logger(__name__)


class PDFProcessingError(Exception):
    """Raised when a PDF cannot be read or has no extractable text."""


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"-\n(\w)", r"\1", text)             # re-join words split across lines
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)       # single newline -> space, keep paragraph breaks
    text = re.sub(r"[ \t]+", " ", text)                # collapse spaces/tabs
    text = re.sub(r"\n{3,}", "\n\n", text)             # collapse blank lines
    return text.strip()


def extract_pages(pdf_path: Path) -> list[dict]:
 
    """Return [{'page': 1, 'text': '...'}, ...] for pages that contain text."""
    try:
        reader = PdfReader(str(pdf_path))
    except (PdfReadError, OSError) as e:
        raise PDFProcessingError(f"Could not read PDF '{pdf_path.name}': {e}")

    if reader.is_encrypted:
        raise PDFProcessingError(f"'{pdf_path.name}' is password protected.")

    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = clean_text(page.extract_text() or "")
        if text:
            pages.append({"page": i, "text": text})

    if not pages:
        raise PDFProcessingError(
            f"No text found in '{pdf_path.name}'. It may be a scanned image PDF."
        )

    log.info(f"Extracted {len(pages)} pages from {pdf_path.name}")
    return pages
