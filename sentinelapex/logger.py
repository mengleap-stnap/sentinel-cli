import logging
from rich.logging import RichHandler

def setup_logger(level: int = logging.INFO) -> logging.Logger:
    """
    Configure the application logger to output via Rich.
    This suppresses standard library logging noise and formats it nicely.
    """
    # Suppress noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(
            rich_tracebacks=True, 
            markup=True,
            show_path=False # Cleaner logs
        )]
    )
    
    logger = logging.getLogger("SentinelApex")
    return logger