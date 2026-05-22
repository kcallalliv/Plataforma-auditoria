import logging
from google.cloud import bigquery
from app.config import settings

logger = logging.getLogger(__name__)

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

    def get_urls_to_validate(self, source_run_id: str | None, max_urls: int | None):
        query = f"""
        SELECT DISTINCT run_id AS source_run_id, page_url, normalized_url, url_hash, url_type, page_group
        FROM `{self.project_id}.{self.dataset_id}.sitemap_master_urls`
        WHERE should_audit = TRUE
        """
        params = []
        if source_run_id:
            query += " AND run_id = @source_run_id"
            params.append(bigquery.ScalarQueryParameter("source_run_id", "STRING", source_run_id))
        query += " ORDER BY page_group, url_type"
        if max_urls:
            query += " LIMIT @max_urls"
            params.append(bigquery.ScalarQueryParameter("max_urls", "INT64", max_urls))
        job_config = bigquery.QueryJobConfig(query_parameters=params)
        return list(self.client.query(query, job_config=job_config).result())