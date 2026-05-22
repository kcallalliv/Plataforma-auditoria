from typing import Optional
from pydantic import BaseModel

class RunPerformanceValidatorRequest(BaseModel):
    source_run_id: Optional[str] = None
    only_priority: bool = True
    max_urls: Optional[int] = 20
    strategies: list[str] = ["mobile", "desktop"]

class RunPerformanceValidatorResponse(BaseModel):
    run_id: str
    status: str
    total_urls_target: int
    total_urls_processed: int
    total_measurements: int
    duration_seconds: float
    message: str