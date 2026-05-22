from typing import Optional
from pydantic import BaseModel

class RunTaggingValidatorRequest(BaseModel):
    source_run_id: Optional[str] = None
    technical_run_id: Optional[str] = None
    seo_run_id: Optional[str] = None
    only_status_200: bool = True
    max_urls: Optional[int] = None
    device_priority: str = "mobile"
    device_profile: Optional[str] = None

class RunTaggingValidatorResponse(BaseModel):
    run_id: str
    status: str
    total_urls_target: int
    total_urls_processed: int
    total_urls_ok: int
    total_urls_error: int
    duration_seconds: float
    message: str