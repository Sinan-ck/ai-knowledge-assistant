from openai import OpenAI

from app.config import settings
from app.rag.embeddings import search
from app.utils.logger import get_logger

log = get_logger(__name__)

RELATIVE_CUTOFF = 0.7  # keep chunks scoring at least 70% of the best one
MIN_SCORE = 0.15  # below this, retrieval found nothing relevant
NO_ANSWER = "I couldn't find this information in the uploaded documents."

SYSTEM_PROMPT = (
    "You answer questions using ONLY the context provided. "
    "If the context does not contain the answer, reply exactly: "
    f"\"{NO_ANSWER}\" "
    "Be concise. Do not use outside knowledge. "
    "Mention the source file name in your answer when you use it."
)

_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)
    return _client


def _build_context(hits: list[dict]) -> str:
    parts = []
    for h in hits:
        m = h["metadata"]
        parts.append(f"[Source: {m['source']}, page {m['page']}]\n{h['text']}")
    return "\n\n---\n\n".join(parts)


def answer(question: str, top_k: int | None = None) -> dict:
    hits = search(question, top_k)
    good = [h for h in hits if h["score"] >= MIN_SCORE]

    if not good:
        log.info(f"No relevant chunks for: {question!r}")
        return {"answer": NO_ANSWER, "sources": [], "refused": True}

    best = good[0]["score"]
    good = [h for h in good if h["score"] >= best * RELATIVE_CUTOFF]
    user_prompt = f"Context:\n{_build_context(good)}\n\nQuestion: {question}\n\nAnswer:"
    try:
        resp = _get_client().chat.completions.create(
            model=settings.llm_model,
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        text = resp.choices[0].message.content.strip()
    except Exception as e:
        log.error(f"LLM call failed: {e}")
        raise

    sources = [
        {
            "source": h["metadata"]["source"],
            "page": h["metadata"]["page"],
            "score": h["score"],
            "snippet": h["text"][:200],
        }
        for h in good
    ]
    return {"answer": text, "sources": sources, "refused": NO_ANSWER in text}