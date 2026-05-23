from .base import BaseProvider
from sentinelapex.models import Message
from typing import AsyncGenerator, List
import json

class OpenAIAdapter(BaseProvider):
    BASE_URL = "https://api.openai.com/v1/chat/completions"

    async def stream_chat(self, messages: List[Message]) -> AsyncGenerator[str, None]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": self.temperature,
            "stream": True
        }

        async with self.client.stream("POST", self.BASE_URL, json=payload, headers=headers) as response:
            if response.status_code != 200:
                error_text = await response.aread()
                raise Exception(f"OpenAI Error: {response.status_code} - {error_text.decode()}")
                
            async for line in response.aiter_lines():
                if line.startswith("data: ") and line != "data: [DONE]":
                    try:
                        data = json.loads(line[6:])
                        delta = data.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue