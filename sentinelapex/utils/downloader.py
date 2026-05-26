from pathlib import Path
from typing import Optional

from huggingface_hub import hf_hub_download
from rich.console import Console

console = Console()

# Sentinel model cache directory
CACHE_DIR = Path.home() / ".sentinel" / "models"

# Create cache folder automatically
CACHE_DIR.mkdir(
    parents=True,
    exist_ok=True
)


class DownloadError(Exception):
    """Raised when model download fails."""


def download_model(
    repo_id: str,
    filename: str,
    token: Optional[str] = None
) -> str:
    """
    Download a GGUF model from Hugging Face.

    Args:
        repo_id:
            Hugging Face repository ID.

        filename:
            GGUF filename.

        token:
            Optional HF token.

    Returns:
        Local path to downloaded model.
    """

    try:
        console.print(
            f"[cyan]Downloading[/cyan] "
            f"{filename}"
        )

        path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=CACHE_DIR,
            token=token
        )

        console.print(
            f"[green]Model ready:[/green] {path}"
        )

        return str(path)

    except Exception as e:
        console.print(
            f"[red]Download failed:[/red] {e}"
        )

        raise DownloadError(
            f"Could not download model "
            f"from '{repo_id}'"
        ) from e


def model_exists(
    filename: str
) -> bool:
    """
    Check if model already exists locally.
    """

    model_path = CACHE_DIR / filename

    return model_path.exists()


def get_model_path(
    filename: str
) -> str:
    """
    Return full local model path.
    """

    return str(CACHE_DIR / filename)