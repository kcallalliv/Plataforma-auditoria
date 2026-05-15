import os
from dataclasses import dataclass, field
from typing import List

PRIORITY_PATHS = {
    "/personas/movil/postpago",
    "/portabilidad",
    "/renovacion",
    "/personas/hogar/internet",
    "/personas/beneficios/movil/cobertura-internacional",
    "/personas/movil/prepago",
    ##
    "/contactanos/ingresa-con-tu-mascota",
    "/personas/olo/centro-ayuda/cambio-de-clave",
}

@dataclass
class Settings:
    project_id: str = os.getenv("PROJECT_ID", "")
    dataset_id: str = os.getenv("DATASET_ID", "seo_audit")
    app_name: str = os.getenv("APP_NAME", "sitemap-reader")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    default_root_sitemaps: List[str] = field(
        default_factory=lambda: [
            s.strip()
            for s in os.getenv(
                "DEFAULT_ROOT_SITEMAPS",
                "https://www.claro.com.pe/sitemap.xml",
            ).split(",")
            if s.strip()
        ]
    )

    allowed_domains: List[str] = field(
        default_factory=lambda: [
            d.strip().lower()
            for d in os.getenv(
                "ALLOWED_DOMAINS",
                "www.claro.com.pe,claro.com.pe",
            ).split(",")
            if d.strip()
        ]
    )

    excluded_extensions: List[str] = field(
        default_factory=lambda: [
            e.strip().lower()
            for e in os.getenv(
                "EXCLUDED_EXTENSIONS",
                ".jpg,.jpeg,.png,.gif,.svg,.webp,.pdf,.xml,.css,.js,.ico",
            ).split(",")
            if e.strip()
        ]
    )

    request_timeout_seconds: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
    user_agent: str = os.getenv(
        "USER_AGENT",
        "Claro-Sitemap-Reader/1.0 (+https://www.claro.com.pe/)",
    )

settings = Settings()