import asyncio
from contextlib import asynccontextmanager

from aiohttp import ClientSession
from fastapi import FastAPI

from adapters.api.route import router
from adapters.messaging.worker import worker_start_polling
from adapters.pb_nalog.http_client.client_instance import HTTPClient
from adapters.pb_nalog.proxy.proxy_provider import ProxyProvider
from config.logger import configure_logger
from config.settings import get_settings

logger = configure_logger("MAIN")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    session = ClientSession()
    proxy_provider = ProxyProvider(proxy_urls=settings.proxy_url_list)
    http_client = HTTPClient(http_session=session, proxy_provider=proxy_provider)

    app.state.http_session = session
    app.state.http_client = http_client

    worker_task = asyncio.create_task(worker_start_polling(client=http_client))

    logger.info("Задачи созданы, http client и proxy инициализированы")

    yield

    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        logger.info("Воркер успешно остановлен")
    await session.close()


app = FastAPI(
    title="Data Extraction Service",
    description="Service for extracting information about directors and their associated companies.",
    root_path="/api/v1",
    openapi_url="/openapi.json" if settings.development else None,
    docs_url="/docs" if settings.development else None,
    redoc_url="/redoc" if settings.development else None,
    lifespan=lifespan,
)

app.include_router(router)