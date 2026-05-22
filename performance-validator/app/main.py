import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from app.config import settings
from app.models import RunPerformanceValidatorRequest
from app.performance_validator import PerformanceValidatorService

logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))

app = FastAPI(
    title="Performance Validator API",
    version="1.0.0",
    description="Módulo 6 - Performance Validator"
)

service = PerformanceValidatorService()

@app.get("/health")
def health():
    return {"status": "ok", "service": settings.app_name}

@app.post("/run/performance-validator")
def run_performance_validator(payload: RunPerformanceValidatorRequest):
    try:
        result = service.run(payload)
        return JSONResponse(content=result, status_code=200)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))