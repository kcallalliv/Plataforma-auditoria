from typing import Optional
from pydantic import BaseModel

class RunContentValidatorRequest(BaseModel):
    source_run_id: Optional[str] = None
    max_urls: Optional[int] = 100
    device_profile: str = "mobile"

class RunContentValidatorResponse(BaseModel):
    run_id: str
    status: str
    total_urls_target: int
    total_urls_processed: int
    total_findings: int
    duration_seconds: float
    message: str