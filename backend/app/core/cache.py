from cachetools import TTLCache

# Bounded in-memory caches to respect the 512 MB container RAM limit.
pricing_cache: TTLCache[str, object] = TTLCache(maxsize=16, ttl=900)
policy_cache: TTLCache[str, object] = TTLCache(maxsize=512, ttl=3600)
cluster_cache: TTLCache[str, object] = TTLCache(maxsize=64, ttl=1800)
