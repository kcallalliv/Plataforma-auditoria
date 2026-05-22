from typing import Optional
from pydantic import BaseModel

class RunLinkValidatorRequest(BaseModel):
    source_run_id: Optional[str] = None
    technical_run_id: Optional[str] = None
    only_priority: bool = True
    max_urls: Optional[int] = 100
    device_profile: str = "mobile"

class RunLinkValidatorResponse(BaseModel):
    run_id: str
    status: str
    total_urls_target: int
    total_urls_processed: int
    total_links_processed: int
    total_links_broken: int
    duration_seconds: float
    message: str