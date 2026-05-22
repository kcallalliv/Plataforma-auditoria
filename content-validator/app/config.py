import os
from dataclasses import dataclass

@dataclass
class Settings:
    project_id: str = os.getenv("PROJECT_ID", "prd-claro-mktg-data-storage")
    dataset_id: str = os.getenv("DATASET_ID", "seo_audit")
    app_name: str = os.getenv("APP_NAME", "content-validator")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    request_timeout_seconds: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "20"))
    request_user_agent: str = os.getenv("REQUEST_USER_AGENT", "Mozilla/5.0 (compatible; ContentValidator/1.0; +https://www.claro.com.pe/)")
    playwright_enabled: bool = os.getenv("PLAYWRIGHT_ENABLED", "false").lower() == "true"
    allowed_fonts: str = os.getenv("ALLOWED_FONTS", "Roboto,AMX")
    forbidden_terms: str = os.getenv("FORBIDDEN_TERMS", "gratis total,sin contrato eterno")
    competitor_terms: str = os.getenv("COMPETITOR_TERMS", "movistar,entel,bitel")
    placeholder_terms: str = os.getenv("PLACEHOLDER_TERMS", "lorem ipsum,placeholder")
    required_disclaimers: str = os.getenv("REQUIRED_DISCLAIMERS", "")

settings = Settings()