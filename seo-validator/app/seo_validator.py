import logging
import time
import uuid
from datetime import date, datetime

import requests
from bs4 import BeautifulSoup

from app.bigquery_repository import BigQueryRepository
from app.config import settings
from app.utils import (
    build_seo_findings,
    get_h1_analysis,
    detect_schema,
    detect_terms_conditions_hint,
    detect_service_keywords,
    get_canonical,
    get_images_without_alt,
    get_lang,
    get_meta_content,
)

logger = logging.getLogger(__name__)

class SEOValidatorService:
    def __init__(self, repository: BigQueryRepository | None = None):
        self.repository = repository or BigQueryRepository()

    def run(self, payload):
        start = time.time()
        run_id = f"seo_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
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

        headers = {"User-Agent": settings.request_user_agent}

        for row in urls:
            page_url = row["page_url"]
            normalized_url = row["normalized_url"]
            url_hash = row["url_hash"]
            url_type = row["url_type"]
            page_group = row["page_group"]

            checked_ts = datetime.utcnow().isoformat()
            seo_status = "ok"
            error_message = None

            try:
                response = requests.get(page_url, timeout=settings.request_timeout_seconds, headers=headers)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")

                title = soup.title.string.strip() if soup.title and soup.title.string else None
                meta_description = get_meta_content(soup, name="description")
                canonical_url = get_canonical(soup)
                robots_content = get_meta_content(soup, name="robots")
                lang = get_lang(soup)

                h1_analysis = get_h1_analysis(soup)
                h1_count = h1_analysis["h1_count"]
                images_total, images_without_alt = get_images_without_alt(soup)

                has_schema, schema_types = detect_schema(soup)

                result = {
                    "run_id": run_id,
                    "source_run_id": payload.source_run_id,
                    "technical_run_id": payload.technical_run_id,
                    "audit_date": str(audit_date),
                    "checked_ts": checked_ts,
                    "page_url": page_url,
                    "normalized_url": normalized_url,
                    "url_hash": url_hash,
                    "url_type": url_type,
                    "page_group": page_group,
                    "title": title,
                    "title_length": len(title) if title else None,
                    "has_title": bool(title),
                    "meta_description": meta_description,
                    "meta_description_length": len(meta_description) if meta_description else None,
                    "has_meta_description": bool(meta_description),
                    "h1_count": h1_count,
                    "has_h1": h1_count > 0,
                    "has_duplicated_h1": h1_analysis["has_duplicated_h1"],
                    "duplicated_h1_values": h1_analysis["duplicated_h1_values"],
                    "canonical_url": canonical_url,
                    "has_canonical": bool(canonical_url),
                    "robots_content": robots_content,
                    "has_noindex": bool(robots_content and "noindex" in robots_content.lower()),
                    "lang": lang,
                    "has_lang": bool(lang),
                    "has_og_title": bool(get_meta_content(soup, property_name="og:title")),
                    "has_og_description": bool(get_meta_content(soup, property_name="og:description")),
                    "has_twitter_card": bool(get_meta_content(soup, name="twitter:card")),
                    "images_total": images_total,
                    "images_without_alt": images_without_alt,
                    "has_schema": has_schema,
                    "schema_types": schema_types,
                    "seo_status": seo_status,
                    "error_message": error_message,
                    "has_terms_conditions_hint": detect_terms_conditions_hint(soup),
                    "has_service_keywords": detect_service_keywords(soup),
                }

                result_to_insert = result.copy()
                result_to_insert.pop("has_duplicated_h1", None)
                result_to_insert.pop("duplicated_h1_values", None)

                results.append(result_to_insert)
                total_ok += 1

                findings = build_seo_findings(result)
                for f in findings:
                    findings_rows.append({
                        "run_id": run_id,
                        "audit_date": str(audit_date),
                        "created_ts": datetime.utcnow().isoformat(),
                        "page_url": page_url,
                        "normalized_url": normalized_url,
                        "finding_code": f["finding_code"],
                        "finding_category": f["finding_category"],
                        "severity": f["severity"],
                        "finding_detail": f["finding_detail"],
                        "recommendation": f["recommendation"],
                        "component_type": f["component_type"],
                        "component_id": f["component_id"],
                        "component_selector": f["component_selector"],
                        "html_section": f["html_section"],
                        "element_value": f["element_value"],
                        "expected_value": f["expected_value"],
                    })

            except Exception as exc:
                total_error += 1
                errors.append(f"{page_url}: {str(exc)}")
                results.append({
                    "run_id": run_id,
                    "source_run_id": payload.source_run_id,
                    "technical_run_id": payload.technical_run_id,
                    "audit_date": str(audit_date),
                    "checked_ts": checked_ts,
                    "page_url": page_url,
                    "normalized_url": normalized_url,
                    "url_hash": url_hash,
                    "url_type": url_type,
                    "page_group": page_group,
                    "title": None,
                    "title_length": None,
                    "has_title": False,
                    "meta_description": None,
                    "meta_description_length": None,
                    "has_meta_description": False,
                    "h1_count": 0,
                    "has_h1": False,
                    "canonical_url": None,
                    "has_canonical": False,
                    "robots_content": None,
                    "has_noindex": False,
                    "lang": None,
                    "has_lang": False,
                    "has_og_title": False,
                    "has_og_description": False,
                    "has_twitter_card": False,
                    "images_total": 0,
                    "images_without_alt": 0,
                    "has_schema": False,
                    "schema_types": None,
                    "seo_status": "error",
                    "error_message": str(exc),
                })

        duration_seconds = round(time.time() - start, 3)
        status = "success" if total_error == 0 else ("partial_success" if total_ok > 0 else "failed")

        run_log = {
            "run_id": run_id,
            "source_run_id": payload.source_run_id,
            "technical_run_id": payload.technical_run_id,
            "run_ts": datetime.utcnow().isoformat(),
            "audit_date": str(audit_date),
            "execution_status": status,
            "total_urls_target": len(urls),
            "total_urls_processed": len(results),
            "total_urls_ok": total_ok,
            "total_urls_error": total_error,
            "duration_seconds": duration_seconds,
            "error_summary": " | ".join(errors[:10]) if errors else None,
        }

        self.repository.insert_rows("seo_validation_run_log", [run_log])
        self.repository.insert_rows("seo_validation_results", results)
        self.repository.insert_rows("seo_validation_findings", findings_rows)

        return {
            "run_id": run_id,
            "status": status,
            "total_urls_target": len(urls),
            "total_urls_processed": len(results),
            "total_urls_ok": total_ok,
            "total_urls_error": total_error,
            "duration_seconds": duration_seconds,
            "message": "SEO Validator ejecutado correctamente"
        }
    
