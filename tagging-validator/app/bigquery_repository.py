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

    def get_urls_to_validate(self, source_run_id: str | None, technical_run_id: str | None, only_status_200: bool, max_urls: int | None):
        query = f"""
        SELECT
          m.run_id AS source_run_id,
          m.page_url,
          m.normalized_url,
          m.url_hash,
          m.normalized_path,
          m.url_type,
          m.page_group
        FROM `{self.project_id}.{self.dataset_id}.sitemap_master_urls` m
        """

        params = []
        where_clauses = ["m.should_audit = TRUE"]

        if only_status_200:
            query += f"""
            INNER JOIN `{self.project_id}.{self.dataset_id}.technical_crawl_results` t
              ON m.normalized_url = t.normalized_url
            """
            where_clauses.append("t.status_code = 200")

            if technical_run_id:
                where_clauses.append("t.run_id = @technical_run_id")
                params.append(bigquery.ScalarQueryParameter("technical_run_id", "STRING", technical_run_id))

        if source_run_id:
            where_clauses.append("m.run_id = @source_run_id")
            params.append(bigquery.ScalarQueryParameter("source_run_id", "STRING", source_run_id))

        query += " WHERE " + " AND ".join(where_clauses)
        query += " ORDER BY m.page_group, m.url_type"

        if max_urls:
            query += " LIMIT @max_urls"
            params.append(bigquery.ScalarQueryParameter("max_urls", "INT64", max_urls))

        job_config = bigquery.QueryJobConfig(query_parameters=params)
        return list(self.client.query(query, job_config=job_config).result())