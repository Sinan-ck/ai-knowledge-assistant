from pydantic import BaseModel, Field


class ProcessRequest(BaseModel):
    filename: str | None = Field(None, description="PDF in the uploads folder. Omit to process all.")


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)
    top_k: int | None = Field(None, ge=1, le=10)
