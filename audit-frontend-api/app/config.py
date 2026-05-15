import os
from dataclasses import dataclass

@dataclass
class Settings:
    project_id: str = os.getenv("PROJECT_ID", "")
    dataset_id: str = os.getenv("DATASET_ID", "seo_audit")
    app_name: str = os.getenv("APP_NAME", "audit-frontend-api")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    default_page_size: int = int(os.getenv("DEFAULT_PAGE_SIZE", "50"))

settings = Settings()