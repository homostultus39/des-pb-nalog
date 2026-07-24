import asyncio
import random

from aiohttp import (
    ClientConnectionError,
    ClientError,
    ClientProxyConnectionError,
    ClientSession,
    InvalidURL,
)
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from adapters.pb_nalog.http_client.schemas import (
    GetOrganizationsRequestPayload,
    SearchPersonsRequestPayload,
)
from adapters.schemas.entities import Organization, Person
from config.logger import configure_logger
from config.settings import get_settings
from domain.contracts.pb_nalog.pb_nalog_client import PbNalogClientContract
from domain.contracts.proxy.proxy_provider import ProxyProviderContract
from domain.entities import DomainOrganization, DomainPerson
from domain.use_cases.exceptions import CaptchaRequiredError

logger = configure_logger("HTTPClient")
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
    async def _request(self, method: str, url: str, proxy: str | None, init_cookie: bool = False, **kwargs):
        try:
            await asyncio.sleep(random.uniform(1.5, 3.0))
            
            async with self._session.request(method=method, url=url, proxy=proxy, **kwargs) as response:
                if response.status >= 400:
                    body = await response.text()
                    
                    if "pbSearchCaptcha" in body:
                        logger.warning("pb.nalog запросил капчу")
                        if proxy:
                            await self._proxy_provider.mark_bad(proxy)
                        raise CaptchaRequiredError("pb.nalog запросил капчу")

                    logger.error(
                        f"pb.nalog ответил ошибкой: status={response.status} url={url} body={body[:500]}"
                    )
                    response.raise_for_status()

                if init_cookie:
                    response.raise_for_status()
                    await response.read()
                    return
                
                data = await response.json(content_type=None)
                return data

        except TimeoutError:
            logger.warning(f"Таймаут запроса к pb.nalog: {method} {url} через прокси {proxy}")
            if proxy:
                await self._proxy_provider.mark_bad(proxy)
            raise
        except (ClientProxyConnectionError, ClientConnectionError):
            logger.warning(f"Ошибка подключения к ресурсу pb.nalog через прокси {proxy}")
            if proxy:
                await self._proxy_provider.mark_bad(proxy)
            raise
        except InvalidURL as e:
            logger.warning(f"Некорректный URL прокси: {proxy}, ошибка: {e}")
            if proxy:
                await self._proxy_provider.mark_bad(proxy)
            raise
        except ClientError as e:
            logger.warning(f"Клиентская ошибка через прокси {proxy}: {e}")
            if proxy:
                await self._proxy_provider.mark_bad(proxy)
            raise

    async def _with_proxy_retry(self, coro, *args, **kwargs):
        if not self._proxy_provider._proxies:
            return await coro(None, *args, **kwargs)

        max_attempts = len(self._proxy_provider._proxies)
        last_exception = None

        for attempt in range(max_attempts):
            proxy = await self._proxy_provider.get_proxy()
            if not proxy:
                logger.error("Нет доступных прокси")
                raise RuntimeError("Нет доступных прокси")

            try:
                return await coro(proxy, *args, **kwargs)
            except (TimeoutError, ClientError, ClientProxyConnectionError, ClientConnectionError, InvalidURL) as e:
                logger.warning(f"Ошибка подключения к прокси {proxy}: {e}, будет использован следующий")
                await self._proxy_provider.mark_bad(proxy)
                last_exception = e
                continue
            except Exception as e:
                logger.warning(f"Неизвестная ошибка прокси {proxy}: {e}, будет использован следующий")
                await self._proxy_provider.mark_bad(proxy)
                last_exception = e
                continue

        raise RuntimeError(f"Все прокси недоступны: {last_exception}") from last_exception

    async def _ensure_cookie(self) -> None:
        if self._cookie_initialized:
            return

        async def _do_get_cookie(proxy: str) -> None:
            await self._request(
                method="GET",
                url=settings.pb_nalog_base_url,
                proxy=proxy,
                init_cookie=True
            )

        try:
            await self._with_proxy_retry(_do_get_cookie)
            self._cookie_initialized = True
            logger.info("Куки успешно получены")
        except Exception as e:
            logger.error(f"Не удалось получить куки ни через один прокси: {e}")
            raise

    async def _poll_result(self, task_id: str, proxy: str | None, timeout: float = 8.0, delay: float = 0.5) -> dict:
        async def _poll_loop():
            while True:
                result = await self._request("POST", settings.pb_nalog_search_url, proxy=proxy, data={"method": "get-response", "id": task_id})
                if result is not None:
                    return result
                await asyncio.sleep(delay)

        try:
            return await asyncio.wait_for(_poll_loop(), timeout=timeout)
        except TimeoutError:
            raise TimeoutError(f"Задача {task_id} не готова за {timeout} секунд")

    async def _map_persons(self, raw: dict) -> list[Person]:
        items = raw.get("upr", {}).get("data", [])
        return [
            DomainPerson(**Person.model_validate(item).model_dump())
            for item in items
        ]

    async def _map_orgranizations(self, raw: dict) -> list[Organization]:
        items = raw.get("ul", {}).get("data", [])
        return [
            DomainOrganization(**Organization.model_validate(item).model_dump())
            for item in items
        ]
    
    async def search_persons(self, search_string: str) -> list[Person]:
        await self._ensure_cookie()

        async def _do_search(proxy: str) -> dict:
            payload = SearchPersonsRequestPayload(queryUpr=search_string)
            task = await self._request("POST", settings.pb_nalog_search_url, proxy=proxy, data=payload.model_dump())
            response = await self._poll_result(task["id"], proxy)
            return response

        raw = await self._with_proxy_retry(_do_search)
        return await self._map_persons(raw)

    async def get_organizations(self, name: str, token: str) -> list[Organization]:
        await self._ensure_cookie()

        async def _do_get_org(proxy: str) -> dict:
            payload = GetOrganizationsRequestPayload(queryUl=name, token=token)
            task = await self._request("POST", settings.pb_nalog_search_url, proxy=proxy, data=payload.model_dump())
            response = await self._poll_result(task["id"], proxy)
            return response

        raw = await self._with_proxy_retry(_do_get_org)
        return await self._map_orgranizations(raw)