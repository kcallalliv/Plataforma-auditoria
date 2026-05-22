import time
import uuid
from datetime import datetime

from app.bigquery_repository import BigQueryRepository

class AlertEngineService:
    def __init__(self, repository: BigQueryRepository | None = None):
        self.repository = repository or BigQueryRepository()

    def run(self, payload):
        start = time.time()
        run_id = f"alr_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        now = datetime.utcnow().isoformat()

        alerts = []
        for row in self.repository.get_latest_technical_errors():
            alerts.append({
                "alert_id": f"{run_id}_{len(alerts)+1}",
                "alert_run_id": run_id,
                "page_url": row.get("page_url"),
                "module_name": "M2 Technical Crawler",
                "severity": "Alta",
                "alert_type": "status_5xx",
                "alert_message": "Página con error 5xx detectada",
                "current_value": str(row.get("status_code")),
                "threshold_value": ">=500",
                "notification_status": "pending",
                "created_ts": now,
            })

        for row in self.repository.get_latest_seo_noindex_commercial():
            alerts.append({
                "alert_id": f"{run_id}_{len(alerts)+1}",
                "alert_run_id": run_id,
                "page_url": row.get("page_url"),
                "module_name": "M4 SEO Validator",
                "severity": "Alta",
                "alert_type": "noindex_commercial",
                "alert_message": "Página comercial con noindex detectada",
                "current_value": "has_noindex=true",
                "threshold_value": "has_noindex=false",
                "notification_status": "pending",
                "created_ts": now,
            })

        run_log = {
            "alert_run_id": run_id,
            "source_run_id": payload.source_run_id,
            "started_ts": now,
            "ended_ts": datetime.utcnow().isoformat(),
            "status": "success",
            "created_ts": now,
        }

        self.repository.insert_rows("alert_run_log", [run_log])
        self.repository.insert_rows("alert_events", alerts)

        return {
            "run_id": run_id,
            "status": "success",
            "total_alerts": len(alerts),
            "duration_seconds": round(time.time() - start, 3),
            "message": "Alert Engine ejecutado correctamente",
        }