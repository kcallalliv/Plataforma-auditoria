import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from app.config import settings
from app.link_validator import LinkValidatorService
from app.models import RunLinkValidatorRequest

logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))

app = FastAPI(
    title="Link Validator API",
    version="1.0.0",
    description="Módulo 3 - Link Validator"
)

service = LinkValidatorService()

@app.get("/health")
def health():
    return {"status": "ok", "service": settings.app_name}

@app.post("/run/link-validator")
def run_link_validator(payload: RunLinkValidatorRequest):
    try:
        result = service.run(payload)
        return JSONResponse(content=result, status_code=200)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))