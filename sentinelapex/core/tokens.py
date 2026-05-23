import tiktoken
from typing import List
from sentinelapex.models import Message

class TokenCounter:
    """
    Estimates token usage for chat messages.
    Supports OpenAI encodings and provides a rough estimate for others.
    """
    
    # Mapping of common model families to their tiktoken encoding
    ENCODING_MAP = {
        "gpt-4": "cl100k_base",
        "gpt-3.5": "cl100k_base",
        "gpt-4o": "o200k_base",
        "claude": "cl100k_base", # Approximation
        "llama": "cl100k_base",  # Approximation for many Llama variants via OpenRouter/Groq
    }

    @staticmethod
    def count_tokens(messages: List[Message], model: str = "gpt-4o") -> int:
        """
        Calculate the number of tokens in a list of messages.
        """
        try:
            # Determine encoding
            encoding_name = "cl100k_base" # Default fallback
            for key, enc in TokenCounter.ENCODING_MAP.items():
                if key in model.lower():
                    encoding_name = enc
                    break
            
            encoding = tiktoken.get_encoding(encoding_name)
            
            # Calculate tokens
            # Note: This is an approximation. Actual API token counts include overhead for message structure.
            num_tokens = 0
            for message in messages:
                # Every message follows format: {"role": role, "content": content}
                num_tokens += 4  # Account for header/structure overhead per message
                num_tokens += len(encoding.encode(message.content))
                
            num_tokens += 2  # Final padding
            
            return num_tokens
            
        except Exception:
            # Fallback: Rough estimate (1 token ~= 4 chars for English text)
            total_chars = sum(len(m.content) for m in messages)
            return total_chars // 4

    @staticmethod
    def get_limit(model: str) -> int:
        """Returns approximate context window limit."""
        if "gpt-4-1106" in model or "gpt-4-turbo" in model or "gpt-4o" in model:
            return 128000
        elif "gpt-4" in model:
            return 8192
        elif "gpt-3.5" in model:
            return 16385
        elif "claude-3" in model:
            return 200000
        elif "llama-3" in model:
            return 8192 # Or 128k depending on variant
        else:
            return 4096 # Safe default