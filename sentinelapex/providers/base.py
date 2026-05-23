from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, Optional
from sentinelapex.models import Message
import httpx

class BaseProvider(ABC):
    def __init__(self, api_key: Optional[str], model: str, temperature: float):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.client = httpx.AsyncClient(timeout=60.0)

    @abstractmethod
    async def stream_chat(self, messages: List[Message]) -> AsyncGenerator[str, None]:
        pass

    async def close(self):
        await self.client.aclose()