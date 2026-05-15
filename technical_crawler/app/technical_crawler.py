import logging
import time
import uuid
from datetime import date, datetime
from urllib.parse import urlparse

import requests

from app.bigquery_repository import BigQueryRepository
from app.config import settings
from app.utils import build_finding

logger = logging.getLogger(__name__)

class TechnicalCrawlerService:
    def __init__(self, repository: BigQueryRepository | None = None):
        self.repository = repository or BigQueryRepository()

    def run(self, payload):
        start = time.time()
        run_id = f"tc_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        audit_date = date.today()

        urls = self.repository.get_urls_to_crawl(
            source_run_id=payload.source_run_id,
            only_priority=payload.only_priority,
            max_urls=payload.max_urls,
        )

        results = []
        findings = []
        total_ok = 0
        total_error = 0
        errors = []

        headers = {"User-Agent": settings.request_user_agent}
        timeout = payload.timeout_seconds or settings.request_timeout_seconds

        for row in urls:
            page_url = row["page_url"]
            normalized_url = row["normalized_url"]
            url_hash = row["url_hash"]
            url_type = row["url_type"]
            page_group = row["page_group"]
            is_priority = row["is_priority"]

            checked_ts = datetime.utcnow().isoformat()
            status_code = None
            final_url = None
            response_time_ms = None
            redirect_count = 0
            content_type = None
            content_length = None
            server_header = None
            cache_control = None
            crawl_status = "ok"
            error_message = None
            is_success = False

            try:
                t0 = time.time()
                response = requests.get(page_url, headers=headers, timeout=timeout, allow_redirects=True)
                response_time_ms = round((time.time() - t0) * 1000, 2)

                status_code = response.status_code
                final_url = response.url
                redirect_count = len(response.history)
                content_type = response.headers.get("Content-Type")
                content_length = int(response.headers.get("Content-Length")) if response.headers.get("Content-Length", "").isdigit() else None
                server_header = response.headers.get("Server")
                cache_control = response.headers.get("Cache-Control")
                is_success = 200 <= status_code < 300

                if not is_success:
                    total_error += 1
                else:
                    total_ok += 1

            except requests.exceptions.Timeout as exc:
                crawl_status = "timeout"
                error_message = str(exc)
                total_error += 1
                errors.append(f"{page_url}: timeout")
            except requests.exceptions.SSLError as exc:
                crawl_status = "ssl_error"
                error_message = str(exc)
                total_error += 1
                errors.append(f"{page_url}: ssl_error")
            except requests.exceptions.ConnectionError as exc:
                crawl_status = "connection_error"
                error_message = str(exc)
                total_error += 1
                errors.append(f"{page_url}: connection_error")
            except Exception as exc:
                crawl_status = "http_error"
                error_message = str(exc)
                total_error += 1
                errors.append(f"{page_url}: {str(exc)}")

            final_domain = urlparse(final_url).netloc.lower() if final_url else None

            results.append({
                "run_id": run_id,
                "source_run_id": payload.source_run_id,
                "audit_date": str(audit_date),
                "checked_ts": checked_ts,
                "page_url": page_url,
                "normalized_url": normalized_url,
                "url_hash": url_hash,
                "url_type": url_type,
                "page_group": page_group,
                "is_priority": is_priority,
                "device_priority": payload.device_priority,
                "request_user_agent": settings.request_user_agent,
                "final_url": final_url,
                "final_domain": final_domain,
                "status_code": status_code,
                "is_success": is_success,
                "response_time_ms": response_time_ms,
                "redirect_count": redirect_count,
                "content_type": content_type,
                "content_length": content_length,
                "server_header": server_header,
                "cache_control": cache_control,
                "crawl_status": crawl_status,
                "error_message": error_message,
                "mobile_context": "mobile_first_priority",
            })

            finding = build_finding(status_code, response_time_ms, page_group, is_priority, crawl_status)

            if finding:
                findings.append({
                    "run_id": run_id,
                    "audit_date": str(audit_date),
                    "created_ts": datetime.utcnow().isoformat(),
                    "page_url": page_url,
                    "normalized_url": normalized_url,
                    "finding_code": finding["finding_code"],
                    "finding_category": finding["finding_category"],
                    "severity": finding["severity"],
                    "finding_detail": finding["finding_detail"],
                    "recommendation": finding["recommendation"],
                    "component_type": finding["component_type"],
                    "component_id": finding["component_id"],
                    "component_selector": finding["component_selector"],
                    "html_section": finding["html_section"],
                    "element_value": finding["element_value"],
                    "expected_value": finding["expected_value"],
                })

        duration_seconds = round(time.time() - start, 3)
        status = "success" if total_error == 0 else ("partial_success" if total_ok > 0 else "failed")

        run_log = {
            "run_id": run_id,
            "source_run_id": payload.source_run_id,
            "run_ts": datetime.utcnow().isoformat(),
            "audit_date": str(audit_date),
            "execution_status": status,
            "device_priority": payload.device_priority,
            "only_priority": payload.only_priority,
            "total_urls_target": len(urls),
            "total_urls_processed": len(results),
            "total_urls_ok": total_ok,
            "total_urls_error": total_error,
            "duration_seconds": duration_seconds,
            "error_summary": " | ".join(errors[:10]) if errors else None,
        }

        self.repository.insert_rows("technical_crawl_run_log", [run_log])
        self.repository.insert_rows("technical_crawl_results", results)
        self.repository.insert_rows("technical_crawl_findings", findings)

        return {
            "run_id": run_id,
            "status": status,
            "total_urls_target": len(urls),
            "total_urls_processed": len(results),
            "total_urls_ok": total_ok,
            "total_urls_error": total_error,
            "duration_seconds": duration_seconds,
            "message": "Technical Crawler ejecutado correctamente"
        }