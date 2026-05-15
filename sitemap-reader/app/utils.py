import hashlib
import logging
from datetime import datetime
from typing import Optional, Tuple
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

logger = logging.getLogger(__name__)

TRACKING_PARAMS_PREFIXES = ("utm_",)
TRACKING_PARAMS_EXACT = {"gclid", "fbclid", "msclkid"}

def parse_lastmod(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None

    candidates = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
    ]

    for fmt in candidates:
        try:
            dt = datetime.strptime(value, fmt)
            if dt.tzinfo:
                return dt.replace(tzinfo=None)
            return dt
        except ValueError:
            continue

    logger.warning("No se pudo parsear lastmod: %s", value)
    return None

def remove_tracking_params(query: str) -> str:
    if not query:
        return ""

    filtered = []
    for key, value in parse_qsl(query, keep_blank_values=True):
        key_lower = key.lower()
        if key_lower in TRACKING_PARAMS_EXACT:
            continue
        if any(key_lower.startswith(prefix) for prefix in TRACKING_PARAMS_PREFIXES):
            continue
        filtered.append((key, value))

    filtered.sort(key=lambda x: x[0])
    return urlencode(filtered, doseq=True)

def normalize_url(raw_url: str) -> str:
    parsed = urlparse(raw_url.strip())

    scheme = "https" if parsed.scheme in ("http", "https") else parsed.scheme
    netloc = parsed.netloc.lower()
    path = parsed.path or "/"

    if path != "/" and path.endswith("/"):
        path = path[:-1]

    query = remove_tracking_params(parsed.query)

    normalized = urlunparse((scheme, netloc, path, "", query, ""))
    return normalized

def normalize_path(path: str) -> str:
    if not path:
        return "/"
    path = path.strip().lower()
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    return path

def get_url_hash(normalized_url: str) -> str:
    return hashlib.sha256(normalized_url.encode("utf-8")).hexdigest()

def get_domain_path_query(url: str) -> Tuple[str, str, Optional[str]]:
    parsed = urlparse(url)
    return parsed.netloc.lower(), parsed.path or "/", parsed.query or None

def has_excluded_extension(path: str, excluded_extensions: list[str]) -> bool:
    lower_path = path.lower()
    return any(lower_path.endswith(ext) for ext in excluded_extensions)

def classify_url(path: str) -> tuple[str, str, str]:
    clean_path = normalize_path(path)

    if clean_path == "/":
        return "home", "comercial", "high"

    if clean_path.startswith("/personas/movil/postpago"):
        return "service_postpago", "comercial", "high"

    if clean_path.startswith("/personas/movil/prepago"):
        return "service_prepago", "comercial", "high"

    if clean_path.startswith("/portabilidad"):
        return "service_portabilidad", "comercial", "high"

    if clean_path.startswith("/renovacion"):
        return "service_renovacion", "comercial", "high"

    if clean_path.startswith("/personas/hogar/internet"):
        return "service_hogar_internet", "comercial", "high"

    if clean_path.startswith("/personas/beneficios/movil/cobertura-internacional"):
        return "service_cobertura_internacional", "comercial", "high"

    if "/beneficios" in clean_path:
        return "beneficios", "comercial", "medium"

    if "/cobertura" in clean_path:
        return "cobertura", "comercial", "medium"

    if "/soporte" in clean_path or "/ayuda" in clean_path or "/faq" in clean_path:
        return "support", "soporte", "medium"

    if "/terminos-y-condiciones" in clean_path or "/legal" in clean_path:
        return "legal", "informativa", "medium"

    return "other", "other", "low"

def is_valid_domain(domain: str, allowed_domains: list[str]) -> bool:
    return domain.lower() in {d.lower() for d in allowed_domains}

def compact_error(errors: list[str], max_items: int = 10) -> Optional[str]:
    if not errors:
        return None
    return " | ".join(errors[:max_items])

def safe_float(value: Optional[str]) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None