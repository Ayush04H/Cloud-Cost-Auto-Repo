from collections.abc import AsyncIterator
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class JobBus(Protocol):
    """Abstraction for optimization job queuing and progress streaming.

    $0 free tier: InMemoryJobBus (asyncio.Queue + TTLCache).
    1M-user AWS scale: SQSJobQueue + RedisPubSub.
    """

    async def enqueue(self, job_id: str, payload: dict[str, Any]) -> None:
        """Enqueue an optimization job."""
        ...

    async def publish(self, job_id: str, event: dict[str, Any]) -> None:
        """Publish a progress or completion event for subscribers."""
        ...

    def subscribe(self, job_id: str) -> AsyncIterator[dict[str, Any]]:
        """Yield events for a job until completion or failure."""
        ...


@runtime_checkable
class BlobStore(Protocol):
    """Abstraction for large cluster snapshot and packing result JSON blobs.

    $0 free tier: PostgresBlobStore (JSONB column).
    1M-user AWS scale: S3BlobStore (metadata URI in Postgres, payload in S3).
    """

    async def put_json(self, key: str, payload: dict[str, Any]) -> str:
        """Store JSON payload and return its storage URI or key."""
        ...

    async def get_json(self, key: str) -> dict[str, Any] | None:
        """Retrieve JSON payload by key or URI."""
        ...


@runtime_checkable
class RateLimiter(Protocol):
    """Abstraction for per-tenant API and LLM rate limiting.

    $0 free tier: InMemoryRateLimiter (token bucket).
    1M-user AWS scale: RedisRateLimiter.
    """

    async def allow(self, tenant_id: str) -> bool:
        """Return True if the tenant is within rate limits."""
        ...
