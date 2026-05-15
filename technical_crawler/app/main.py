import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from app.config import settings
from app.models import RunTechnicalCrawlerRequest
from app.technical_crawler import TechnicalCrawlerService

logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))

app = FastAPI(
    title="Technical Crawler API",
    version="1.0.0",
    description="Módulo 2 - Technical Crawler"
)

service = TechnicalCrawlerService()

@app.get("/health")
def health():
    return {"status": "ok", "service": settings.app_name}

@app.post("/run/technical-crawler")
def run_technical_crawler(payload: RunTechnicalCrawlerRequest):
    try:
        result = service.run(payload)
        return JSONResponse(content=result, status_code=200)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))