FROM python:3.12-slim

WORKDIR /code

# System deps needed by sentence-transformers / torch and pypdf
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Chroma DB persists here — mount a volume to this path to keep data across restarts
VOLUME ["/code/chroma_db"]

# Pre-download the embedding model at build time so first request isn't slow
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

ENV LLM_BASE_URL=http://host.docker.internal:11434/v1
ENV LLM_API_KEY=ollama
ENV LLM_MODEL=llama3.2:3b

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
