from async_lru import alru_cache


class Session:
    _cache: dict[str, str]

    def __init__(self) -> None:
        self._cache = {}

    async def set(self, key: str, peer_id: str) -> None:
        self._cache[key] = peer_id

    @alru_cache(ttl=1200)
    async def _get(self, key: str) -> str:
        return self._cache.get(key)

    async def get(self, key: str) -> str:
        res = await self._get(key)
        if res is None:
            self._get.cache_invalidate(key)
        return res


session = Session()
