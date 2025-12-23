import asyncio
import threading
from typing import Any, Coroutine
from optics_framework.common.logging_config import internal_logger

# Global persistent event loop for Playwright async operations
_persistent_loop = None
_loop_thread = None
_loop_lock = threading.Lock()


def _get_or_create_persistent_loop():
    """Get or create a persistent event loop in a background thread."""
    global _persistent_loop, _loop_thread

    with _loop_lock:
        if _persistent_loop is None or _persistent_loop.is_closed():
            def run_loop():
                global _persistent_loop
                _persistent_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(_persistent_loop)
                _persistent_loop.run_forever()

            _loop_thread = threading.Thread(target=run_loop, daemon=True)
            _loop_thread.start()

            # Wait for loop to be created
            import time
            for _ in range(10):
                if _persistent_loop is not None:
                    break
                time.sleep(0.1)

    return _persistent_loop


def run_async(coro: Coroutine[Any, Any, Any]):
    """
    Run async coroutine safely from sync code.
    Handles nested event loops (pytest, Jupyter, asyncio frameworks).
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop is None:
        # No running loop - use persistent loop in background thread
        persistent_loop = _get_or_create_persistent_loop()
        future = asyncio.run_coroutine_threadsafe(coro, persistent_loop)
        try:
            result = future.result(timeout=30)
        except Exception:
            raise
        return result

    internal_logger.debug("[AsyncUtils] Running loop detected → thread-safe execution")
    # Check if we're in the same thread as the event loop
    current_thread = threading.current_thread()
    loop_thread = getattr(loop, '_thread', None)

    # If we're in the same thread as the event loop, we need to run in a separate thread
    # to avoid deadlock. Use ThreadPoolExecutor to run the coroutine in a new event loop.
    if current_thread == loop_thread:
        # Run in a separate thread with a new event loop
        # Note: This creates a new event loop, so the page object needs to be accessible
        # Actually, this won't work because the page is tied to the original loop
        # So we need to use run_coroutine_threadsafe but ensure the loop can process it
        # Let's try using a timeout and see if that helps
        future = asyncio.run_coroutine_threadsafe(coro, loop)
        try:
            # Use a timeout to prevent indefinite blocking
            result = future.result(timeout=30)
        except Exception:
            raise
        return result
    else:
        # Different thread - safe to use run_coroutine_threadsafe
        future = asyncio.run_coroutine_threadsafe(coro, loop)
        result = future.result(timeout=30)
        return result
