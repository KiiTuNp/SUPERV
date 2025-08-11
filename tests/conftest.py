import os
import pytest
import pytest_asyncio
from httpx import AsyncClient
from pathlib import Path
import sys
import asyncio

# Ensure required environment variables exist before importing server
os.environ.setdefault("MONGO_URL", "mongodb://test")
os.environ.setdefault("DB_NAME", "test_db")

# Add project root to Python path for module imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Disable background tasks during import to avoid event loop issues
create_task = asyncio.create_task
asyncio.create_task = lambda *args, **kwargs: None
from backend import server
asyncio.create_task = create_task

class DummyAdmin:
    async def command(self, cmd):
        return {"ok": 1}

class DummyCollection:
    def __init__(self):
        self.storage = {}
    async def insert_one(self, doc):
        self.storage[doc["id"]] = doc
    async def find_one(self, query):
        for doc in self.storage.values():
            if all(doc.get(k) == v for k, v in query.items()):
                return doc
        return None

class DummyDB:
    def __init__(self):
        self.meetings = DummyCollection()

@pytest_asyncio.fixture
async def async_client(monkeypatch):
    dummy_client = type("DummyClient", (), {"admin": DummyAdmin()})()
    monkeypatch.setattr(server, "client", dummy_client)
    monkeypatch.setattr(server, "db", DummyDB())
    async with AsyncClient(app=server.app, base_url="http://test") as ac:
        yield ac
