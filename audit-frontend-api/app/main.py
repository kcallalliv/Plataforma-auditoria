import logging
from fastapi import FastAPI, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.bigquery_repository import BigQueryRepository
from app.service import AuditFrontendService

logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))

app = FastAPI(
    title="Audit Frontend API",
    version="1.0.0",
    description="BFF para la plataforma de auditoría de Claro Personas"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

repo = BigQueryRepository()
service = AuditFrontendService(repo)

@app.get("/health")
def health():
    return {"status": "ok", "service": settings.app_name}

@app.get("/api/navigation")
def navigation():
    return JSONResponse(content=jsonable_encoder(service.get_navigation()))

@app.get("/api/overview/latest")
def overview_latest():
    return JSONResponse(content=jsonable_encoder(service.get_overview_latest()))

@app.get("/api/modules/{module_key}/latest")
def module_latest(module_key: str):
    if module_key not in {"sitemap", "technical", "seo", "tagging", "links", "content", "performance", "change-history", "alerts"}:
        raise HTTPException(status_code=404, detail="Module not found")
    return JSONResponse(content=jsonable_encoder(service.get_module_latest(module_key)))

@app.get("/api/modules/{module_key}/runs")
def module_runs(module_key: str, limit: int = Query(default=10, le=50)):
    if module_key not in {"sitemap", "technical", "seo", "tagging", "links", "content", "performance", "change-history", "alerts"}:
        raise HTTPException(status_code=404, detail="Module not found")
    return JSONResponse(content=jsonable_encoder(service.get_module_runs(module_key, limit)))

@app.get("/api/modules/sitemap/runs/{run_id}/urls")
def sitemap_urls(run_id: str, limit: int = Query(default=100, le=500)):
    return JSONResponse(content=jsonable_encoder(repo.get_sitemap_urls_by_run(run_id, limit)))

@app.get("/api/modules/technical/runs/{run_id}/results")
def technical_results(
    run_id: str,
    limit: int = Query(default=100, le=500),
    device_profile: str | None = None,
    page_url: str | None = None,):
    return JSONResponse(content=jsonable_encoder(
        repo.get_results_by_run("technical_crawl_results", run_id, limit, device_profile=device_profile, page_url=page_url)
    ))

@app.get("/api/modules/technical/runs/{run_id}/findings")
def technical_findings(
    run_id: str,
    limit: int = Query(default=100, le=500),
    severity: str | None = None,
    finding_code: str | None = None,
    page_url: str | None = None,
):
    return JSONResponse(content=jsonable_encoder(
        repo.get_findings_by_run(
            "technical_crawl_findings",
            run_id,
            limit,
            severity=severity,
            finding_code=finding_code,
            page_url=page_url,
        )
    ))

@app.get("/api/modules/seo/runs/{run_id}/results")
def seo_results(
    run_id: str,
    limit: int = Query(default=100, le=500),
    device_profile: str | None = None,
    page_url: str | None = None,
):
    return JSONResponse(content=jsonable_encoder(
        repo.get_results_by_run("seo_validation_results", run_id, limit, device_profile=device_profile, page_url=page_url)
    ))

@app.get("/api/modules/seo/runs/{run_id}/findings")
def seo_findings(
    run_id: str,
    limit: int = Query(default=100, le=500),
    severity: str | None = None,
    finding_code: str | None = None,
    page_url: str | None = None,
):
    return JSONResponse(content=jsonable_encoder(
        repo.get_findings_by_run("seo_validation_findings", run_id, limit, severity=severity, finding_code=finding_code, page_url=page_url)
    ))

@app.get("/api/modules/tagging/runs/{run_id}/results")
def tagging_results(
    run_id: str,
    limit: int = Query(default=100, le=500),
    device_profile: str | None = None,
    page_url: str | None = None,
):
    return JSONResponse(content=jsonable_encoder(
        repo.get_results_by_run("tagging_validation_results", run_id, limit, device_profile=device_profile, page_url=page_url)
    ))

@app.get("/api/modules/tagging/runs/{run_id}/findings")
def tagging_findings(
    run_id: str,
    limit: int = Query(default=100, le=500),
    severity: str | None = None,
    finding_code: str | None = None,
    page_url: str | None = None,
):
    return JSONResponse(content=jsonable_encoder(
        repo.get_findings_by_run("tagging_validation_findings", run_id, limit, severity=severity, finding_code=finding_code, page_url=page_url)
    ))

@app.get("/api/modules/links/latest")
def links_latest():
    return JSONResponse(content=jsonable_encoder(repo.get_link_latest_run()))

@app.get("/api/modules/links/runs/{run_id}/results")
def links_results(
    run_id: str,
    limit: int = Query(default=100, le=500),
    device_profile: str | None = None,
    page_url: str | None = None,
):
    return JSONResponse(content=jsonable_encoder(
        repo.get_link_results_by_run(run_id, limit, device_profile=device_profile, page_url=page_url)
    ))

@app.get("/api/modules/links/runs/{run_id}/findings")
def links_findings(
    run_id: str,
    limit: int = Query(default=100, le=500),
    severity: str | None = None,
    finding_code: str | None = None,
    page_url: str | None = None,
):
    return JSONResponse(content=jsonable_encoder(
        repo.get_link_findings_by_run(run_id, limit, severity=severity, finding_code=finding_code, page_url=page_url)
    ))

@app.get("/api/modules/links/runs/{run_id}/kpis")
def links_kpis(run_id: str):
    return JSONResponse(content=jsonable_encoder(repo.get_link_kpis_by_run(run_id)))

@app.get("/api/modules/links/runs/{run_id}/summary")
def links_summary(run_id: str):
    return JSONResponse(content=jsonable_encoder(repo.get_link_summary_by_run(run_id)))

@app.get("/api/modules/links/runs/{run_id}/top-broken-pages")
def links_top_broken_pages(run_id: str, limit: int = Query(default=10, le=100)):
    return JSONResponse(content=jsonable_encoder(repo.get_link_top_broken_pages(run_id, limit)))

@app.get("/api/modules/performance/latest")
def performance_latest():
    return JSONResponse(content=jsonable_encoder(repo.get_performance_latest_run()))

@app.get("/api/modules/performance/runs/{run_id}/results")
def performance_results(
    run_id: str,
    limit: int = Query(default=100, le=500),
    strategy: str | None = None,
    page_url: str | None = None,
):
    return JSONResponse(content=jsonable_encoder(
        repo.get_performance_results_by_run(run_id, limit, strategy=strategy, page_url=page_url)
    ))

@app.get("/api/modules/performance/runs/{run_id}/findings")
def performance_findings(
    run_id: str,
    limit: int = Query(default=100, le=500),
    severity: str | None = None,
    finding_code: str | None = None,
    page_url: str | None = None,
):
    return JSONResponse(content=jsonable_encoder(
        repo.get_performance_findings_by_run(run_id, limit, severity=severity, finding_code=finding_code, page_url=page_url)
    ))

@app.get("/api/modules/content/latest")
def content_latest():
    return JSONResponse(content=jsonable_encoder(repo.get_content_latest_run()))

@app.get("/api/modules/content/runs/{run_id}/results")
def content_results(
    run_id: str,
    limit: int = Query(default=100, le=500),
    device_profile: str | None = None,
    page_url: str | None = None,
):
    return JSONResponse(content=jsonable_encoder(
        repo.get_content_results_by_run(run_id, limit, device_profile=device_profile, page_url=page_url)
    ))

@app.get("/api/modules/content/runs/{run_id}/findings")
def content_findings(
    run_id: str,
    limit: int = Query(default=100, le=500),
    severity: str | None = None,
    finding_code: str | None = None,
    page_url: str | None = None,
):
    return JSONResponse(content=jsonable_encoder(
        repo.get_content_findings_by_run(run_id, limit, severity=severity, finding_code=finding_code, page_url=page_url)
    ))

@app.get("/api/modules/content/runs/{run_id}/kpis")
def content_kpis(run_id: str):
    return JSONResponse(content=jsonable_encoder(repo.get_content_kpis_by_run(run_id)))

@app.get("/api/modules/content/runs/{run_id}/summary")
def content_summary(run_id: str):
    return JSONResponse(content=jsonable_encoder(repo.get_content_summary_by_run(run_id)))

@app.get("/api/modules/change-history/latest")
def change_history_latest():
    return JSONResponse(content=jsonable_encoder(repo.get_change_history_latest_run()))

@app.get("/api/modules/change-history/runs/{run_id}/results")
def change_history_results(
    run_id: str,
    limit: int = Query(default=100, le=500),
    page_url: str | None = None,
):
    return JSONResponse(content=jsonable_encoder(
        repo.get_change_history_results_by_run(run_id, limit, page_url=page_url)
    ))

@app.get("/api/modules/change-history/runs/{run_id}/summary")
def change_history_summary(run_id: str):
    return JSONResponse(content=jsonable_encoder(repo.get_change_history_summary_by_run(run_id)))

@app.get("/api/url-detail")
def url_detail(normalized_url: str):
    detail = service.get_url_detail(normalized_url)
    if not detail:
        raise HTTPException(status_code=404, detail="URL not found")
    return JSONResponse(content=jsonable_encoder(detail))

@app.get("/api/runs/compare")
def runs_compare(
    current_run_id: str,
    previous_run_id: str,
    limit: int = Query(default=200, le=1000),
):
    return JSONResponse(content=jsonable_encoder(
        repo.compare_runs(current_run_id=current_run_id, previous_run_id=previous_run_id, limit=limit)
    ))

@app.get("/api/findings/summary/latest")
def findings_summary_latest():
    return JSONResponse(content=jsonable_encoder(repo.get_findings_summary_latest()))

@app.get("/api/findings/by-url")
def findings_by_url(url: str, limit: int = Query(default=200, le=1000)):
    return JSONResponse(content=jsonable_encoder(repo.get_findings_by_url(page_url=url, limit=limit)))

@app.get("/api/modules/alerts/latest")
def alerts_latest():
    return JSONResponse(content=jsonable_encoder(repo.get_alert_latest_run()))

@app.get("/api/modules/alerts/runs/{run_id}/events")
def alerts_events(
    run_id: str,
    limit: int = Query(default=100, le=500),
    severity: str | None = None,
    page_url: str | None = None,
):
    return JSONResponse(content=jsonable_encoder(
        repo.get_alert_events_by_run(run_id, limit=limit, severity=severity, page_url=page_url)
    ))

@app.get("/api/modules/alerts/runs/{run_id}/summary")
def alerts_summary(run_id: str):
    return JSONResponse(content=jsonable_encoder(repo.get_alert_summary_by_run(run_id)))

@app.get("/api/modules/{module_key}/runs/{run_id}/kpis")
def module_kpis(module_key: str, run_id: str):
    if module_key == "seo":
        return JSONResponse(content=jsonable_encoder(repo.get_seo_kpis_by_run(run_id)))

    if module_key == "sitemap":
        return JSONResponse(content=jsonable_encoder(repo.get_sitemap_kpis_by_run(run_id)))

    raise HTTPException(status_code=404, detail="KPIs not available for this module")