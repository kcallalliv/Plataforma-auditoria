import hashlib
import logging
import time
import uuid
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from app.bigquery_repository import BigQueryRepository
from app.config import settings
from app.runtime_capture import run_typography_capture

logger = logging.getLogger(__name__)

def _csv_terms(raw: str) -> list[str]:
    return [item.strip().lower() for item in (raw or "").split(",") if item.strip()]

class ContentValidatorService:
    def __init__(self, repository: BigQueryRepository | None = None):
        self.repository = repository or BigQueryRepository()

    def run(self, payload):
        start = time.time()
        run_id = f"cont_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        urls = self.repository.get_urls_to_validate(payload.source_run_id, payload.max_urls)

        results, findings, errors = [], [], []
        headers = {"User-Agent": settings.request_user_agent}
        forbidden_terms = _csv_terms(settings.forbidden_terms)
        competitor_terms_cfg = _csv_terms(settings.competitor_terms)
        placeholder_terms = _csv_terms(settings.placeholder_terms)
        required_disclaimers = _csv_terms(settings.required_disclaimers)

        for row in urls:
            page_url = row["page_url"]
            try:
                response = requests.get(page_url, timeout=settings.request_timeout_seconds, headers=headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                text = soup.get_text(" ", strip=True).lower()

                detected_terms = [t for t in forbidden_terms if t in text]
                competitor_terms = [t for t in competitor_terms_cfg if t in text]
                placeholder_detected = any(t in text for t in placeholder_terms)
                missing_disclaimers = [d for d in required_disclaimers if d not in text]
                word_count = len([w for w in text.split() if w])
                thin_content_detected = word_count < 120
                content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()

                allowed_fonts = [font.strip() for font in settings.allowed_fonts.split(",") if font.strip()]
                runtime_font_findings = []
                if settings.playwright_enabled:
                    runtime_capture = run_typography_capture(page_url, payload.device_profile, allowed_fonts)
                    runtime_font_findings = runtime_capture.get("findings", [])

                invalid_button_font_count = sum(1 for f in runtime_font_findings if str(f.get("finding_code")) in {"BRAND_INVALID_FONT_BUTTON", "BRAND_INVALID_FONT_CTA"})
                invalid_text_font_count = sum(1 for f in runtime_font_findings if str(f.get("finding_code")) in {"BRAND_INVALID_FONT_TEXT", "BRAND_INVALID_FONT_NAV", "BRAND_INVALID_FONT_FOOTER"})
                failed_brand_font_count = sum(1 for f in runtime_font_findings if str(f.get("finding_code")) == "BRAND_FONT_RESOURCE_FAILED")
                brand_font_status = "ok" if len(runtime_font_findings) == 0 else "issues_detected"

                result_row = {
                    "content_run_id": run_id,
                    "source_run_id": payload.source_run_id,
                    "page_url": page_url,
                    "device_profile": payload.device_profile,
                    "page_type": row.get("url_type"),
                    "detected_terms": detected_terms,
                    "missing_disclaimers": missing_disclaimers,
                    "expired_campaign_detected": False,
                    "competitor_terms_detected": competitor_terms,
                    "placeholder_detected": placeholder_detected,
                    "word_count": word_count,
                    "thin_content_detected": thin_content_detected,
                    "duplicate_content_hash": content_hash,
                    "invalid_font_count": len(runtime_font_findings),
                    "invalid_button_font_count": invalid_button_font_count,
                    "invalid_text_font_count": invalid_text_font_count,
                    "failed_brand_font_count": failed_brand_font_count,
                    "brand_font_status": brand_font_status,
                    "created_ts": datetime.utcnow().isoformat(),
                }
                results.append(result_row)

                for font_finding in runtime_font_findings:
                    findings.append({
                        "content_run_id": run_id,
                        "source_run_id": payload.source_run_id,
                        "page_url": page_url,
                        **font_finding,
                        "created_ts": datetime.utcnow().isoformat(),
                    })

                if detected_terms:
                    findings.append({
                        "content_run_id": run_id,
                        "source_run_id": payload.source_run_id,
                        "page_url": page_url,
                        "rule_id": "CONT_FORBIDDEN_TERMS",
                        "finding_type": "forbidden_terms",
                        "severity": "Alta",
                        "element_tag": "body",
                        "element_id": None,
                        "element_class": None,
                        "element_text": ", ".join(detected_terms),
                        "css_selector": "body",
                        "xpath": "/html/body",
                        "dom_section": "body",
                        "html_snippet": response.text[:500],
                        "expected_value": "Sin términos prohibidos",
                        "actual_value": ", ".join(detected_terms),
                        "computed_font_family": None,
                        "computed_font_size": None,
                        "computed_font_weight": None,
                        "created_ts": datetime.utcnow().isoformat(),
                    })
                if missing_disclaimers:
                    findings.append({
                        "content_run_id": run_id,
                        "source_run_id": payload.source_run_id,
                        "page_url": page_url,
                        "rule_id": "CONT_MISSING_DISCLAIMER",
                        "finding_type": "missing_disclaimer",
                        "severity": "Alta",
                        "element_tag": "body",
                        "element_id": None,
                        "element_class": None,
                        "element_text": None,
                        "css_selector": "body",
                        "xpath": "/html/body",
                        "dom_section": "body",
                        "html_snippet": response.text[:500],
                        "expected_value": ", ".join(required_disclaimers) if required_disclaimers else "Disclaimer obligatorio presente",
                        "actual_value": ", ".join(missing_disclaimers),
                        "computed_font_family": None,
                        "computed_font_size": None,
                        "computed_font_weight": None,
                        "created_ts": datetime.utcnow().isoformat(),
                    })
                if thin_content_detected:
                    findings.append({
                        "content_run_id": run_id,
                        "source_run_id": payload.source_run_id,
                        "page_url": page_url,
                        "rule_id": "CONT_THIN_CONTENT",
                        "finding_type": "thin_content",
                        "severity": "Media",
                        "element_tag": "body",
                        "element_id": None,
                        "element_class": None,
                        "element_text": None,
                        "css_selector": "body",
                        "xpath": "/html/body",
                        "dom_section": "body",
                        "html_snippet": response.text[:500],
                        "expected_value": ">= 120 palabras",
                        "actual_value": str(word_count),
                        "computed_font_family": None,
                        "computed_font_size": None,
                        "computed_font_weight": None,
                        "created_ts": datetime.utcnow().isoformat(),
                    })
            except Exception as exc:
                errors.append(f"{page_url}: {str(exc)}")

        status = "success" if not errors else ("partial_success" if results else "failed")
        duration_seconds = round(time.time() - start, 3)

        run_log = {
            "content_run_id": run_id,
            "source_run_id": payload.source_run_id,
            "started_ts": datetime.utcnow().isoformat(),
            "ended_ts": datetime.utcnow().isoformat(),
            "status": status,
            "created_ts": datetime.utcnow().isoformat(),
        }

        self.repository.insert_rows("content_validation_run_log", [run_log])
        self.repository.insert_rows("content_validation_results", results)
        self.repository.insert_rows("content_validation_findings", findings)

        return {
            "run_id": run_id,
            "status": status,
            "total_urls_target": len(urls),
            "total_urls_processed": len(results),
            "total_findings": len(findings),
            "duration_seconds": duration_seconds,
            "message": "Content Validator ejecutado correctamente"
        }