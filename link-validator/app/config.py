import os
from dataclasses import dataclass

@dataclass
class Settings:
    project_id: str = os.getenv("PROJECT_ID", "prd-claro-mktg-data-storage")
    dataset_id: str = os.getenv("DATASET_ID", "seo_audit")
    app_name: str = os.getenv("APP_NAME", "link-validator")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    request_timeout_seconds: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "20"))
    request_user_agent: str = os.getenv(
        "REQUEST_USER_AGENT",
        "Mozilla/5.0 (compatible; LinkValidator/1.0; +https://www.claro.com.pe/)"
    )

settings = Settings()