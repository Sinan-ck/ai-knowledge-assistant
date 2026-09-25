# AI Knowledge Assistant 

A RAG (Retrieval-Augmented Generation) system that answers questions from a set of PDF documents, with grounded answers, source citations, and hallucination control. Built as a machine test for the AI Engineering Intern role at Acadeno Technologies.

## Demo Video
[Watch the Demo video](https://drive.google.com/file/d/1wkJfT0WgW3tRYCZICw7fBW-IMJSniB67/view?usp=drivesdk)

## 1. Problem

Given a collection of PDFs (course brochures, fee sheets, FAQs, placement reports), build an assistant that answers questions using only the supplied documents, cites its sources, and clearly says "not found" when the answer isn't present — rather than inventing an answer.

## 2. Architecture

See `architecture.svg` for the full diagram. In short:
PDF → extract (pypdf) → clean → chunk (per page, size=800, overlap=150)
→ embed (all-MiniLM-L6-v2) → store (ChromaDB, persistent)

Query → embed → similarity search (top_k=4) → score filter
→ LLM (Ollama, llama3.2:3b) → grounded answer + citations
→ (or "not found" if no chunk passes the score filter)

## 3. Technology Choices

| Component | Choice | Why |
|---|---|---|
| Backend | FastAPI | Async, automatic OpenAPI docs, Pydantic validation |
| PDF extraction | pypdf | Lightweight, page-level extraction needed for citations |
| Embeddings | `sentence-transformers` (`all-MiniLM-L6-v2`) | Free, local, fast, good enough quality for this scale |
| Vector store | ChromaDB (persistent, on-disk) | Simple to run locally, no external service needed |
| LLM | Ollama, `llama3.2:3b`, via OpenAI-compatible SDK | Runs fully offline — no API key, no cost, no data leaves the machine. The app talks to it through the standard `openai` Python client (just pointing `base_url` at Ollama), so swapping in a hosted model (Grok, Gemini, OpenAI) later only means changing three environment variables |

**Note on LLM choice:** the original plan was to use the Grok API, but the available account had no credits (see `.env.example` — the code is provider-agnostic via `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL`, so any OpenAI-compatible endpoint works, including Grok, Gemini, or Groq, with no code changes).

## 4. Chunking Strategy

Chunking happens **per page**, not on the whole document, so every chunk keeps an exact page number for citation. Within a page, the splitter cuts at the nearest paragraph break, then sentence break, then space — never mid-word. Consecutive chunks overlap by 150 characters so an answer near a chunk boundary isn't lost.

Chunk size (800) and overlap (150) are configurable via `.env` — see Section 8 for a comparison against an alternative configuration.

## 5. Hallucination Control

Every retrieved chunk gets a similarity score. Two filters run before a chunk is allowed into the LLM's context:

- **`MIN_SCORE`** — an absolute floor a chunk's similarity score must clear.
- **`RELATIVE_CUTOFF`** — chunks scoring far below the best match in this query are dropped even if they clear `MIN_SCORE`, so a mediocre match doesn't get treated as ground truth.

If **no chunk passes both filters**, the pipeline skips the LLM call entirely and returns a fixed "not found in the provided documents" response — the model is never given a chance to guess from an empty or irrelevant context. The system prompt also explicitly instructs the LLM to answer only from the provided context and say so if the answer isn't there, as a second layer of defense.

### Bug found and fixed during evaluation

One evaluation question ("What is the early-bird discount?") initially failed. Investigation showed the correct chunk was being retrieved from ChromaDB (score 0.2495) but was being silently dropped because `MIN_SCORE` was set to 0.25 — the chunk missed the floor by 0.005. This was confirmed with a raw similarity query against the vector store, isolating the bug to the filter, not extraction or chunking (see `evaluation/check_threshold.py`).

**Fix:** lowered `MIN_SCORE` from 0.25 to 0.15, relying on `RELATIVE_CUTOFF` (0.7) to still filter out genuinely irrelevant chunks. Re-running the full evaluation suite after the fix brought the score from 17/18 to 18/18, with no new false positives on the negative test questions.

## 6. API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/documents/upload` | Upload a PDF |
| POST | `/documents/process` | Extract, chunk, embed, and index an uploaded PDF |
| POST | `/chat` | Ask a question; returns a grounded answer with source citations |
| GET | `/documents` | List indexed documents |
| GET | `/health` | Health/status check |

Interactive API docs are available at `http://localhost:8000/docs` once the server is running.

### Example: `/chat`

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the early-bird discount?"}'
```

```json
{
  "answer": "The early-bird discount is 10 percent on tuition, for students who pay the full fee before 15 December 2026.",
  "sources": [
    {"document": "02_fee_structure.pdf", "page": 2}
  ]
}
```

## 7. Evaluation Methodology

18 test questions in `evaluation/questions.json`, covering:
- Direct factual questions
- Multi-document questions (answer spans more than one PDF)
- Numerical questions (fees, percentages, dates)
- Contextual/ambiguous questions
- 6 **negative** questions with no answer in the documents, used to verify the system doesn't hallucinate

Each question is run through `evaluation/run_eval.py`, which checks the answer against an expected result and logs whether retrieval found the right source and whether the answer was correctly grounded or correctly refused. Results are saved to `evaluation/results.json`.

**Result: 18/18 (100%)** after the `MIN_SCORE` fix described in Section 5 (17/18 before the fix).

## 8. Optimization Experiment

Two `TOP_K` configurations were compared by running the full 18-question evaluation suite against each, using `evaluation/compare_configs.py`.

| Config | Pass rate | Avg latency/question | Avg sources used |
|---|---|---|---|
| `TOP_K=4` (default) | 18/18 (100%) | 2.21s* | 1.9 |
| `TOP_K=8` | 18/18 (100%) | 1.2s | 1.9 |

*The `TOP_K=4` average includes a 13.4s outlier on the first question, caused by one-time embedding model load/warm-up rather than retrieval itself; excluding it, both configs perform similarly per-question.

**Result:** retrieval accuracy and answer quality were identical between the two configurations. This is expected given the pipeline's design: `RELATIVE_CUTOFF=0.7` (see Section 5) discards any retrieved chunk scoring below 70% of the best match, regardless of how many chunks `TOP_K` initially returns. So raising `TOP_K` from 4 to 8 widened the retrieval net but the relative-score filter trimmed both back down to the same ~1.9 genuinely relevant chunks per question on this document set. A higher `TOP_K` would likely matter more on a larger or noisier document collection, where more candidate chunks compete for the top slots; on this 4-document test set, `TOP_K=4` is kept as the default since it retrieves less data per query with no measurable cost to quality.

Full run data: `evaluation/config_comparison.json`.

## 9. Logging

Every `/chat` request logs: the query, retrieval time, LLM generation time, and total latency, via `app/utils/logger.py`.

## 10. Setup Instructions

### Prerequisites
- Python 3.12
- [Ollama](https://ollama.com) installed, with `llama3.2:3b` pulled (`ollama pull llama3.2:3b`)

### Local setup
```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in LLM_API_KEY / LLM_BASE_URL / LLM_MODEL
python evaluation/make_sample_docs.py   # regenerates the 4 sample PDFs
uvicorn app.main:app --reload
```

### Docker
```bash
docker build -t ai-knowledge-assistant .
docker run -p 8000:8000 -v $(pwd)/chroma_db:/app/chroma_db ai-knowledge-assistant
```
The container reaches Ollama on the host via `host.docker.internal:11434` (already set as the default `LLM_BASE_URL` for Docker in `.env.example`).

## 11. Limitations

- Local `llama3.2:3b` is a small model; answer quality is lower than a larger hosted model would give.
- No OCR — scanned/image-only PDFs are not supported, only text-based PDFs.
- Single-node ChromaDB, not designed for concurrent high-throughput use.
- No conversation memory — each `/chat` call is independent (see Optional Advanced Features for what could be added).

## 12. Sample Documents

The 4 PDFs in `data/sample_docs/` are for a fictional institute ("Northbridge Institute of Technology") generated by `evaluation/make_sample_docs.py`, so the evaluation questions have known, exact expected answers. Regenerate them anytime with:
```bash
python evaluation/make_sample_docs.py
```
