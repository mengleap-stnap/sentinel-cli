import asyncio
import functools
from sentinelapex.ui.console import console

def retry_async(retries: int = 3, delay: float = 1.0, backoff: float = 2.0, exceptions: tuple = (Exception,)):
    """
    Decorator for async functions to retry on failure.
    
    Args:
        retries: Number of retry attempts.
        delay: Initial delay between retries in seconds.
        backoff: Multiplier for delay after each retry.
        exceptions: Tuple of exception classes to catch.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < retries - 1:
                        # Check if it's a rate limit error to maybe wait longer
                        wait_time = current_delay
                        if "429" in str(e):
                            console.print(f"[warning]Rate limit hit. Waiting {wait_time}s...[/warning]")
                        else:
                            console.print(f"[dim]Attempt {attempt + 1} failed: {str(e)}. Retrying in {wait_time}s...[/dim]")
                        
                        await asyncio.sleep(wait_time)
                        current_delay *= backoff
                    else:
                        console.print(f"[danger]Failed after {retries} attempts.[/danger]")
            
            raise last_exception
        return wrapper
    return decorator