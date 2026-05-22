import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from app.config import settings
from app.content_validator import ContentValidatorService
from app.models import RunContentValidatorRequest

logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))

app = FastAPI(
    title="Content Validator API",
    version="1.0.0",
    description="Módulo 5 - Content/UI Compliance Validator"
)

service = ContentValidatorService()

@app.get("/health")
def health():
    return {"status": "ok", "service": settings.app_name}

@app.post("/run/content-validator")
def run_content_validator(payload: RunContentValidatorRequest):
    try:
        result = service.run(payload)
        return JSONResponse(content=result, status_code=200)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))