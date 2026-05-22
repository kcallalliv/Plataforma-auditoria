import logging
import time
import uuid
from datetime import datetime
import requests

from app.bigquery_repository import BigQueryRepository
from app.config import settings

logger = logging.getLogger(__name__)

class PerformanceValidatorService:
    def __init__(self, repository: BigQueryRepository | None = None):
        self.repository = repository or BigQueryRepository()

    def run(self, payload):
        start = time.time()
        run_id = f"perf_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        urls = self.repository.get_urls_to_measure(
            source_run_id=payload.source_run_id,
            only_priority=payload.only_priority,
            max_urls=payload.max_urls,
        )

        results, findings = [], []
        errors = []

        if not settings.pagespeed_api_key:
            errors.append("PAGESPEED_API_KEY no configurada. Define la variable de entorno para habilitar métricas reales.")

        for row in urls:
            for strategy in payload.strategies:
                try:
                    metrics = self._fetch_pagespeed_metrics(row["page_url"], strategy)
                    previous = self.repository.get_previous_result(row["page_url"], strategy)
                    result_row = {
                        "performance_run_id": run_id,
                        "source_run_id": payload.source_run_id,
                        "page_url": row["page_url"],
                        "strategy": strategy,
                        "network_profile": "regular_4g" if strategy == "mobile" else "fast",
                        "performance_score": metrics.get("performance_score"),
                        "fcp_ms": metrics.get("fcp_ms"),
                        "lcp_ms": metrics.get("lcp_ms"),
                        "inp_ms": metrics.get("inp_ms"),
                        "cls": metrics.get("cls"),
                        "ttfb_ms": metrics.get("ttfb_ms"),
                        "speed_index_ms": metrics.get("speed_index_ms"),
                        "total_blocking_time_ms": metrics.get("total_blocking_time_ms"),
                        "page_weight_kb": None,
                        "image_weight_kb": None,
                        "js_weight_kb": None,
                        "css_weight_kb": None,
                        "lighthouse_json_path": None,
                        "created_ts": datetime.utcnow().isoformat(),
                    }
                    results.append(result_row)

                    findings.extend(self._build_findings(run_id, row["page_url"], strategy, metrics, previous))
                except Exception as exc:
                    errors.append(f"{row['page_url']} [{strategy}]: {str(exc)}")

        status = "success" if not errors else ("partial_success" if results else "failed")
        duration_seconds = round(time.time() - start, 3)

        run_log = {
            "performance_run_id": run_id,
            "source_run_id": payload.source_run_id,
            "started_ts": datetime.utcnow().isoformat(),
            "ended_ts": datetime.utcnow().isoformat(),
            "status": status,
            "created_ts": datetime.utcnow().isoformat(),
            "error_summary": " | ".join(errors[:10]) if errors else None,
        }

        self.repository.insert_rows("performance_validation_run_log", [run_log])
        self.repository.insert_rows("performance_validation_results", results)
        self.repository.insert_rows("performance_validation_findings", findings)

        return {
            "run_id": run_id,
            "status": status,
            "total_urls_target": len(urls),
            "total_urls_processed": len(urls),
            "total_measurements": len(results),
            "duration_seconds": duration_seconds,
            "message": "Performance Validator ejecutado correctamente"
        }

    def _fetch_pagespeed_metrics(self, page_url: str, strategy: str) -> dict:
        if not settings.pagespeed_api_key:
            return {}

        last_error = None
        for attempt in range(settings.pagespeed_max_retries + 1):
            try:
                response = requests.get(
                    settings.pagespeed_base_url,
                    params={
                        "url": page_url,
                        "strategy": strategy,
                        "key": settings.pagespeed_api_key,
                        "category": ["PERFORMANCE"],
                    },
                    timeout=settings.pagespeed_timeout_seconds,
                )
                if response.status_code == 429:
                    raise RuntimeError("PSI quota/rate limit (429)")
                response.raise_for_status()
                data = response.json()
                lh = data.get("lighthouseResult", {})
                audits = lh.get("audits", {})
                categories = lh.get("categories", {})

                score = categories.get("performance", {}).get("score")
                score = round(score * 100, 2) if score is not None else None

                def num(path, cast=float):
                    v = audits.get(path, {}).get("numericValue")
                    return cast(v) if v is not None else None

                return {
                    "performance_score": score,
                    "fcp_ms": num("first-contentful-paint"),
                    "lcp_ms": num("largest-contentful-paint"),
                    "inp_ms": num("interaction-to-next-paint"),
                    "cls": num("cumulative-layout-shift"),
                    "ttfb_ms": num("server-response-time"),
                    "speed_index_ms": num("speed-index"),
                    "total_blocking_time_ms": num("total-blocking-time"),
                }
            except Exception as exc:
                last_error = exc
                if attempt < settings.pagespeed_max_retries:
                    time.sleep((2 ** attempt) + (settings.pagespeed_sleep_ms / 1000.0))
                else:
                    raise
        raise RuntimeError(str(last_error))

    def _build_findings(self, run_id: str, page_url: str, strategy: str, m: dict, previous: dict | None = None) -> list[dict]:
        findings = []
        now = datetime.utcnow().isoformat()

        def add(code, detail, severity, expected, actual):
            findings.append({
                "performance_run_id": run_id,
                "page_url": page_url,
                "strategy": strategy,
                "finding_code": code,
                "finding_detail": detail,
                "severity": severity,
                "recommendation": "Optimizar recursos bloqueantes, imágenes y tiempos de respuesta.",
                "expected_value": expected,
                "actual_value": actual,
                "created_ts": now,
            })

        if m.get("performance_score") is not None and m["performance_score"] < 60:
            add("PERF_SCORE_LOW", "Performance score bajo", "Alta", ">= 60", str(m["performance_score"]))
        if m.get("lcp_ms") is not None and m["lcp_ms"] > 2500:
            add("PERF_LCP_HIGH", "LCP alto", "Alta", "<= 2500", str(m["lcp_ms"]))
        if m.get("cls") is not None and m["cls"] > 0.1:
            add("PERF_CLS_HIGH", "CLS alto", "Media", "<= 0.1", str(m["cls"]))
        if m.get("inp_ms") is not None and m["inp_ms"] > 200:
            add("PERF_INP_HIGH", "INP alto", "Alta", "<= 200", str(m["inp_ms"]))
        if m.get("ttfb_ms") is not None and m["ttfb_ms"] > 800:
            add("PERF_TTFB_HIGH", "TTFB alto", "Media", "<= 800", str(m["ttfb_ms"]))
        if previous and m.get("performance_score") is not None and previous.get("performance_score") is not None:
            delta = float(m["performance_score"]) - float(previous["performance_score"])
            if delta <= -10:
                add(
                    "PERF_SCORE_DROP",
                    "Caída de performance vs corrida anterior",
                    "Alta",
                    f">= {previous['performance_score']}",
                    str(m["performance_score"]),
                )
        return findings