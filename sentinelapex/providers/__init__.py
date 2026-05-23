from sentinelapex.providers.registry import ProviderRegistry
from sentinelapex.providers.openai_adapter import OpenAIAdapter
from sentinelapex.providers.anthropic_adapter import AnthropicAdapter
from sentinelapex.providers.gemini_adapter import GeminiAdapter
from sentinelapex.providers.ollama_adapter import OllamaAdapter
from sentinelapex.providers.generic_rest import GenericRESTAdapter

# Register Standard Providers
ProviderRegistry.register("openai", OpenAIAdapter)
ProviderRegistry.register("anthropic", AnthropicAdapter)
ProviderRegistry.register("google", GeminiAdapter) # Google uses 'google' as key in config
ProviderRegistry.register("ollama", OllamaAdapter)

# Register Generic REST Providers (using specific classes or generic config)
# Note: For providers like Groq, Mistral, Together, DeepSeek which follow OpenAI spec,
# we can either create specific small classes or use a configured GenericRESTAdapter.
# Here we register specific named entries pointing to the Generic adapter with pre-configured URLs.

def register_generic_providers():
    """Helper to register OpenAI-compatible endpoints"""
    
    # Groq
    class GroqAdapter(GenericRESTAdapter):
        BASE_URL = "https://api.groq.com/openai/v1/chat/completions"
        
    ProviderRegistry.register("groq", GroqAdapter)

    # Mistral AI
    class MistralAdapter(GenericRESTAdapter):
        BASE_URL = "https://api.mistral.ai/v1/chat/completions"
        
    ProviderRegistry.register("mistral", MistralAdapter)

    # Together AI
    class TogetherAdapter(GenericRESTAdapter):
        BASE_URL = "https://api.together.xyz/v1/chat/completions"
        
    ProviderRegistry.register("together", TogetherAdapter)

    # DeepSeek
    class DeepSeekAdapter(GenericRESTAdapter):
        BASE_URL = "https://api.deepseek.com/v1/chat/completions"
        
    ProviderRegistry.register("deepseek", DeepSeekAdapter)

    # OpenRouter (Requires special header handling usually, but often compatible)
    class OpenRouterAdapter(GenericRESTAdapter):
        BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
        def __init__(self, api_key, model, temperature):
            super().__init__(api_key, model, temperature)
            # OpenRouter specific headers can be added here if needed
            
    ProviderRegistry.register("openrouter", OpenRouterAdapter)

    # LM Studio (Local)
    class LMStudioAdapter(GenericRESTAdapter):
        BASE_URL = "http://localhost:1234/v1/chat/completions"
        
    ProviderRegistry.register("lmstudio", LMStudioAdapter)

    # HuggingFace Inference API (Chat Completion endpoint if available, otherwise text-gen)
    # Note: HF is complex, often using specific model IDs. This assumes a TGI endpoint compatible with OpenAI format.
    class HuggingFaceAdapter(GenericRESTAdapter):
        # Users might need to override this URL via config for specific endpoints
        BASE_URL = "https://api-inference.huggingface.co/v1/chat/completions" 
        
    ProviderRegistry.register("huggingface", HuggingFaceAdapter)

# Execute registration
register_generic_providers()

__all__ = [
    "ProviderRegistry",
    "OpenAIAdapter",
    "AnthropicAdapter",
    "GeminiAdapter",
    "OllamaAdapter",
    "GenericRESTAdapter"
]