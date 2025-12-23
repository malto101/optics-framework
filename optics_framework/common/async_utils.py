import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
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

    # If we're in the same thread as the event loop, we need to avoid deadlock.
    # run_coroutine_threadsafe() + blocking wait causes deadlock when called from
    # the same thread as the event loop. Use ThreadPoolExecutor to run the
    # coroutine scheduling from a different thread.
    #
    # If loop_thread is None (not set on this event loop), we err on the side
    # of caution and assume we might be in the same thread to avoid deadlock.
    if loop_thread is None or current_thread == loop_thread:
        if loop_thread is None:
            internal_logger.debug("[AsyncUtils] Loop thread unknown → using ThreadPoolExecutor (safe)")
        else:
            internal_logger.debug("[AsyncUtils] Same thread as event loop → using ThreadPoolExecutor")

        def _run_in_thread():
            """Helper function to run coroutine_threadsafe from a different thread."""
            future = asyncio.run_coroutine_threadsafe(coro, loop)
            try:
                return future.result(timeout=30)
            except Exception:
                raise

        # Use ThreadPoolExecutor to run the helper in a different thread
        # This avoids deadlock because the helper thread can safely block
        # while the event loop thread continues processing
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_run_in_thread)
            return future.result(timeout=30)
    else:
        # Different thread - safe to use run_coroutine_threadsafe directly
        internal_logger.debug("[AsyncUtils] Different thread → safe to use run_coroutine_threadsafe")
        future = asyncio.run_coroutine_threadsafe(coro, loop)
        try:
            result = future.result(timeout=30)
        except Exception:
            raise
        return result
