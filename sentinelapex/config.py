import os
from pathlib import Path
from dotenv import load_dotenv, set_key
from pydantic import BaseModel, Field
from typing import Optional
from sentinelapex.security import SecurityManager
from sentinelapex.ui.console import console

# Global paths
CONFIG_DIR = Path.home() / ".sentinelapex"
ENV_PATH = CONFIG_DIR / ".env"
DB_PATH = CONFIG_DIR / "sentinelapex.db"

# Initialize Security Manager
SECURITY_MGR = SecurityManager()

class AppConfig(BaseModel):
    """Holds non-secret application configuration."""
    default_provider: str = "openai"
    default_model: str = "gpt-4o"
    default_temperature: float = 0.7
    max_history_length: int = 50
    theme: str = "cyberpunk"
    enable_sqlite: bool = True
    db_path: str = str(DB_PATH)

class KeyManager:
    """
    Manages API keys securely.
    It encrypts keys before saving them to the local .env file.
    """
    
    # Mapping of provider names to .env variable names
    PROVIDER_ENV_MAP = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "google": "GOOGLE_API_KEY",
        "groq": "GROQ_API_KEY",
        "mistral": "MISTRAL_API_KEY",
        "cohere": "COHERE_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
        "together": "TOGETHER_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
        "huggingface": "HUGGINGFACE_TOKEN",
    }

    def __init__(self):
        # Ensure directory and file exist
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        if not ENV_PATH.exists():
            ENV_PATH.touch()
        
        # Load environment variables
        load_dotenv(dotenv_path=ENV_PATH)

    def get_key(self, provider: str) -> Optional[str]:
        """Retrieve and decrypt an API key."""
        env_var = self.PROVIDER_ENV_MAP.get(provider)
        if not env_var:
            return None
        
        encrypted_val = os.getenv(env_var)
        if not encrypted_val:
            return None
        
        return SECURITY_MGR.decrypt_token(encrypted_val)

    def set_key(self, provider: str, key: str) -> bool:
        """Encrypt and save an API key."""
        env_var = self.PROVIDER_ENV_MAP.get(provider)
        if not env_var:
            raise ValueError(f"Unknown provider: {provider}")
        
        if not key:
            return False

        encrypted_key = SECURITY_MGR.encrypt_token(key)
        # Write to .env file
        set_key(str(ENV_PATH), env_var, encrypted_key)
        
        # Reload to reflect changes immediately in this session
        load_dotenv(dotenv_path=ENV_PATH, override=True)
        return True

    def remove_key(self, provider: str):
        """Remove an API key from storage."""
        env_var = self.PROVIDER_ENV_MAP.get(provider)
        if env_var:
            set_key(str(ENV_PATH), env_var, "")
            load_dotenv(dotenv_path=ENV_PATH, override=True)

    def has_key(self, provider: str) -> bool:
        """Check if a provider has a configured key."""
        return self.get_key(provider) is not None

    def list_configured_providers(self) -> list:
        """Returns a list of provider names that have keys set."""
        configured = []
        for prov, var in self.PROVIDER_ENV_MAP.items():
            if os.getenv(var):
                configured.append(prov)
        # Always list local providers as available
        configured.extend(["ollama", "lmstudio"])
        return list(set(configured)) # Unique list