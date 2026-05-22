import logging
from fastapi import FastAPI

from app.config import settings
from app.change_history import ChangeHistoryService
from app.models import RunChangeHistoryRequest, RunChangeHistoryResponse

logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))

app = FastAPI(title="Change History", version="1.0.0")
service = ChangeHistoryService()

@app.get("/health")
def health():
    return {"status": "ok", "service": settings.app_name}

@app.post("/run/change-history", response_model=RunChangeHistoryResponse)
def run_change_history(payload: RunChangeHistoryRequest):
    return service.run(payload)