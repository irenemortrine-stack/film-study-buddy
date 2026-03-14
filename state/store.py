import json
import asyncio
from typing import Optional
import redis.asyncio as aioredis
from config import settings
from state.models import Session

SESSION_TTL = 86400  # 24h


def _session_key(open_id: str) -> str:
    return f"session:{open_id}"


def _lock_key(open_id: str) -> str:
    return f"session_lock:{open_id}"


def get_redis() -> aioredis.Redis:
    return aioredis.from_url(settings.redis_url, decode_responses=True)


async def get_session(open_id: str) -> Session:
    r = get_redis()
    try:
        data = await r.get(_session_key(open_id))
        if data:
            return Session.model_validate_json(data)
        return Session()
    finally:
        await r.aclose()


async def save_session(open_id: str, session: Session) -> None:
    r = get_redis()
    try:
        await r.set(
            _session_key(open_id),
            session.model_dump_json(),
            ex=SESSION_TTL,
        )
    finally:
        await r.aclose()


async def delete_session(open_id: str) -> None:
    r = get_redis()
    try:
        await r.delete(_session_key(open_id))
    finally:
        await r.aclose()


class SessionLock:
    """Async context manager for distributed session lock."""

    def __init__(self, open_id: str, timeout: int = 30):
        self.open_id = open_id
        self.timeout = timeout
        self._r: Optional[aioredis.Redis] = None

    async def __aenter__(self):
        self._r = get_redis()
        deadline = asyncio.get_event_loop().time() + self.timeout
        while asyncio.get_event_loop().time() < deadline:
            acquired = await self._r.set(
                _lock_key(self.open_id), "1", nx=True, ex=self.timeout
            )
            if acquired:
                return self
            await asyncio.sleep(0.1)
        raise TimeoutError(f"Could not acquire session lock for {self.open_id}")

    async def __aexit__(self, *_):
        await self._r.delete(_lock_key(self.open_id))
        await self._r.aclose()
