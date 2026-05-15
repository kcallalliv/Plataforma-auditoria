import logging

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from app.config import settings
from app.models import RunSitemapReaderRequest
from app.sitemap_reader import SitemapReaderService

logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Sitemap Reader API",
    version="1.0.0",
    description="Módulo 1 - Sitemap Reader para auditoría web",
)

service = SitemapReaderService()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": settings.app_name}


@app.post("/run/sitemap-reader")
def run_sitemap_reader(payload: RunSitemapReaderRequest) -> JSONResponse:
    try:
        result = service.run(payload)
        return JSONResponse(content=result, status_code=200)
    except Exception as exc:
        logger.exception("Error ejecutando Sitemap Reader")
        raise HTTPException(status_code=500, detail=str(exc))