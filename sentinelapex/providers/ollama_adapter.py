import json
import httpx
from typing import AsyncGenerator, List, Optional
from sentinelapex.providers.base import BaseProvider
from sentinelapex.models import Message

class OllamaAdapter(BaseProvider):
    DEFAULT_URL = "http://localhost:11434/api/chat"

    def __init__(self, api_key: Optional[str], model: str, temperature: float):
        # Ollama doesn't strictly need an API key for local usage, but we keep signature consistent
        super().__init__(api_key, model, temperature)
        self.url = self.DEFAULT_URL

    async def stream_chat(self, messages: List[Message]) -> AsyncGenerator[str, None]:
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": True,
            "options": {
                "temperature": self.temperature
            }
        }

        try:
            async with self.client.stream("POST", self.url, json=payload) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    raise Exception(f"Ollama Error {response.status_code}: {error_text.decode()}")

                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            # Ollama stream returns full message object sometimes, or just delta
                            # In chat endpoint with stream:true, it returns chunks
                            if "message" in data:
                                content = data["message"].get("content")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue
        except httpx.ConnectError:
            raise Exception("Could not connect to Ollama. Is it running on localhost:11434?")
        except httpx.RequestError as e:
            raise Exception(f"Request Error: {str(e)}")