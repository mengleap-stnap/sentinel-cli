import time
import pyfiglet
from rich.panel import Panel
from rich.text import Text
from rich.console import Console
from sentinelapex.ui.console import console

def print_startup_banner():
    """
    Displays the animated SentinelApex startup sequence.
    """
    # Clear screen for dramatic effect (optional, works on most terminals)
    console.clear()

    # Generate ASCII Art
    title_art = pyfiglet.figlet_format("SENTINEL\nAPEX", font="slant")
    
    # Style the art with neon colors
    styled_art = Text(title_art)
    styled_art.stylize("bold magenta")
    
    # Print centered
    console.print(styled_art, justify="center")
    
    # System Info Panel
    info_panel = Panel(
        "[bold cyan]v1.0.0[/bold cyan] | [green]Secure Multi-Provider AI Interface[/green]\n"
        "[dim]Type /help for commands. Press Ctrl+C to exit.[/dim]",
        border_style="bright_magenta",
        title="[bold]SYSTEM ONLINE[/bold]",
        subtitle="[dim]Encrypted Storage Active[/dim]"
    )
    console.print(info_panel)
    
    # Simulate boot sequence
    console.print("\n[blink]Initializing Neural Link...[/blink]")
    time.sleep(0.3)
    console.print("[dim]Loading Providers...[/dim]")
    time.sleep(0.3)
    console.print("[dim]Decrypting Keys...[/dim]")
    time.sleep(0.3)
    console.print("[green]✓ Ready.[/green]\n")