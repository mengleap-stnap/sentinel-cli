import json
import httpx
from typing import AsyncGenerator, List, Optional
from sentinelapex.providers.base import BaseProvider
from sentinelapex.models import Message

class GeminiAdapter(BaseProvider):
    BASE_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?alt=sse&key={key}"

    async def stream_chat(self, messages: List[Message]) -> AsyncGenerator[str, None]:
        if not self.api_key:
            raise ValueError("Google API Key is required for Gemini.")

        # Convert messages to Gemini format
        # Gemini expects 'parts' inside 'contents'
        contents = []
        for msg in messages:
            if msg.role == "system":
                # Gemini doesn't have a direct system role in the standard chat endpoint easily 
                # without the system_instruction field which isn't always available in simple REST.
                # We'll prepend it to the first user message or ignore depending on strictness.
                # For simplicity, we treat system as user context here or skip.
                continue 
            
            role = "model" if msg.role == "assistant" else "user"
            contents.append({
                "role": role,
                "parts": [{"text": msg.content}]
            })

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": self.temperature,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 8192,
            }
        }

        url = self.BASE_URL_TEMPLATE.format(model=self.model, key=self.api_key)
        headers = {"Content-Type": "application/json"}

        try:
            async with self.client.stream("POST", url, json=payload, headers=headers) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    raise Exception(f"Gemini Error {response.status_code}: {error_text.decode()}")

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        try:
                            data = json.loads(data_str)
                            candidates = data.get("candidates", [])
                            if candidates:
                                content_parts = candidates[0].get("content", {}).get("parts", [])
                                if content_parts:
                                    yield content_parts[0].get("text", "")
                        except json.JSONDecodeError:
                            continue
        except httpx.RequestError as e:
            raise Exception(f"Connection Error: {str(e)}")