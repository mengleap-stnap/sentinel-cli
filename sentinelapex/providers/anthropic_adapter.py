import json
import httpx
from typing import AsyncGenerator, List, Optional
from sentinelapex.providers.base import BaseProvider
from sentinelapex.models import Message

class AnthropicAdapter(BaseProvider):
    BASE_URL = "https://api.anthropic.com/v1/messages"
    DEFAULT_VERSION = "2023-06-01"

    def __init__(self, api_key: Optional[str], model: str, temperature: float):
        super().__init__(api_key, model, temperature)
        self.headers = {
            "x-api-key": self.api_key,
            "anthropic-version": self.DEFAULT_VERSION,
            "content-type": "application/json"
        }

    async def stream_chat(self, messages: List[Message]) -> AsyncGenerator[str, None]:
        """
        Anthropic uses a different message format than OpenAI.
        System prompt is separated from messages.
        """
        # Extract system message if present
        system_prompt = ""
        chat_messages = []
        for msg in messages:
            if msg.role == "system":
                system_prompt = msg.content
            else:
                chat_messages.append({"role": msg.role, "content": msg.content})

        payload = {
            "model": self.model,
            "messages": chat_messages,
            "max_tokens": 4096, # Anthropic requires max_tokens
            "temperature": self.temperature,
            "stream": True
        }
        
        if system_prompt:
            payload["system"] = system_prompt

        try:
            async with self.client.stream("POST", self.BASE_URL, json=payload, headers=self.headers) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    raise Exception(f"Anthropic Error {response.status_code}: {error_text.decode()}")

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        
                        try:
                            event = json.loads(data_str)
                            # Handle different event types
                            if event.get("type") == "content_block_delta":
                                delta = event.get("delta", {})
                                if delta.get("type") == "text_delta":
                                    yield delta.get("text", "")
                        except json.JSONDecodeError:
                            continue
        except httpx.RequestError as e:
            raise Exception(f"Connection Error: {str(e)}")