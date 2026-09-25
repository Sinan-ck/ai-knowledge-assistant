from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    llm_api_key: str = "ollama"
    llm_base_url: str = "http://localhost:11434/v1"
    llm_model: str = "llama3.2:3b"

    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 800
    chunk_overlap: int = 150
    top_k: int = 4

    upload_dir: Path = BASE_DIR / "data" / "uploads"
    chroma_dir: Path = BASE_DIR / "chroma_db"
    max_upload_mb: int = 20

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")


settings = Settings()
settings.upload_dir.mkdir(parents=True, exist_ok=True)
settings.chroma_dir.mkdir(parents=True, exist_ok=True)
