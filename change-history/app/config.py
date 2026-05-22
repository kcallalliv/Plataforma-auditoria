import os
from dataclasses import dataclass

@dataclass
class Settings:
    project_id: str = os.getenv("PROJECT_ID", "prd-claro-mktg-data-storage")
    dataset_id: str = os.getenv("DATASET_ID", "seo_audit")
    app_name: str = os.getenv("APP_NAME", "change-history")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()