import logging
import time
import uuid
from datetime import date, datetime
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from app.bigquery_repository import BigQueryRepository
from app.config import settings

logger = logging.getLogger(__name__)

def severity_by_finding_code(code: str) -> str:
    if code in {"broken_internal_link", "broken_pdf", "broken_image", "invalid_anchor"}:
        return "Alta"
    if code in {"broken_external_link", "excessive_redirects", "javascript_void_link"}:
        return "Media"
    return "Baja"

class LinkValidatorService:
    def __init__(self, repository: BigQueryRepository | None = None):
        self.repository = repository or BigQueryRepository()

    def _link_type(self, link_url: str, base_domain: str) -> str:
        p = urlparse(link_url)
        if link_url.startswith("#"):
            return "anchor"
        if any(link_url.lower().endswith(ext) for ext in [".pdf"]):
            return "pdf"
        if any(link_url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"]):
            return "image"
        if p.netloc and p.netloc != base_domain:
            return "external"
        return "internal"

    def run(self, payload):
        start = time.time()
        run_id = f"link_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        audit_date = date.today()

        urls = self.repository.get_urls_to_validate(
            source_run_id=payload.source_run_id,
            technical_run_id=payload.technical_run_id,
            only_priority=payload.only_priority,
            max_urls=payload.max_urls,
        )

        results, findings, errors = [], [], []
        total_links_broken = 0
        headers = {"User-Agent": settings.request_user_agent}

        for row in urls:
            page_url = row["page_url"]
            normalized_url = row["normalized_url"]
            try:
                resp = requests.get(page_url, timeout=settings.request_timeout_seconds, headers=headers)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")
                base_domain = urlparse(page_url).netloc

                for el in soup.find_all(["a", "img"]):
                    href = el.get("href")
                    src = el.get("src")
                    raw_url = href if href else src
                    if not raw_url:
                        finding_code = "empty_href" if el.name == "a" else "broken_image"
                        result_row = {
                            "link_run_id": run_id,
                            "source_run_id": payload.source_run_id,
                            "technical_run_id": payload.technical_run_id,
                            "page_url": page_url,
                            "device_profile": payload.device_profile,
                            "link_url": None,
                            "link_type": "anchor" if el.name == "a" else "image",
                            "link_text": (el.get_text(" ", strip=True) if el.name == "a" else el.get("alt")) or "",
                            "link_status_code": None,
                            "link_final_url": None,
                            "is_broken": True,
                            "redirect_count": None,
                            "element_tag": el.name,
                            "element_id": el.get("id"),
                            "element_class": " ".join(el.get("class", [])) if el.get("class") else None,
                            "element_text": (el.get_text(" ", strip=True) if el.name == "a" else el.get("alt")) or "",
                            "css_selector": f"{el.name}{'#' + el.get('id') if el.get('id') else ''}",
                            "xpath": None,
                            "href": href,
                            "src": src,
                            "dom_section": "body",
                            "html_snippet": str(el)[:500],
                            "created_ts": datetime.utcnow().isoformat(),
                        }
                        results.append(result_row)
                        findings.append({**result_row, "finding_type": finding_code, "severity": severity_by_finding_code(finding_code)})
                        total_links_broken += 1
                        continue
                    link_url = urljoin(page_url, raw_url)
                    ltype = self._link_type(raw_url, base_domain)
                    link_text = (el.get_text(" ", strip=True) if el.name == "a" else el.get("alt")) or ""

                    status_code, is_broken, redirect_count = None, False, 0
                    finding_code = None
                    if ltype != "anchor" and not raw_url.lower().startswith("javascript:void"):
                        try:
                            r2 = requests.head(link_url, timeout=settings.request_timeout_seconds, headers=headers, allow_redirects=True)
                            status_code = r2.status_code
                            redirect_count = len(r2.history)
                            if status_code >= 400:
                                is_broken = True
                                finding_code = "broken_internal_link" if ltype == "internal" else "broken_external_link" if ltype == "external" else "broken_pdf" if ltype == "pdf" else "broken_image"
                            elif redirect_count > 2:
                                is_broken = True
                                finding_code = "excessive_redirects"
                        except Exception:
                            is_broken = True
                            finding_code = "broken_internal_link" if ltype == "internal" else "broken_external_link" if ltype == "external" else "broken_pdf" if ltype == "pdf" else "broken_image"

                    if raw_url.lower().startswith("javascript:void"):
                        is_broken = True
                        finding_code = "javascript_void_link"

                    if ltype == "anchor" and raw_url.startswith("#"):
                        anchor_id = raw_url[1:]
                        if anchor_id and not soup.find(id=anchor_id):
                            is_broken = True
                            finding_code = "invalid_anchor"

                    if el.name == "a" and not link_text.strip():
                        is_broken = True
                        if finding_code is None:
                            finding_code = "empty_anchor_text"

                    if is_broken:
                        total_links_broken += 1

                    result_row = {
                        "link_run_id": run_id,
                        "source_run_id": payload.source_run_id,
                        "technical_run_id": payload.technical_run_id,
                        "page_url": page_url,
                        "device_profile": payload.device_profile,
                        "link_url": link_url,
                        "link_type": ltype,
                        "link_text": link_text,
                        "link_status_code": status_code,
                        "link_final_url": link_url,
                        "is_broken": is_broken,
                        "redirect_count": redirect_count,
                        "element_tag": el.name,
                        "element_id": el.get("id"),
                        "element_class": " ".join(el.get("class", [])) if el.get("class") else None,
                        "element_text": link_text,
                        "css_selector": f"{el.name}{'#' + el.get('id') if el.get('id') else ''}",
                        "xpath": None,
                        "href": href,
                        "src": src,
                        "dom_section": "body",
                        "html_snippet": str(el)[:500],
                        "created_ts": datetime.utcnow().isoformat(),
                    }
                    results.append(result_row)

                    if is_broken:
                        findings.append({
                            **result_row,
                            "finding_type": finding_code or ("broken_internal_link" if ltype == "internal" else "broken_external_link"),
                            "severity": severity_by_finding_code(finding_code or "broken_internal_link"),
                        })

            except Exception as exc:
                errors.append(f"{page_url}: {str(exc)}")

        duration_seconds = round(time.time() - start, 3)
        status = "success" if not errors else ("partial_success" if results else "failed")

        run_log = {
            "link_run_id": run_id,
            "source_run_id": payload.source_run_id,
            "technical_run_id": payload.technical_run_id,
            "started_ts": datetime.utcnow().isoformat(),
            "ended_ts": datetime.utcnow().isoformat(),
            "status": status,
            "created_ts": datetime.utcnow().isoformat(),
            "audit_date": str(audit_date),
            "error_summary": " | ".join(errors[:10]) if errors else None,
        }

        self.repository.insert_rows("link_validation_run_log", [run_log])
        self.repository.insert_rows("link_validation_results", results)
        self.repository.insert_rows("link_validation_findings", findings)

        return {
            "run_id": run_id,
            "status": status,
            "total_urls_target": len(urls),
            "total_urls_processed": len(urls),
            "total_links_processed": len(results),
            "total_links_broken": total_links_broken,
            "duration_seconds": duration_seconds,
            "message": "Link Validator ejecutado correctamente"
        }