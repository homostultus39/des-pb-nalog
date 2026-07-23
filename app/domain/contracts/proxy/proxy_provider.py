from abc import abstractmethod, ABC


class ProxyProviderContract(ABC):
    @abstractmethod
    async def get_proxy(self) -> str | None:
        pass

    @abstractmethod
    async def mark_bad(self, proxy: str) -> None:
        pass