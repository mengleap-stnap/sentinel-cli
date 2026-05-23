import typer
import asyncio
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter
from rich.prompt import Prompt, Confirm

from sentinelapex.ui.console import console
from sentinelapex.ui.banner import print_startup_banner
from sentinelapex.ui.wizard import SetupWizard
from sentinelapex.config import KeyManager, AppConfig
from sentinelapex.core.engine import Engine
from sentinelapex.utils.file_io import ChatExporter

app = typer.Typer(add_completion=False, help="SENTINELAPEX-AI Secure CLI Assistant")

# Global instances
key_mgr = KeyManager()
engine = Engine()

# Command completion list
COMMANDS = [
    "/help", "/exit", "/clear", "/apikey", "/model", 
    "/provider", "/save", "/load", "/system", "/theme", 
    "/history", "/tokens"
]

completer = WordCompleter(COMMANDS, ignore_case=True)

async def repl_loop():
    """The main interactive loop."""
    # Setup history file
    history_path = engine.history_mgr.db_path.parent / "cli_history.txt"
    
    session = PromptSession(
        history=FileHistory(str(history_path)),
        completer=completer,
    )

    # Check if first run
    configured = key_mgr.list_configured_providers()
    if not configured:
        console.print("\n[bold yellow]Welcome to SentinelApex![/bold yellow]")
        console.print("It looks like you haven't configured any API keys yet.\n")
        wizard = SetupWizard(key_mgr)
        await wizard.run_initial_setup()
        # Refresh list after wizard
        configured = key_mgr.list_configured_providers()

    # Start the chat loop
    await engine.initialize()

    while True:
        try:
            # Construct dynamic prompt
            prompt_text = (
                f"[bold cyan][{engine.current_provider_name}][/bold cyan] "
                f"[dim]({engine.current_model})[/dim] > "
            )
            
            user_input = await session.prompt_async(prompt_text)
            
            if not user_input:
                continue

            # Handle commands
            if user_input.startswith("/"):
                await handle_command(user_input)
            else:
                await engine.process_input(user_input)

        except KeyboardInterrupt:
            if Confirm.ask("\n[danger]Exit SentinelApex?[/danger]"):
                break
            continue
        except EOFError:
            break

async def handle_command(cmd: str):
    """Parse and execute slash commands."""
    parts = cmd.split(" ", 1)
    command = parts[0].lower()
    arg = parts[1].strip() if len(parts) > 1 else None

    if command == "/exit":
        raise EOFError
    
    elif command == "/clear":
        engine.messages.clear()
        console.print("[info]Conversation context cleared.[/info]")

    elif command == "/help":
        console.print(
            "[bold cyan]Commands:[/bold cyan]\n"
            "/help       - Show this message\n"
            "/clear      - Clear chat history\n"
            "/exit       - Exit application\n"
            "/apikey     - Manage API Keys (Add/Remove)\n"
            "/provider   - Switch Provider (e.g. openai, anthropic)\n"
            "/model      - Switch Model (e.g. gpt-4o, claude-3)\n"
            "/system     - Set system prompt\n"
            "/temp       - Set temperature (0.0 - 1.0)\n"
            "/save       - Save chat to file (.md, .txt, .json)\n"
            "/history    - View past sessions"
        )

    elif command == "/apikey":
        wizard = SetupWizard(key_mgr)
        await wizard.configure_provider_flow()

    elif command == "/provider":
        if arg:
            success = await engine.switch_provider(arg)
            if success:
                # If model was previously specific to provider, reset it
                pass
        else:
            console.print(f"[info]Current: {engine.current_provider_name}[/info]")

    elif command == "/model":
        if arg:
            engine.current_model = arg
            if engine.current_session:
                engine.current_session.model = arg
            console.print(f"[success]Model set to {arg}[/success]")
        else:
            console.print(f"[info]Current Model: {engine.current_model}[/info]")

    elif command == "/system":
        if arg:
            engine.set_system_prompt(arg)
        else:
            console.print("[info]Usage: /system [prompt text][/info]")

    elif command == "/temp":
        if arg:
            try:
                engine.set_temperature(float(arg))
            except ValueError:
                console.print("[danger]Invalid temperature. Must be float.[/danger]")

    elif command == "/save":
        fmt = "md"
        filename = arg
        if arg and "." in arg:
            filename = arg.split(".")[0]
            fmt = arg.split(".")[-1]
        
        ChatExporter.save_chat(engine.current_session, filename, fmt)

    elif command == "/history":
        sessions = await engine.history_mgr.list_sessions()
        if not sessions:
            console.print("[info]No saved sessions found.[/info]")
        else:
            console.print("[bold]History:[/bold]")
            for s in sessions[:5]: # Show last 5
                console.print(f"  - {s['id']} | {s['name']} | {s['provider']}")

    else:
        console.print(f"[warning]Unknown command: {command}[/warning]")

@app.command()
def run():
    """Launch SentinelApex AI Assistant."""
    print_startup_banner()
    asyncio.run(repl_loop())

if __name__ == "__main__":
    app()