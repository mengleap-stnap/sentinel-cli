from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from pathlib import Path
from sentinelapex.ui.console import console

# Path for storing input history
HISTORY_FILE = Path.home() / ".sentinelapex" / "input_history.txt"
HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

# Define available commands for autocomplete
COMMANDS = [
    "/help", "/exit", "/clear", "/apikey", "/model", 
    "/provider", "/save", "/load", "/system", "/theme", 
    "/history", "/tokens"
]

# Create completer
completer = WordCompleter(COMMANDS, ignore_case=True)

# Create session
session = PromptSession(
    history=FileHistory(str(HISTORY_FILE)),
    auto_suggest=AutoSuggestFromHistory(),
    completer=completer,
)

async def get_user_input(prompt_text: str) -> str:
    """
    Asynchronously get user input with rich styling and history.
    
    Args:
        prompt_text: The text to display before the input cursor.
        
    Returns:
        The user's input string.
    """
    try:
        # Note: prompt_toolkit handles its own styling via the prompt toolkit styles,
        # but we pass the raw text here. The visual styling of the prompt itself 
        # is handled by the CLI loop in cli.py using Rich for the output.
        user_input = await session.prompt_async(prompt_text)
        return user_input.strip()
    except EOFError:
        return "/exit"
    except KeyboardInterrupt:
        return "/exit"