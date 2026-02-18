import asyncio

def run_async(coro):
    """
    Helper function to run async code from sync context.
    
    Handles both cases:
    - No event loop running: uses asyncio.run()
    - Event loop already running: uses nest_asyncio to allow nested loops
    
    Args:
        coro: Coroutine to run
        
    Returns:
        Result of the coroutine
    """
    try:
        # Try to get running event loop
        loop = asyncio.get_running_loop()
        # If we're here, there's a running loop
        # Use nest_asyncio to allow nested event loops
        try:
            import nest_asyncio
            nest_asyncio.apply()
            # Now we can use asyncio.run() even with a running loop
            return asyncio.run(coro)
        except ImportError:
            raise RuntimeError(
                "nest_asyncio is required when running async code from sync context "
                "within an existing event loop. Install with: pip install nest-asyncio"
            )
    except RuntimeError:
        # No event loop running, safe to use asyncio.run()
        return asyncio.run(coro)
