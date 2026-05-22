import hashlib
import json
import time
import uuid
from datetime import datetime

from app.bigquery_repository import BigQueryRepository

class ChangeHistoryService:
    def __init__(self, repository: BigQueryRepository | None = None):
        self.repository = repository or BigQueryRepository()

    def run(self, payload):
        start = time.time()
        run_id = f"chg_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

        run_ids = self.repository.get_latest_source_run_ids()
        current_run_id = payload.source_run_id or (run_ids[0] if run_ids else None)
        previous_run_id = run_ids[1] if len(run_ids) > 1 else None

        if not current_run_id:
            return {"run_id": run_id, "status": "failed", "total_changes": 0, "duration_seconds": 0.0, "message": "No source run available"}

        current_rows = self.repository.get_sitemap_urls_for_run(current_run_id)
        previous_rows = self.repository.get_sitemap_urls_for_run(previous_run_id) if previous_run_id else []

        current_map = {r["page_url"]: r for r in current_rows}
        previous_map = {r["page_url"]: r for r in previous_rows}

        all_urls = set(current_map.keys()) | set(previous_map.keys())
        changes = []
        now = datetime.utcnow().isoformat()

        for url in sorted(all_urls):
            prev = previous_map.get(url)
            curr = current_map.get(url)
            if prev is None and curr is not None:
                changes.append({"change_run_id": run_id, "source_run_id": current_run_id, "technical_run_id": payload.technical_run_id,
                                "page_url": url, "change_type": "new_url", "previous_value": None,
                                "current_value": json.dumps(curr, ensure_ascii=False), "previous_run_id": previous_run_id,
                                "current_run_id": current_run_id, "detected_ts": now, "created_ts": now})
            elif prev is not None and curr is None:
                changes.append({"change_run_id": run_id, "source_run_id": current_run_id, "technical_run_id": payload.technical_run_id,
                                "page_url": url, "change_type": "removed_url", "previous_value": json.dumps(prev, ensure_ascii=False),
                                "current_value": None, "previous_run_id": previous_run_id,
                                "current_run_id": current_run_id, "detected_ts": now, "created_ts": now})
            elif prev != curr:
                previous_hash = hashlib.sha256(json.dumps(prev, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
                current_hash = hashlib.sha256(json.dumps(curr, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
                changes.append({"change_run_id": run_id, "source_run_id": current_run_id, "technical_run_id": payload.technical_run_id,
                                "page_url": url, "change_type": "modified_url", "previous_value": json.dumps(prev, ensure_ascii=False),
                                "current_value": json.dumps(curr, ensure_ascii=False), "previous_run_id": previous_run_id,
                                "current_run_id": current_run_id, "detected_ts": now, "created_ts": now})
                changes.append({"change_run_id": run_id, "source_run_id": current_run_id, "technical_run_id": payload.technical_run_id,
                                "page_url": url, "change_type": "metadata_changed", "previous_value": json.dumps(prev, ensure_ascii=False),
                                "current_value": json.dumps(curr, ensure_ascii=False), "previous_run_id": previous_run_id,
                                "current_run_id": current_run_id, "detected_ts": now, "created_ts": now})
                if previous_hash != current_hash:
                    changes.append({"change_run_id": run_id, "source_run_id": current_run_id, "technical_run_id": payload.technical_run_id,
                                    "page_url": url, "change_type": "content_hash_changed", "previous_value": previous_hash,
                                    "current_value": current_hash, "previous_run_id": previous_run_id,
                                    "current_run_id": current_run_id, "detected_ts": now, "created_ts": now})

        status = "success"
        run_log = {"change_run_id": run_id, "source_run_id": current_run_id, "technical_run_id": payload.technical_run_id,
                   "started_ts": now, "ended_ts": datetime.utcnow().isoformat(), "status": status, "created_ts": datetime.utcnow().isoformat()}

        self.repository.insert_rows("change_history_run_log", [run_log])
        self.repository.insert_rows("change_history_results", changes)

        return {"run_id": run_id, "status": status, "total_changes": len(changes), "duration_seconds": round(time.time()-start,3), "message": "Change History ejecutado correctamente"}