from typing import Optional
from pydantic import BaseModel

class RunChangeHistoryRequest(BaseModel):
    source_run_id: Optional[str] = None
    technical_run_id: Optional[str] = None

class RunChangeHistoryResponse(BaseModel):
    run_id: str
    status: str
    total_changes: int
    duration_seconds: float
    message: str