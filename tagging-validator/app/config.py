import os
from dataclasses import dataclass

MOBILE_USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0 Mobile Safari/537.36"
)

@dataclass
class Settings:
    project_id: str = os.getenv("PROJECT_ID", "")
    dataset_id: str = os.getenv("DATASET_ID", "seo_audit")
    app_name: str = os.getenv("APP_NAME", "tagging-validator")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    request_timeout_seconds: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "20"))
    request_user_agent: str = os.getenv("REQUEST_USER_AGENT", MOBILE_USER_AGENT)
    default_device_priority: str = os.getenv("DEFAULT_DEVICE_PRIORITY", "mobile")

settings = Settings()