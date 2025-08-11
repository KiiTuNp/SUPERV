import asyncio

vote_locks = {}
lock_manager = asyncio.Lock()
