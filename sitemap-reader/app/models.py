from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class RunSitemapReaderRequest(BaseModel):
    root_sitemaps: List[str] = Field(default_factory=list)
    run_type: str = "manual"
    force_reload: bool = True
    allowed_domains: Optional[List[str]] = None
    excluded_extensions: Optional[List[str]] = None


class RunSummaryResponse(BaseModel):
    run_id: str
    status: str
    root_sitemaps: int
    total_sitemaps_found: int
    total_urls_found: int
    total_urls_unique: int
    total_urls_excluded: int
    total_urls_ready_for_audit: int
    duration_seconds: float
    message: str


class SitemapRunLog(BaseModel):
    run_id: str
    run_ts: datetime
    audit_date: date
    source_root_sitemap: str
    run_type: str
    execution_status: str
    total_sitemaps_found: int
    total_sitemaps_read_ok: int
    total_sitemaps_failed: int
    total_urls_found: int
    total_urls_unique: int
    total_urls_excluded: int
    total_urls_ready_for_audit: int
    duration_seconds: float
    error_summary: Optional[str] = None


class SitemapRawEntry(BaseModel):
    run_id: str
    discovered_ts: datetime
    source_sitemap: str
    parent_sitemap: Optional[str]
    entry_type: str
    loc: Optional[str]
    lastmod_raw: Optional[str]
    changefreq_raw: Optional[str]
    priority_raw: Optional[str]
    http_status: Optional[int]
    read_status: str
    error_message: Optional[str] = None


class SitemapMasterUrl(BaseModel):
    run_id: str
    audit_date: date
    created_ts: datetime
    page_url: str
    normalized_url: str
    url_hash: str
    domain: str
    path: str
    query_string: Optional[str]
    source_sitemap: str
    lastmod_ts: Optional[datetime]
    changefreq: Optional[str]
    priority_value: Optional[float]
    url_type: str
    page_group: str
    is_duplicate: bool
    is_excluded: bool
    exclusion_reason: Optional[str]
    should_audit: bool
    priority_group: str
    http_status: Optional[int] = None
    redirect_type: Optional[str] = None
    final_url: Optional[str] = None
    is_valid_status: Optional[bool] = None
    sitemap_issue: Optional[str] = None