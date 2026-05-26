from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class Message(BaseModel):
    """Represents a single message in a conversation."""

    role: Literal["system", "user", "assistant"]
    content: str
    timestamp: datetime = Field(
        default_factory=datetime.now
    )


class ChatSession(BaseModel):
    """Represents a persistent chat session."""

    id: str
    name: str

    # FIXED mutable default bug
    messages: List[Message] = Field(
        default_factory=list
    )

    created_at: datetime = Field(
        default_factory=datetime.now
    )

    updated_at: datetime = Field(
        default_factory=datetime.now
    )

    provider: str = "openai"
    model: str = "gpt-4o"

    class Config:
        validate_assignment = True


class ProviderResponse(BaseModel):
    """Represents the parsed response from an AI provider."""

    content: str

    usage: Optional[dict] = None

    model: str

    finish_reason: Optional[str] = None