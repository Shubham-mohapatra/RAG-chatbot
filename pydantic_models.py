from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class ModelName(str, Enum):
    GEMINI_1_5_FLASH = "gemini-1.5-flash"
    GEMINI_2_5_FLASH = "gemini-2.0-flash-exp"

class QueryInput(BaseModel):
    question: str
    session_id: str = Field(default=None, description="Optional session ID for maintaining chat history")
    model: ModelName = Field(default=ModelName.GEMINI_2_5_FLASH)

class QueryResponse(BaseModel):
    answer: str
    session_id: str
    model: ModelName

class DocumentInfo(BaseModel):
    id: int
    filename: str
    upload_timestamp: datetime
    file_size: int
    content_type: str

    class Config:
        # Allow field aliases for frontend compatibility
        from_attributes = True

class DeleteFileRequest(BaseModel):
    file_id: int
