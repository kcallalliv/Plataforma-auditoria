import logging
import time
import uuid
import xml.etree.ElementTree as ET
from datetime import date, datetime
from typing import Any

import requests

from app.bigquery_repository import BigQueryRepository
from app.config import settings
from app.models import RunSitemapReaderRequest
from app.config import settings, PRIORITY_PATHS
from app.utils import (
    classify_url,
    compact_error,
    get_domain_path_query,
    get_url_hash,
    has_excluded_extension,
    is_valid_domain,
    normalize_url,
    normalize_path,
    parse_lastmod,
    safe_float,
)

from app.utils import normalize_path

logger = logging.getLogger(__name__)

SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


class SitemapReaderService:
    def __init__(self, repository: BigQueryRepository | None = None) -> None:
        self.repository = repository or BigQueryRepository()

    def _download_xml(self, sitemap_url: str) -> tuple[str, int]:
        headers = {"User-Agent": settings.user_agent}
        response = requests.get(
            sitemap_url,
            timeout=settings.request_timeout_seconds,
            headers=headers,
        )
        response.raise_for_status()
        return response.text, response.status_code
    
    def _validate_url_status(self, url: str) -> dict[str, Any]:
        try:
            headers = {"User-Agent": settings.user_agent}
            response = requests.get(
                url,
                timeout=settings.request_timeout_seconds,
                headers=headers,
                allow_redirects=False,
            )

            status = response.status_code
            location = response.headers.get("Location")

            if status == 200:
                return {
                    "http_status": status,
                    "redirect_type": None,
                    "final_url": url,
                    "is_valid_status": True,
                    "sitemap_issue": None,
                }

            if status in [301, 302]:
                return {
                    "http_status": status,
                    "redirect_type": str(status),
                    "final_url": location or url,
                    "is_valid_status": False,
                    "sitemap_issue": f"URL en sitemap responde con redirección {status}",
                }

            if status >= 400:
                return {
                    "http_status": status,
                    "redirect_type": None,
                    "final_url": url,
                    "is_valid_status": False,
                    "sitemap_issue": f"URL en sitemap responde con error HTTP {status}",
                }

            return {
                "http_status": status,
                "redirect_type": None,
                "final_url": url,
                "is_valid_status": False,
                "sitemap_issue": f"URL en sitemap responde con estado HTTP {status}",
            }

        except Exception as exc:
            return {
                "http_status": None,
                "redirect_type": None,
                "final_url": url,
                "is_valid_status": False,
                "sitemap_issue": f"No se pudo validar la URL: {str(exc)}",
            }

    def _parse_urlset(self, xml_text: str) -> list[dict[str, Any]]:
        root = ET.fromstring(xml_text)

        urls = []
        for url_node in root.findall("sm:url", SITEMAP_NS):
            loc = self._get_text(url_node, "sm:loc")
            lastmod = self._get_text(url_node, "sm:lastmod")
            changefreq = self._get_text(url_node, "sm:changefreq")
            priority = self._get_text(url_node, "sm:priority")

            urls.append(
                {
                    "loc": loc,
                    "lastmod_raw": lastmod,
                    "changefreq_raw": changefreq,
                    "priority_raw": priority,
                }
            )
        return urls

    @staticmethod
    def _get_text(node: ET.Element, path: str) -> str | None:
        child = node.find(path, SITEMAP_NS)
        if child is None or child.text is None:
            return None
        return child.text.strip()

    def run(self, request: RunSitemapReaderRequest) -> dict[str, Any]:
        start_time = time.time()
        run_id = f"sr_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        audit_date = date.today()

        root_sitemaps = request.root_sitemaps or settings.default_root_sitemaps
        allowed_domains = request.allowed_domains or settings.allowed_domains
        excluded_extensions = request.excluded_extensions or settings.excluded_extensions

        total_sitemaps_found = len(root_sitemaps)
        total_sitemaps_read_ok = 0
        total_sitemaps_failed = 0
        total_urls_found = 0
        total_urls_excluded = 0
        errors: list[str] = []

        raw_entries: list[dict] = []
        master_urls: list[dict] = []

        seen_hashes: set[str] = set()

        for sitemap_url in root_sitemaps:
            try:
                xml_text, http_status = self._download_xml(sitemap_url)
                total_sitemaps_read_ok += 1

                parsed_entries = self._parse_urlset(xml_text)
                total_urls_found += len(parsed_entries)

                for entry in parsed_entries:
                    loc = entry["loc"]
                    raw_entries.append(
                        {
                            "run_id": run_id,
                            "discovered_ts": datetime.utcnow().isoformat(),
                            "source_sitemap": sitemap_url,
                            "parent_sitemap": None,
                            "entry_type": "url",
                            "loc": loc,
                            "lastmod_raw": entry["lastmod_raw"],
                            "changefreq_raw": entry["changefreq_raw"],
                            "priority_raw": entry["priority_raw"],
                            "http_status": http_status,
                            "read_status": "read_ok" if loc else "invalid",
                            "error_message": None if loc else "loc vacío",
                        }
                    )

                    if not loc:
                        total_urls_excluded += 1
                        continue

                    normalized_url = normalize_url(loc)
                    domain, path, query_string = get_domain_path_query(normalized_url)

                    normalized_path = normalize_path(path)
                    is_priority = normalized_path in PRIORITY_PATHS
                    logger.info("PATH ORIGINAL=%s | NORMALIZED=%s | IS_PRIORITY=%s", path, normalized_path, is_priority)

                    if is_priority:
                        logger.info("MATCH_PRIORITY=%s", normalized_path)

                    if not is_priority:
                        logger.info("EXCLUDED_NON_PRIORITY=%s", normalized_path)
                        total_urls_excluded += 1
                        continue

                    is_excluded = False
                    exclusion_reason = None

                    if not is_valid_domain(domain, allowed_domains):
                        is_excluded = True
                        exclusion_reason = "domain_not_allowed"

                    elif has_excluded_extension(path, excluded_extensions):
                        is_excluded = True
                        exclusion_reason = "excluded_extension"

                    url_hash = get_url_hash(normalized_url)
                    is_duplicate = url_hash in seen_hashes

                    if is_duplicate:
                        is_excluded = True
                        exclusion_reason = "duplicate_url"

                    if not is_duplicate:
                        seen_hashes.add(url_hash)

                    if is_excluded:
                        total_urls_excluded += 1

                    status_data = self._validate_url_status(loc)
                    url_type, page_group, priority_group = classify_url(path)

                    master_urls.append(
                        {
                            "run_id": run_id,
                            "audit_date": str(audit_date),
                            "created_ts": datetime.utcnow().isoformat(),
                            "page_url": loc,
                            "normalized_url": normalized_url,
                            "url_hash": url_hash,
                            "domain": domain,
                            "path": path,
                            "query_string": query_string,
                            "source_sitemap": sitemap_url,
                            "lastmod_ts": (
                                parse_lastmod(entry["lastmod_raw"]).isoformat()
                                if parse_lastmod(entry["lastmod_raw"])
                                else None
                            ),
                            "changefreq": entry["changefreq_raw"],
                            "priority_value": safe_float(entry["priority_raw"]),
                            "url_type": url_type,
                            "page_group": page_group,
                            "is_duplicate": is_duplicate,
                            "is_excluded": is_excluded,
                            "exclusion_reason": exclusion_reason,
                            "should_audit": not is_excluded,
                            "priority_group": priority_group,
                            "is_priority": is_priority,
                            "priority_source": "mvp_priority_paths" if is_priority else None,
                            "normalized_path": normalized_path,
                            "http_status": status_data["http_status"],
                            "redirect_type": status_data["redirect_type"],
                            "final_url": status_data["final_url"],
                            "is_valid_status": status_data["is_valid_status"],
                            "sitemap_issue": status_data["sitemap_issue"],
                        }
                    )

            except Exception as exc:
                logger.exception("Error leyendo sitemap %s", sitemap_url)
                total_sitemaps_failed += 1
                errors.append(f"{sitemap_url}: {str(exc)}")

                raw_entries.append(
                    {
                        "run_id": run_id,
                        "discovered_ts": datetime.utcnow().isoformat(),
                        "source_sitemap": sitemap_url,
                        "parent_sitemap": None,
                        "entry_type": "urlset",
                        "loc": None,
                        "lastmod_raw": None,
                        "changefreq_raw": None,
                        "priority_raw": None,
                        "http_status": None,
                        "read_status": "parse_error",
                        "error_message": str(exc),
                    }
                )

        total_urls_unique = len({r["url_hash"] for r in master_urls})
        total_urls_ready_for_audit = sum(1 for r in master_urls if r["should_audit"])

        duration_seconds = round(time.time() - start_time, 3)
        status = "success" if total_sitemaps_failed == 0 else "partial_success"

        run_log = {
            "run_id": run_id,
            "run_ts": datetime.utcnow().isoformat(),
            "audit_date": str(audit_date),
            "source_root_sitemap": ",".join(root_sitemaps),
            "run_type": request.run_type,
            "execution_status": status,
            "total_sitemaps_found": total_sitemaps_found,
            "total_sitemaps_read_ok": total_sitemaps_read_ok,
            "total_sitemaps_failed": total_sitemaps_failed,
            "total_urls_found": total_urls_found,
            "total_urls_unique": total_urls_unique,
            "total_urls_excluded": total_urls_excluded,
            "total_urls_ready_for_audit": total_urls_ready_for_audit,
            "duration_seconds": duration_seconds,
            "error_summary": compact_error(errors),
        }

        # Persistencia
        self.repository.insert_run_log(run_log)
        self.repository.insert_raw_entries(raw_entries)
        self.repository.insert_master_urls(master_urls)

        return {
            "run_id": run_id,
            "status": status,
            "root_sitemaps": len(root_sitemaps),
            "total_sitemaps_found": total_sitemaps_found,
            "total_urls_found": total_urls_found,
            "total_urls_unique": total_urls_unique,
            "total_urls_excluded": total_urls_excluded,
            "total_urls_ready_for_audit": total_urls_ready_for_audit,
            "duration_seconds": duration_seconds,
            "message": "Sitemap Reader ejecutado correctamente",
        }