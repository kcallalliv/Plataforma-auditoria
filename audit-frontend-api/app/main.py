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
    if module_key not in {"sitemap", "technical", "seo", "tagging"}:
        raise HTTPException(status_code=404, detail="Module not found")
    return JSONResponse(content=jsonable_encoder(service.get_module_latest(module_key)))

@app.get("/api/modules/{module_key}/runs")
def module_runs(module_key: str, limit: int = Query(default=10, le=50)):
    if module_key not in {"sitemap", "technical", "seo", "tagging"}:
        raise HTTPException(status_code=404, detail="Module not found")
    return JSONResponse(content=jsonable_encoder(service.get_module_runs(module_key, limit)))

@app.get("/api/modules/sitemap/runs/{run_id}/urls")
def sitemap_urls(run_id: str, limit: int = Query(default=100, le=500)):
    return JSONResponse(content=jsonable_encoder(repo.get_sitemap_urls_by_run(run_id, limit)))

@app.get("/api/modules/technical/runs/{run_id}/results")
def technical_results(run_id: str, limit: int = Query(default=100, le=500)):
    return JSONResponse(content=jsonable_encoder(repo.get_results_by_run("technical_crawl_results", run_id, limit)))

@app.get("/api/modules/technical/runs/{run_id}/findings")
def technical_findings(run_id: str, limit: int = Query(default=100, le=500)):
    return JSONResponse(content=jsonable_encoder(repo.get_findings_by_run("technical_crawl_findings", run_id, limit)))

@app.get("/api/modules/seo/runs/{run_id}/results")
def seo_results(run_id: str, limit: int = Query(default=100, le=500)):
    return JSONResponse(content=jsonable_encoder(repo.get_results_by_run("seo_validation_results", run_id, limit)))

@app.get("/api/modules/seo/runs/{run_id}/findings")
def seo_findings(run_id: str, limit: int = Query(default=100, le=500)):
    return JSONResponse(content=jsonable_encoder(repo.get_findings_by_run("seo_validation_findings", run_id, limit)))

@app.get("/api/modules/tagging/runs/{run_id}/results")
def tagging_results(run_id: str, limit: int = Query(default=100, le=500)):
    return JSONResponse(content=jsonable_encoder(repo.get_results_by_run("tagging_validation_results", run_id, limit)))

@app.get("/api/modules/tagging/runs/{run_id}/findings")
def tagging_findings(run_id: str, limit: int = Query(default=100, le=500)):
    return JSONResponse(content=jsonable_encoder(repo.get_findings_by_run("tagging_validation_findings", run_id, limit)))

@app.get("/api/url-detail")
def url_detail(normalized_url: str):
    detail = service.get_url_detail(normalized_url)
    if not detail:
        raise HTTPException(status_code=404, detail="URL not found")
    return JSONResponse(content=jsonable_encoder(detail))

@app.get("/api/modules/{module_key}/runs/{run_id}/kpis")
def module_kpis(module_key: str, run_id: str):
    if module_key == "seo":
        return JSONResponse(content=jsonable_encoder(repo.get_seo_kpis_by_run(run_id)))

    if module_key == "sitemap":
        return JSONResponse(content=jsonable_encoder(repo.get_sitemap_kpis_by_run(run_id)))

    raise HTTPException(status_code=404, detail="KPIs not available for this module")