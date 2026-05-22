from google.cloud import bigquery
from app.config import settings

class BigQueryRepository:
    def __init__(self):
        self.client = bigquery.Client(project=settings.project_id)
        self.project_id = settings.project_id
        self.dataset_id = settings.dataset_id

    def insert_rows(self, table_name: str, rows: list[dict]):
        if not rows:
            return
        table_id = f"{self.project_id}.{self.dataset_id}.{table_name}"
        errors = self.client.insert_rows_json(table_id, rows)
        if errors:
            raise RuntimeError(f"BigQuery insert error in {table_id}: {errors}")

    def get_latest_source_run_ids(self):
        sql = f"""
        SELECT DISTINCT run_id
        FROM `{self.project_id}.{self.dataset_id}.sitemap_master_urls`
        ORDER BY run_id DESC
        LIMIT 2
        """
        rows = list(self.client.query(sql).result())
        return [r["run_id"] for r in rows]

    def get_sitemap_urls_for_run(self, run_id: str):
        sql = f"""
        SELECT page_url, CAST(is_priority AS STRING) AS is_priority, CAST(should_audit AS STRING) AS should_audit
        FROM `{self.project_id}.{self.dataset_id}.sitemap_master_urls`
        WHERE run_id = @run_id
        """
        cfg = bigquery.QueryJobConfig(query_parameters=[bigquery.ScalarQueryParameter("run_id", "STRING", run_id)])
        rows = list(self.client.query(sql, job_config=cfg).result())
        return [dict(r.items()) for r in rows]