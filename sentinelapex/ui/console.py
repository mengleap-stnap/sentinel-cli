from rich.console import Console
from rich.theme import Theme

# Define the Cyberpunk Theme
CYBERPUNK_THEME = Theme({
    "info": "dim cyan",
    "warning": "bold yellow",
    "danger": "bold red",
    "success": "bold green",
    "header": "bold magenta",
    "user_msg": "cyan",
    "ai_msg": "green",
    "system_msg": "dim yellow",
    "code": "bold blue",
    "border": "bright_magenta",
    "repr.str": "cyan",
    "repr.number": "magenta"
})

# Initialize Global Console
console = Console(
    theme=CYBERPUNK_THEME,
    highlight=True,
    markup=True,
    soft_wrap=True,
    legacy_windows=False  # Ensure true color support on modern Windows terminals
)