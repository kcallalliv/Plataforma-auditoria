import os
from dataclasses import dataclass

@dataclass
class Settings:
    project_id: str = os.getenv("PROJECT_ID", "prd-claro-mktg-data-storage")
    dataset_id: str = os.getenv("DATASET_ID", "seo_audit")
    app_name: str = os.getenv("APP_NAME", "performance-validator")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    pagespeed_api_key: str = os.getenv("PAGESPEED_API_KEY", "")
    pagespeed_base_url: str = os.getenv("PAGESPEED_BASE_URL", "https://www.googleapis.com/pagespeedonline/v5/runPagespeed")
    pagespeed_timeout_seconds: int = int(os.getenv("PAGESPEED_TIMEOUT_SECONDS", "30"))
    pagespeed_max_retries: int = int(os.getenv("PAGESPEED_MAX_RETRIES", "2"))
    pagespeed_max_workers: int = int(os.getenv("PAGESPEED_MAX_WORKERS", "4"))
    pagespeed_sleep_ms: int = int(os.getenv("PAGESPEED_SLEEP_MS", "150"))

settings = Settings()