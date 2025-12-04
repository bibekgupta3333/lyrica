"""
Utility functions for handling async operations in sync contexts.

This module provides helpers for running async code from synchronous contexts,
particularly useful when dealing with libraries that require async operations
but are called from FastAPI endpoints or other async contexts.
"""

import asyncio
import threading
from typing import Coroutine, TypeVar

from loguru import logger

T = TypeVar("T")


def run_async_in_thread(coro: Coroutine[None, None, T]) -> T:
    """
    Run an async coroutine in a separate thread with its own event loop.

    This is useful when you need to call async code from a sync context,
    especially when you're already in an async context
    (like FastAPI endpoints).

    Args:
        coro: The coroutine to run

    Returns:
        The result of the coroutine

    Example:
        ```python
        async def my_async_function():
            return "result"

        # This will work even if called from an async context
        result = run_async_in_thread(my_async_function())
        ```
    """
    try:
        # Check if we're already in an async context
        asyncio.get_running_loop()
        # We're in an async context, run in a separate thread
        # with its own event loop
        result_container: list[T] = []
        exception_container: list[Exception] = []

        def run_in_thread():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                result = new_loop.run_until_complete(coro)
                result_container.append(result)
            except Exception as e:
                exception_container.append(e)
            finally:
                new_loop.close()

        thread = threading.Thread(target=run_in_thread)
        thread.start()
        thread.join()

        if exception_container:
            raise exception_container[0]

        return result_container[0] if result_container else None

    except RuntimeError:
        # No running loop, safe to use asyncio.run()
        return asyncio.run(coro)


def safe_run_async(coro: Coroutine[None, None, T]) -> T:
    """
    Safely run an async coroutine, handling both sync and async contexts.

    This is a convenience wrapper around run_async_in_thread that provides
    better error handling and logging.

    Args:
        coro: The coroutine to run

    Returns:
        The result of the coroutine

    Raises:
        RuntimeError: If the coroutine execution fails
    """
    try:
        return run_async_in_thread(coro)
    except Exception as e:
        logger.error(f"Failed to run async coroutine: {e}")
        raise
