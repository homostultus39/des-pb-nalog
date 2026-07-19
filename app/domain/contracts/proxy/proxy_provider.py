from abc import abstractmethod, ABC


class ProxyProviderContract(ABC):
    @abstractmethod
    async def get_proxy(self) -> str | None:
        """
        Просто возвращаем url строку для подключения к прокси или None, если прокси
        не настроен или не нужен
        """
        pass