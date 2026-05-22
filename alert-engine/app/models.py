from typing import Optional
from pydantic import BaseModel

class RunAlertEngineRequest(BaseModel):
    source_run_id: Optional[str] = None
    technical_run_id: Optional[str] = None

class RunAlertEngineResponse(BaseModel):
    run_id: str
    status: str
    total_alerts: int
    duration_seconds: float
    message: str