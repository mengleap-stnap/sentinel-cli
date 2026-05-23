from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from sentinelapex.config import KeyManager
from sentinelapex.providers.registry import ProviderRegistry
import httpx

console = Console()

class SetupWizard:
    def __init__(self, key_manager: KeyManager):
        self.key_manager = key_manager

    async def run_initial_setup(self):
        console.print(Panel.fit("[bold cyan]SENTINELAPEX INITIAL SETUP[/bold cyan]", border_style="cyan"))
        console.print("Let's configure your AI providers. Keys are encrypted locally.\n")

        configured = self.key_manager.list_configured_providers()
        if configured:
            console.print(f"[green]✓ Detected existing config for: {', '.join(configured)}[/green]")
            if not Confirm.ask("Reconfigure?", default=False):
                return

        await self.configure_provider_flow()

    async def configure_provider_flow(self):
        providers = ["openai", "anthropic", "google", "groq", "ollama", "exit"]
        
        while True:
            choice = Prompt.ask(
                "\n[bold]Select provider to configure[/bold]",
                choices=providers,
                default="openai"
            )
            
            if choice == "exit":
                break
            
            if choice in ["ollama", "lmstudio"]:
                console.print("[green]✓ Local provider selected. No API key needed.[/green]")
                continue

            key = Prompt.ask(f"Enter API Key for [bold]{choice}[/bold]", password=True)
            if not key:
                console.print("[red]Key cannot be empty.[/red]")
                continue

            # Validate Key
            console.print("[dim]Validating key...[/dim]")
            is_valid = await self.validate_key(choice, key)
            
            if is_valid:
                self.key_manager.set_key(choice, key)
                console.print(f"[bold green]✓ Key saved and encrypted for {choice}.[/bold green]")
            else:
                console.print("[bold red]✗ Invalid Key or Network Error. Try again.[/bold red]")

    async def validate_key(self, provider: str, key: str) -> bool:
        """Quick smoke test for API keys."""
        try:
            if provider == "openai":
                async with httpx.AsyncClient() as client:
                    resp = await client.get(
                        "https://api.openai.com/v1/models",
                        headers={"Authorization": f"Bearer {key}"},
                        timeout=5.0
                    )
                    return resp.status_code == 200
            elif provider == "anthropic":
                async with httpx.AsyncClient() as client:
                    resp = await client.get(
                        "https://api.anthropic.com/v1/models",
                        headers={"x-api-key": key, "anthropic-version": "2023-06-01"},
                        timeout=5.0
                    )
                    return resp.status_code == 200
            # Add other providers validation logic here
            else:
                return True # Skip validation for others for brevity
        except Exception:
            return False