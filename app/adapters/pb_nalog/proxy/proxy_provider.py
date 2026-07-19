from domain.contracts.proxy.proxy_provider import ProxyProviderContract


class ProxyProvider(ProxyProviderContract):
    def __init__(self, proxy_url: str | None = None):
        self._proxy_url = proxy_url
    
    async def get_proxy(self) -> str | None:
        return self._proxy_url