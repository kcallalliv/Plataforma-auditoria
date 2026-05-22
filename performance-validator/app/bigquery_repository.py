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

    def get_urls_to_measure(self, source_run_id: str | None, only_priority: bool, max_urls: int | None):
        query = f"""
        SELECT DISTINCT
          run_id AS source_run_id,
          page_url,
          normalized_url,
          url_hash,
          url_type,
          page_group,
          IFNULL(is_priority, FALSE) AS is_priority
        FROM `{self.project_id}.{self.dataset_id}.sitemap_master_urls`
        WHERE should_audit = TRUE
        """
        params = []
        if source_run_id:
            query += " AND run_id = @source_run_id"
            params.append(bigquery.ScalarQueryParameter("source_run_id", "STRING", source_run_id))
        if only_priority:
            query += " AND IFNULL(is_priority, FALSE) = TRUE"
        query += " ORDER BY page_group, url_type"
        if max_urls:
            query += " LIMIT @max_urls"
            params.append(bigquery.ScalarQueryParameter("max_urls", "INT64", max_urls))

        job_config = bigquery.QueryJobConfig(query_parameters=params)
        return list(self.client.query(query, job_config=job_config).result())

    def get_previous_result(self, page_url: str, strategy: str):
        sql = f"""
        SELECT *
        FROM `{self.project_id}.{self.dataset_id}.performance_validation_results`
        WHERE page_url = @page_url
          AND strategy = @strategy
          AND performance_score IS NOT NULL
        ORDER BY created_ts DESC
        LIMIT 1
        """
        params = [
            bigquery.ScalarQueryParameter("page_url", "STRING", page_url),
            bigquery.ScalarQueryParameter("strategy", "STRING", strategy),
        ]
        rows = list(self.client.query(sql, job_config=bigquery.QueryJobConfig(query_parameters=params)).result())
        return dict(rows[0].items()) if rows else None