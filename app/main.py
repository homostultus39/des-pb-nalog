from fastapi import FastAPI

from config.settings import get_settings


settings = get_settings()

app = FastAPI(
    title="Data Extraction Service",
    description="Service for extracting information about directors and their associated companies.",
    root_path="/api/v1",
    openapi_url="/openapi.json" if settings.development else None,
    docs_url="/docs" if settings.development else None,
    redoc_url="/redoc" if settings.development else None 
)