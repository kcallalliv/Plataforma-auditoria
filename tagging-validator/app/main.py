import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from app.config import settings
from app.models import RunTaggingValidatorRequest
from app.tagging_validator import TaggingValidatorService

logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))

app = FastAPI(
    title="Tagging Validator API",
    version="1.0.0",
    description="Módulo 4 - Tagging Validator"
)

service = TaggingValidatorService()

@app.get("/health")
def health():
    return {"status": "ok", "service": settings.app_name}

@app.post("/run/tagging-validator")
def run_tagging_validator(payload: RunTaggingValidatorRequest):
    try:
        result = service.run(payload)
        return JSONResponse(content=result, status_code=200)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))