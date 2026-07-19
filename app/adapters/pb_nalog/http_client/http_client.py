import asyncio
from typing import List
from aiohttp import ClientSession, ClientError, ClientProxyConnectionError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from config.settings import get_settings
from domain.entities import Person, Organization
from adapters.pb_nalog.http_client.schemas import SearchPersonsRequestPayload, GetOrganizationsRequestPayload
from domain.contracts.pb_nalog.pb_nalog_client import PbNalogClientContract
from domain.contracts.proxy.proxy_provider import ProxyProviderContract


settings = get_settings()

class HTTPClient(PbNalogClientContract):
    def __init__(self, http_session: ClientSession, proxy_provider: ProxyProviderContract):
        self._session = http_session
        self._proxy_provider = proxy_provider
        self._cookie_initialized = False

    @retry(
        stop = stop_after_attempt(2),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=2),
        retry=retry_if_exception_type((ClientError, asyncio.TimeoutError))
    )
    async def _request(self, method: str, url: str, proxy: str | None, **kwargs) -> ClientSession:
        try:
            async with self._session.request(method=method, url=url, proxy=proxy, **kwargs) as response:
                response.raise_for_status()
                return await response.json()
        except ClientProxyConnectionError:
            # TODO: добавить логгирование
            raise

    async def _ensure_cookie(self) -> None:
        if not self._cookie_initialized:
            proxy = await self._proxy_provider.get_proxy()
            await self._request(method="GET", url=settings.pb_nalog_base_url, proxy=proxy)
            self._cookie_initialized = True

    async def _poll_result(self, task_id: str, proxy: str | None, timeout: float = 8.0, delay: float = 0.5) -> dict:
        async def _poll_loop():
            while True:
                result = await self._request("POST", settings.pb_nalog_search_url, proxy=proxy, data={"method": "get-response", "id": task_id})
                if result is not None:
                    return result
                await asyncio.sleep(delay)

        try:
            return await asyncio.wait_for(_poll_loop(), timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Задача {task_id} не готова за {timeout} секунд")

    async def _map_persons(self, raw: dict) -> List[Person]:
        items = raw.get("upr", {}).get("data", [])
        # я решил не разделять модели сырых и внутрисервисных данных в силу их абсолютной идентичности
        return [Person.model_validate(item) for item in items]

    async def _map_orgranizations(self, raw: dict) -> List[Organization]:
        items = raw.get("ul", {}).get("data", [])
        return [Organization.model_validate(item) for item in items]

    async def search_persons(self, name: str) -> List[Person]:
        await self._ensure_cookie()
        proxy = await self._proxy_provider.get_proxy()
        
        payload = SearchPersonsRequestPayload(
            queryUpr=name
        )
        task = await self._request("POST", settings.pb_nalog_search_url, proxy=proxy, data=payload)
        
        response = await self._poll_result(task["id"], proxy)

        return self._map_persons(response)

    async def get_organizations(self, name, token) -> List[Organization]:
        await self._ensure_cookie()
        proxy = await self._proxy_provider.get_proxy()

        payload = GetOrganizationsRequestPayload(
            queryUl=name,
            token=token
        )

        task = await self._request("POST", settings.pb_nalog_search_url, proxy, data=payload)

        response = await self._poll_result(task["id"], proxy)

        return self._map_orgranizations(response)