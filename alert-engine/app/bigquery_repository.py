from google.cloud import bigquery
from app.config import settings

class BigQueryRepository:
    def __init__(self):
        self.client = bigquery.Client(project=settings.project_id)
        self.project_id = settings.project_id
        self.dataset_id = settings.dataset_id

    def query(self, sql: str, params: list | None = None):
        cfg = bigquery.QueryJobConfig(query_parameters=params or [])
        return list(self.client.query(sql, job_config=cfg).result())

    def insert_rows(self, table_name: str, rows: list[dict]):
        if not rows:
            return
        table_id = f"{self.project_id}.{self.dataset_id}.{table_name}"
        errors = self.client.insert_rows_json(table_id, rows)
        if errors:
            raise RuntimeError(f"BigQuery insert error in {table_id}: {errors}")

    def get_latest_technical_errors(self):
        sql = f"""
        SELECT page_url, status_code, is_priority
        FROM `{self.project_id}.{self.dataset_id}.technical_crawl_results`
        WHERE status_code >= 500
        ORDER BY checked_ts DESC
        LIMIT 200
        """
        return [dict(r.items()) for r in self.query(sql)]

    def get_latest_seo_noindex_commercial(self):
        sql = f"""
        SELECT page_url, page_group, has_noindex
        FROM `{self.project_id}.{self.dataset_id}.seo_validation_results`
        WHERE has_noindex = TRUE AND LOWER(COALESCE(page_group, '')) LIKE '%comercial%'
        ORDER BY checked_ts DESC
        LIMIT 200
        """
        return [dict(r.items()) for r in self.query(sql)]