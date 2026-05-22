import logging
from fastapi import FastAPI

from app.alert_engine import AlertEngineService
from app.config import settings
from app.models import RunAlertEngineRequest, RunAlertEngineResponse

logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))

app = FastAPI(title="Alert Engine", version="1.0.0")
service = AlertEngineService()

@app.get("/health")
def health():
    return {"status": "ok", "service": settings.app_name}

@app.post("/run/alert-engine", response_model=RunAlertEngineResponse)
def run_alert_engine(payload: RunAlertEngineRequest):
    return service.run(payload)