import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from app.config import settings
from app.models import RunSEOValidatorRequest
from app.seo_validator import SEOValidatorService

logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))

app = FastAPI(
    title="SEO Validator API",
    version="1.0.0",
    description="Módulo 3 - SEO Validator"
)

service = SEOValidatorService()

@app.get("/health")
def health():
    return {"status": "ok", "service": settings.app_name}

@app.post("/run/seo-validator")
def run_seo_validator(payload: RunSEOValidatorRequest):
    try:
        result = service.run(payload)
        return JSONResponse(content=result, status_code=200)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))