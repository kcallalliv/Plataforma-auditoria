import logging
import time
import uuid
from datetime import date, datetime

import requests
from bs4 import BeautifulSoup

from app.bigquery_repository import BigQueryRepository
from app.config import settings
from app.utils import (
    build_tagging_findings,
    count_clickable_elements,
    count_cta_elements,
    count_form_elements,
    detect_datalayer,
    detect_double_tagging,
    detect_event_hint,
    detect_ga4,
    detect_gtm,
    get_script_text,
    has_required_params,
)

logger = logging.getLogger(__name__)

def normalize_severity(value: str | None) -> str:
    v = str(value or "").strip().lower()
    if "alta" in v or "crit" in v:
        return "Alta"
    if "media" in v:
        return "Media"
    return "Baja"

class TaggingValidatorService:
    def __init__(self, repository: BigQueryRepository | None = None):
        self.repository = repository or BigQueryRepository()

    def run(self, payload):
        start = time.time()
        run_id = f"tag_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        audit_date = date.today()

        urls = self.repository.get_urls_to_validate(
            source_run_id=payload.source_run_id,
            technical_run_id=payload.technical_run_id,
            only_status_200=payload.only_status_200,
            max_urls=payload.max_urls,
        )

        results = []
        findings_rows = []
        total_ok = 0
        total_error = 0
        errors = []

        effective_device_profile = payload.device_profile or payload.device_priority or "mobile"
        headers = {"User-Agent": settings.request_user_agent}

        for row in urls:
            page_url = row["page_url"]
            normalized_url = row["normalized_url"]
            normalized_path = row["normalized_path"]
            url_hash = row["url_hash"]
            url_type = row["url_type"]
            page_group = row["page_group"]

            checked_ts = datetime.utcnow().isoformat()

            try:
                response = requests.get(page_url, timeout=settings.request_timeout_seconds, headers=headers)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")
                script_text = get_script_text(soup)

                cta_elements_count = count_cta_elements(soup)
                form_elements_count = count_form_elements(soup)
                clickable_elements_count = count_clickable_elements(soup)
                has_interactions = (cta_elements_count > 0) or (form_elements_count > 0) or (clickable_elements_count > 0)

                duplicate_gtm, duplicate_ga4, duplicate_event, double_tagging = detect_double_tagging(script_text)

                result = {
                    "run_id": run_id,
                    "source_run_id": payload.source_run_id,
                    "technical_run_id": payload.technical_run_id,
                    "seo_run_id": payload.seo_run_id,
                    "audit_date": str(audit_date),
                    "checked_ts": checked_ts,
                    "page_url": page_url,
                    "normalized_url": normalized_url,
                    "url_hash": url_hash,
                    "normalized_path": normalized_path,
                    "url_type": url_type,
                    "page_group": page_group,
                    "device_priority": payload.device_priority,
                    "device_profile": effective_device_profile,
                    "has_gtm": detect_gtm(script_text),
                    "has_ga4": detect_ga4(script_text),
                    "has_datalayer": detect_datalayer(script_text),
                    "cta_elements_count": cta_elements_count,
                    "form_elements_count": form_elements_count,
                    "clickable_elements_count": clickable_elements_count,
                    "has_interactions": has_interactions,
                    "has_cta_click_hint": detect_event_hint(script_text, "cta_click"),
                    "has_generate_lead_hint": detect_event_hint(script_text, "generate_lead"),
                    "has_form_start_hint": detect_event_hint(script_text, "form_start"),
                    "has_form_submit_hint": detect_event_hint(script_text, "form_submit"),
                    "has_contact_click_hint": detect_event_hint(script_text, "contact_click"),
                    "has_whatsapp_click_hint": detect_event_hint(script_text, "whatsapp_click"),
                    "has_portabilidad_click_hint": detect_event_hint(script_text, "portabilidad_click"),
                    "has_renovacion_click_hint": detect_event_hint(script_text, "renovacion_click"),
                    "has_cobertura_click_hint": detect_event_hint(script_text, "cobertura_click"),
                    "cta_required_params": has_required_params(script_text, "cta"),
                    "lead_required_params": has_required_params(script_text, "lead"),
                    "form_required_params": has_required_params(script_text, "form"),
                    "duplicate_gtm_detected": duplicate_gtm,
                    "duplicate_ga4_detected": duplicate_ga4,
                    "duplicate_event_hint_detected": duplicate_event,
                    "double_tagging_detected": double_tagging,
                    "tagging_status": "ok",
                    "error_message": None,
                }

                results.append(result)
                total_ok += 1

                findings = build_tagging_findings(result)
                for f in findings:
                    findings_rows.append({
                        "run_id": run_id,
                        "audit_date": str(audit_date),
                        "created_ts": datetime.utcnow().isoformat(),
                        "page_url": page_url,
                        "normalized_url": normalized_url,
                        "finding_code": f["finding_code"],
                        "finding_category": f["finding_category"],
                        "severity": normalize_severity(f["severity"]),
                        "finding_detail": f["finding_detail"],
                        "recommendation": f["recommendation"],
                        "module_name": "M8 Tagging Validator",
                        "rule_id": f["finding_code"],
                        "component_type": f["component_type"],
                        "component_id": f["component_id"],
                        "component_selector": f["component_selector"],
                        "html_section": f["html_section"],
                        "element_value": f["element_value"],
                        "expected_value": f["expected_value"],
                        "actual_value": f["element_value"],
                        "element_id": f["component_id"],
                        "element_class": None,
                        "css_selector": f["component_selector"],
                        "xpath": None,
                    })

            except Exception as exc:
                total_error += 1
                errors.append(f"{page_url}: {str(exc)}")
                results.append({
                    "run_id": run_id,
                    "source_run_id": payload.source_run_id,
                    "technical_run_id": payload.technical_run_id,
                    "seo_run_id": payload.seo_run_id,
                    "audit_date": str(audit_date),
                    "checked_ts": checked_ts,
                    "page_url": page_url,
                    "normalized_url": normalized_url,
                    "url_hash": url_hash,
                    "normalized_path": normalized_path,
                    "url_type": url_type,
                    "page_group": page_group,
                    "device_priority": payload.device_priority,
                    "device_profile": effective_device_profile,
                    "has_gtm": False,
                    "has_ga4": False,
                    "has_datalayer": False,
                    "cta_elements_count": 0,
                    "form_elements_count": 0,
                    "clickable_elements_count": 0,
                    "has_interactions": False,
                    "has_cta_click_hint": False,
                    "has_generate_lead_hint": False,
                    "has_form_start_hint": False,
                    "has_form_submit_hint": False,
                    "has_contact_click_hint": False,
                    "has_whatsapp_click_hint": False,
                    "has_portabilidad_click_hint": False,
                    "has_renovacion_click_hint": False,
                    "has_cobertura_click_hint": False,
                    "cta_required_params": False,
                    "lead_required_params": False,
                    "form_required_params": False,
                    "duplicate_gtm_detected": False,
                    "duplicate_ga4_detected": False,
                    "duplicate_event_hint_detected": False,
                    "double_tagging_detected": False,
                    "tagging_status": "error",
                    "error_message": str(exc),
                })

        duration_seconds = round(time.time() - start, 3)
        status = "success" if total_error == 0 else ("partial_success" if total_ok > 0 else "failed")

        run_log = {
            "run_id": run_id,
            "source_run_id": payload.source_run_id,
            "technical_run_id": payload.technical_run_id,
            "seo_run_id": payload.seo_run_id,
            "run_ts": datetime.utcnow().isoformat(),
            "audit_date": str(audit_date),
            "execution_status": status,
            "device_priority": payload.device_priority,
            "device_profile": effective_device_profile,
            "total_urls_target": len(urls),
            "total_urls_processed": len(results),
            "total_urls_ok": total_ok,
            "total_urls_error": total_error,
            "duration_seconds": duration_seconds,
            "error_summary": " | ".join(errors[:10]) if errors else None,
        }

        self.repository.insert_rows("tagging_validation_run_log", [run_log])
        self.repository.insert_rows("tagging_validation_results", results)
        self.repository.insert_rows("tagging_validation_findings", findings_rows)

        return {
            "run_id": run_id,
            "status": status,
            "total_urls_target": len(urls),
            "total_urls_processed": len(results),
            "total_urls_ok": total_ok,
            "total_urls_error": total_error,
            "duration_seconds": duration_seconds,
            "message": "Tagging Validator ejecutado correctamente"
        }