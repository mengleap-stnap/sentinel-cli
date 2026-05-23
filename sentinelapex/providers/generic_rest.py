import json
import httpx
from typing import AsyncGenerator, List, Optional
from sentinelapex.providers.base import BaseProvider
from sentinelapex.models import Message

class GenericRESTAdapter(BaseProvider):
    """
    Base class for providers that implement the OpenAI Chat Completion API standard.
    Subclasses should define BASE_URL.
    """
    BASE_URL = "" # Must be overridden by subclass

    async def stream_chat(self, messages: List[Message]) -> AsyncGenerator[str, None]:
        if not self.BASE_URL:
            raise NotImplementedError("BASE_URL must be defined in subclass")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Some local providers (LM Studio) might not need auth or handle it differently
        if not self.api_key:
            del headers["Authorization"]

        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": self.temperature,
            "stream": True
        }

        try:
            async with self.client.stream("POST", self.BASE_URL, json=payload, headers=headers) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    raise Exception(f"API Error {response.status_code}: {error_text.decode()}")

                async for line in response.aiter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        try:
                            data = json.loads(line[6:])
                            choices = data.get("choices", [])
                            if choices:
                                delta = choices[0].get("delta", {})
                                content = delta.get("content")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue
        except httpx.RequestError as e:
            raise Exception(f"Connection Error: {str(e)}")