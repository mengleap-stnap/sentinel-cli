import asyncio
from multiprocessing import get_context
from typing import List, Optional
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from sentinelapex import providers
from sentinelapex.ui.console import console
from sentinelapex.config import KeyManager, AppConfig
from sentinelapex.providers.registry import ProviderRegistry
from sentinelapex.core.history import HistoryManager
from sentinelapex.core.tokens import TokenCounter
from sentinelapex.models import Message, ChatSession


class Engine:
    def __init__(self):
        self.config = AppConfig()  # In a real app, load from file/ENV
        self.key_mgr = KeyManager()
        self.history_mgr = HistoryManager(self.config.db_path, self.config.enable_sqlite)

        # State
        self.current_session: Optional[ChatSession] = None
        self.messages: List[Message] = []
        self.system_prompt = "You are SentinelApex, a highly advanced AI assistant. Be concise, professional, and helpful."

        # Current Provider Settings
        self.current_provider_name = self.config.default_provider
        self.current_model = self.config.default_model
        self.temperature = self.config.default_temperature

    async def initialize(self):
        """Start up services"""
        await self.history_mgr.init_db()

        # Load last session or create new one
        # For simplicity, we start fresh or could load last ID from config
        self.start_new_session()

    def start_new_session(self):
        self.current_session = self.history_mgr.new_session(
            provider=self.current_provider_name,
            model=self.current_model
        )
        self.messages = []
        console.print(f"[info]Started new session: {self.current_session.id}[/info]")

    async def switch_provider(self, provider_name: str, model: Optional[str] = None):
        """Validate and switch provider"""
        # Check if key exists (unless local)
        if provider_name not in ["ollama", "lmstudio"]:
            if not self.key_mgr.has_key(provider_name):
                console.print(f"[danger]No API key configured for {provider_name}. Use /apikey[/danger]")
                return False

        self.current_provider_name = provider_name
        if model:
            self.current_model = model

        # Update session metadata
        if self.current_session:
            self.current_session.provider = provider_name
            if model:
                self.current_session.model = model

        console.print(f"[success]Switched to [bold]{provider_name}[/bold] ({self.current_model})[/success]")
        return True

    def set_system_prompt(self, prompt: str):
        self.system_prompt = prompt
        console.print("[success]System prompt updated.[/success]")

    def set_temperature(self, temp: float):
        if 0.0 <= temp <= 2.0:
            self.temperature = temp
            console.print(f"[success]Temperature set to {temp}[/success]")
        else:
            console.print("[danger]Temperature must be between 0.0 and 2.0[/danger]")

    async def process_input(self, user_input: str):
        if not self.current_session:
            self.start_new_session()

        # Add user message
        user_msg = Message(role="user", content=user_input)
        self.messages.append(user_msg)

        # Get Provider Instance
        api_key = self.key_mgr.get_key(self.current_provider_name)

        try:
            provider = ProviderRegistry.get_adapter(
                self.current_provider_name,
                api_key,
                self.current_model,
                self.temperature
            )
        except Exception as e:
            console.print(f"[danger]Provider Initialization Error: {e}[/danger]")
            # Remove the user message if we can't process it? No, keep history.
            return

        # Prepare context
        # Prepend system prompt virtually (some providers handle it differently, adapters handle this)
        chat_context = [Message(role="system", content=self.system_prompt)] + self.messages

        # Token Check (Optional warning)
        # token_count = TokenCounter.count_tokens(chat_context, self.current_model)
        # limit = TokenCounter.get_limit(self.current_model)
        # if token_count > limit * 0.9:
        #     console.print("[warning]Approaching context limit![/warning]")

        # Stream Response
        full_response = ""
        error_occurred = False

        try:
            # Create a live display for streaming
            with Live(console=console, refresh_per_second=15, transient=False, vertical_overflow="visible") as live:
                try:
                    async for chunk in provider.stream_chat(chat_context):
                        full_response += chunk
                        # Render Markdown
                        md = Markdown(full_response)
                        panel = Panel(
                            md,
                            title=f"[bold cyan]{self.current_provider_name}[/bold cyan]",
                            border_style="green",
                            padding=(1, 2)
                        )
                        live.update(panel)

                except Exception as e:
                    error_occurred = True
                    console.print(f"\n[danger]Stream Error: {str(e)}[/danger]")

        finally:
            await provider.close()

        if not error_occurred and full_response:
            # Save assistant message
            self.messages.append(Message(role="assistant", content=full_response))

            # Auto-save session to DB
            await self.history_mgr.save_session(self.current_session)

            # Print token usage info (optional)
            # total_tokens = TokenCounter.count_tokens(self.messages, self.current_model)
            # console.print(f"[dim]Tokens: {total_tokens}[/dim]")