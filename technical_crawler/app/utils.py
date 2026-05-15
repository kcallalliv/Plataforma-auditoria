import hashlib
from urllib.parse import urlparse

def get_url_hash(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()

def severity_from_result(status_code, response_time_ms, page_group, is_priority, crawl_status):
    if crawl_status in ("timeout", "ssl_error", "connection_error"):
        return "alta"

    if status_code is None:
        return "alta"

    if status_code >= 500:
        return "alta"

    if status_code == 404:
        return "alta"

    if response_time_ms is not None:
        if is_priority and response_time_ms > 2000:
            return "alta"
        if response_time_ms > 1000:
            return "media"

    if 300 <= status_code < 400:
        return "media"

    return "baja"


def build_finding(status_code, response_time_ms, page_group, is_priority, crawl_status):
    severity = severity_from_result(status_code, response_time_ms, page_group, is_priority, crawl_status)

    base_location = {
        "component_type": "url",
        "component_id": None,
        "component_selector": None,
        "html_section": "http_response",
    }

    if crawl_status == "timeout":
        return {
            "finding_code": "TECH_TIMEOUT",
            "finding_category": "technical",
            "severity": severity,
            "finding_detail": "La URL excedió el tiempo máximo de respuesta",
            "recommendation": "Revisar backend, CDN y tiempos de carga",
            **base_location,
            "element_value": crawl_status,
            "expected_value": "Respuesta dentro del timeout configurado",
        }

    if crawl_status == "ssl_error":
        return {
            "finding_code": "TECH_SSL",
            "finding_category": "technical",
            "severity": severity,
            "finding_detail": "La URL presentó error SSL",
            "recommendation": "Revisar certificado y cadena TLS",
            **base_location,
            "element_value": crawl_status,
            "expected_value": "Certificado SSL válido",
        }

    if crawl_status == "connection_error":
        return {
            "finding_code": "TECH_CONN",
            "finding_category": "technical",
            "severity": severity,
            "finding_detail": "La URL no pudo ser alcanzada",
            "recommendation": "Revisar disponibilidad y red",
            **base_location,
            "element_value": crawl_status,
            "expected_value": "URL alcanzable",
        }

    if status_code is not None and status_code >= 500:
        return {
            "finding_code": "HTTP_5XX",
            "finding_category": "http",
            "severity": severity,
            "finding_detail": f"La URL respondió con {status_code}",
            "recommendation": "Revisar aplicación o infraestructura",
            **base_location,
            "element_value": str(status_code),
            "expected_value": "HTTP 200",
        }

    if status_code == 404:
        return {
            "finding_code": "HTTP_404",
            "finding_category": "http",
            "severity": severity,
            "finding_detail": "La URL respondió 404",
            "recommendation": "Corregir ruta o remover del inventario",
            **base_location,
            "element_value": "404",
            "expected_value": "HTTP 200",
        }

    if status_code is not None and 300 <= status_code < 400:
        return {
            "finding_code": "HTTP_3XX",
            "finding_category": "redirect",
            "severity": severity,
            "finding_detail": f"La URL respondió con redirect {status_code}",
            "recommendation": "Validar si el redirect es esperado o corregir la URL final.",
            **base_location,
            "element_value": str(status_code),
            "expected_value": "HTTP 200",
        }

    if response_time_ms is not None and response_time_ms > 2000:
        return {
            "finding_code": "SLOW_RESPONSE",
            "finding_category": "latency",
            "severity": severity,
            "finding_detail": f"La URL tardó {response_time_ms:.2f} ms",
            "recommendation": "Optimizar backend, caché o recursos",
            **base_location,
            "element_value": f"{response_time_ms:.2f} ms",
            "expected_value": "<= 2000 ms",
        }

    if response_time_ms is not None and response_time_ms > 1000:
        return {
            "finding_code": "MEDIUM_RESPONSE",
            "finding_category": "latency",
            "severity": severity,
            "finding_detail": f"La URL tardó {response_time_ms:.2f} ms",
            "recommendation": "Monitorear y optimizar",
            **base_location,
            "element_value": f"{response_time_ms:.2f} ms",
            "expected_value": "<= 1000 ms",
        }

    return None