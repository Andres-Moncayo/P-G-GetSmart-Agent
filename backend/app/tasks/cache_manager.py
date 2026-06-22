"""
FastAPI In-Memory Cache Manager

Replaces Redis caching with FastAPI in-memory caching for API responses.
Maintains same cache patterns and TTL as Redis implementation.
"""

from datetime import timedelta
from typing import Any, Optional
from fastapi_cache import FastAPICache
from fastapi_cache.backends.memory import InMemoryBackend
from fastapi_cache.decorator import cache

# Cache configuration
CACHE_TTL_SECONDS = 3600  # 1 hour TTL as per specification
CACHE_KEY_PREFIX = "scraper"


class CacheManager:
    """FastAPI in-memory cache manager for API responses."""
    
    @staticmethod
    async def init_cache():
        """Initialize FastAPI cache with in-memory backend."""
        FastAPICache.init(
            InMemoryBackend(), 
            prefix=CACHE_KEY_PREFIX
        )
    
    @staticmethod
    def get_cache_key(game_id: str, api_source: str, endpoint_hash: str) -> str:
        """Generate cache key in format: scraper:{game_id}:{api_source}:{endpoint_hash}"""
        return f"{CACHE_KEY_PREFIX}:{game_id}:{api_source}:{endpoint_hash}"
    
    @staticmethod
    def cache_response(expire: int = CACHE_TTL_SECONDS):
        """Decorator for caching API responses."""
        return cache(
            expire=expire,
            namespace=CACHE_KEY_PREFIX
        )
    
    @staticmethod
    async def get(key: str) -> Optional[Any]:
        """Get value from cache."""
        backend = FastAPICache.get_backend()
        return await backend.get(key)
    
    @staticmethod
    async def set(key: str, value: Any, expire: int = CACHE_TTL_SECONDS) -> None:
        """Set value in cache."""
        backend = FastAPICache.get_backend()
        await backend.set(key, value, expire=timedelta(seconds=expire))
    
    @staticmethod
    async def delete(key: str) -> None:
        """Delete value from cache."""
        backend = FastAPICache.get_backend()
        await backend.delete(key)
    
    @staticmethod
    async def clear() -> None:
        """Clear all cache entries."""
        backend = FastAPICache.get_backend()
        await backend.clear()


# Cache decorators for specific API endpoints
def cache_igdb_metadata(expire: int = CACHE_TTL_SECONDS):
    """Cache IGDB game metadata responses."""
    return cache(expire=expire, namespace=f"{CACHE_KEY_PREFIX}:igdb")


def cache_rawg_metadata(expire: int = CACHE_TTL_SECONDS):
    """Cache RAWG game metadata responses."""
    return cache(expire=expire, namespace=f"{CACHE_KEY_PREFIX}:rawg")


def cache_steam_storefront(expire: int = CACHE_TTL_SECONDS):
    """Cache Steam Storefront responses."""
    return cache(expire=expire, namespace=f"{CACHE_KEY_PREFIX}:steam")


def cache_steamspy(expire: int = CACHE_TTL_SECONDS):
    """Cache SteamSpy responses."""
    return cache(expire=expire, namespace=f"{CACHE_KEY_PREFIX}:steamspy")