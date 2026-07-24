import asyncio
from time import monotonic

from domain.contracts.proxy.proxy_provider import ProxyProviderContract


class ProxyProvider(ProxyProviderContract):
    def __init__(self, proxy_urls: list[str] | None = None, cooldown_seconds: float = 30.0):
        self._proxies = proxy_urls or None
        self._cooldown_seconds = cooldown_seconds
        self._index = 0
        self._lock = asyncio.Lock()
        self._bad_until: dict[str, float] = {}

    async def get_proxy(self) -> str | None:
        if not self._proxies:
            return None
        
        async with self._lock:
            now = monotonic()

            for _ in range(len(self._proxies)):
                candidate = self._proxies[self._index % len(self._proxies)]
                self._index += 1
                bad_until = self._bad_until.get(candidate)

                if bad_until is None or bad_until <= now:
                    return candidate
            return None
        
    async def mark_bad(self, proxy: str) -> None:
        async with self._lock:
            self._bad_until[proxy] = monotonic() + self._cooldown_seconds