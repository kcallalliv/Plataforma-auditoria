from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel

class RunTechnicalCrawlerRequest(BaseModel):
    source_run_id: Optional[str] = None
    only_priority: bool = True
    max_urls: Optional[int] = None
    timeout_seconds: Optional[int] = 20
    device_priority: str = "mobile"
    device_profile: Optional[str] = None
    device_profiles: Optional[list[str]] = None
    runtime_scan: bool = False

class RunTechnicalCrawlerResponse(BaseModel):
    run_id: str
    status: str
    total_urls_target: int
    total_urls_processed: int
    total_urls_ok: int
    total_urls_error: int
    duration_seconds: float
    message: str