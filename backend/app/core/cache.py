# backend/app/core/cache.py

import time
from server.logger import log
from app.core.settings import settings


class SimpleCache:
    """
    In-memory TTL cache used for:
    - caching repeated questions (FAQ-style)
    - reducing LLM + RAG API cost
    - speeding up responses

    Cache autodeletes older entries based on TTL.
    """

    def __init__(self, ttl: int = None):
        self.ttl = ttl or settings.CACHE_TTL_SECONDS  # default 30 days
        self.store = {}

    def set(self, key: str, value: str):
        """Save value in cache with timestamp."""
        key = key.strip().lower()
        self.store[key] = {
            "value": value,
            "timestamp": time.time()
        }
        log.info(f"[CACHE] Stored key: {key}")

    def get(self, key: str):
        """Retrieve cached value if not expired."""
        key = key.strip().lower()
        if key not in self.store:
            return None

        entry = self.store[key]
        age = time.time() - entry["timestamp"]

        if age > self.ttl:
            # expired → delete
            del self.store[key]
            log.info(f"[CACHE] Expired key removed: {key}")
            return None

        log.info(f"[CACHE] Hit for key: {key}")
        return entry["value"]

    def delete(self, key: str):
        key = key.strip().lower()
        if key in self.store:
            del self.store[key]

    def clear(self):
        """Force clear all cache."""
        self.store = {}
        log.info("[CACHE] Cleared all entries")
