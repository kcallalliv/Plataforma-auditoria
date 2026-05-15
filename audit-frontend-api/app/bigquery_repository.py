import logging
from google.cloud import bigquery
from app.config import settings

logger = logging.getLogger(__name__)

class BigQueryRepository:
    def __init__(self):
        self.client = bigquery.Client(project=settings.project_id)
        self.project_id = settings.project_id
        self.dataset_id = settings.dataset_id

    def query(self, sql: str, params: list | None = None):
        job_config = bigquery.QueryJobConfig(query_parameters=params or [])
        return list(self.client.query(sql, job_config=job_config).result())

    def get_latest_run(self, table_name: str):
        sql = f"""
        SELECT *
        FROM `{self.project_id}.{self.dataset_id}.{table_name}`
        ORDER BY run_ts DESC
        LIMIT 1
        """
        rows = self.query(sql)
        return dict(rows[0].items()) if rows else None

    def get_recent_runs(self, table_name: str, limit: int = 10):
        sql = f"""
        SELECT *
        FROM `{self.project_id}.{self.dataset_id}.{table_name}`
        ORDER BY run_ts DESC
        LIMIT @limit
        """
        params = [bigquery.ScalarQueryParameter("limit", "INT64", limit)]
        return [dict(r.items()) for r in self.query(sql, params)]

    def get_sitemap_urls_by_run(self, run_id: str, limit: int = 100):
        sql = f"""
        SELECT
          page_url,
          normalized_url,
          normalized_path,
          url_type,
          page_group,
          is_priority,
          should_audit,
          priority_group,
          http_status,
          redirect_type,
          final_url,
          is_valid_status,
          sitemap_issue
        FROM `{self.project_id}.{self.dataset_id}.sitemap_master_urls`
        WHERE run_id = @run_id
        ORDER BY is_priority DESC, normalized_path
        LIMIT @limit
        """
        params = [
            bigquery.ScalarQueryParameter("run_id", "STRING", run_id),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
        return [dict(r.items()) for r in self.query(sql, params)]

    def get_results_by_run(self, table_name: str, run_id: str, limit: int = 100):
        sql = f"""
        SELECT *
        FROM `{self.project_id}.{self.dataset_id}.{table_name}`
        WHERE run_id = @run_id
        ORDER BY checked_ts DESC
        LIMIT @limit
        """
        params = [
            bigquery.ScalarQueryParameter("run_id", "STRING", run_id),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
        return [dict(r.items()) for r in self.query(sql, params)]

    def get_findings_by_run(self, table_name: str, run_id: str, limit: int = 100):
        sql = f"""
        SELECT *
        FROM `{self.project_id}.{self.dataset_id}.{table_name}`
        WHERE run_id = @run_id
        ORDER BY created_ts DESC
        LIMIT @limit
        """
        params = [
            bigquery.ScalarQueryParameter("run_id", "STRING", run_id),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
        return [dict(r.items()) for r in self.query(sql, params)]

    def get_url_detail(self, normalized_url: str):
        sql = f"""
        WITH sitemap AS (
          SELECT *
          FROM `{self.project_id}.{self.dataset_id}.sitemap_master_urls`
          WHERE normalized_url = @normalized_url
          ORDER BY created_ts DESC
          LIMIT 1
        ),
        technical AS (
          SELECT *
          FROM `{self.project_id}.{self.dataset_id}.technical_crawl_results`
          WHERE normalized_url = @normalized_url
          ORDER BY checked_ts DESC
          LIMIT 1
        ),
        seo AS (
          SELECT *
          FROM `{self.project_id}.{self.dataset_id}.seo_validation_results`
          WHERE normalized_url = @normalized_url
          ORDER BY checked_ts DESC
          LIMIT 1
        ),
        tagging AS (
          SELECT *
          FROM `{self.project_id}.{self.dataset_id}.tagging_validation_results`
          WHERE normalized_url = @normalized_url
          ORDER BY checked_ts DESC
          LIMIT 1
        )
        SELECT
          (SELECT AS STRUCT * FROM sitemap) AS sitemap,
          (SELECT AS STRUCT * FROM technical) AS technical,
          (SELECT AS STRUCT * FROM seo) AS seo,
          (SELECT AS STRUCT * FROM tagging) AS tagging
        """
        params = [bigquery.ScalarQueryParameter("normalized_url", "STRING", normalized_url)]
        rows = self.query(sql, params)
        return dict(rows[0].items()) if rows else None

    def get_overview_latest(self):
        sql = f"""
        SELECT
          (SELECT AS STRUCT * FROM `{self.project_id}.{self.dataset_id}.sitemap_run_log` ORDER BY run_ts DESC LIMIT 1) AS sitemap,
          (SELECT AS STRUCT * FROM `{self.project_id}.{self.dataset_id}.technical_crawl_run_log` ORDER BY run_ts DESC LIMIT 1) AS technical,
          (SELECT AS STRUCT * FROM `{self.project_id}.{self.dataset_id}.seo_validation_run_log` ORDER BY run_ts DESC LIMIT 1) AS seo,
          (SELECT AS STRUCT * FROM `{self.project_id}.{self.dataset_id}.tagging_validation_run_log` ORDER BY run_ts DESC LIMIT 1) AS tagging
        """
        rows = self.query(sql)
        return dict(rows[0].items()) if rows else None
    
    def get_seo_kpis_by_run(self, run_id: str):
        sql = f"""
        SELECT
          COUNT(DISTINCT page_url) AS total_pages,
          COUNTIF(h1_count = 0) AS pages_without_h1,
          COUNTIF(title_length < 30) AS titles_too_short,
          COUNTIF(title_length > 60) AS titles_too_long,
          COUNTIF(meta_description_length < 70) AS metas_too_short,
          COUNTIF(meta_description_length > 160) AS metas_too_long,
          COUNTIF(h1_count > 1) AS pages_with_multiple_h1
        FROM `{self.project_id}.{self.dataset_id}.seo_validation_results`
        WHERE run_id = @run_id
        """
        params = [bigquery.ScalarQueryParameter("run_id", "STRING", run_id)]
        rows = self.query(sql, params)
        return dict(rows[0].items()) if rows else {}
    
    def get_sitemap_kpis_by_run(self, run_id: str):
        sql = f"""
        SELECT
          COUNT(*) AS total_urls,
          COUNTIF(http_status = 200) AS urls_status_200,
          COUNTIF(http_status = 301) AS urls_status_301,
          COUNTIF(http_status = 302) AS urls_status_302,
          COUNTIF(http_status >= 400) AS urls_status_4xx_5xx,
          COUNTIF(is_valid_status = FALSE) AS urls_invalid_status
        FROM `{self.project_id}.{self.dataset_id}.sitemap_master_urls`
        WHERE run_id = @run_id
        """
        params = [bigquery.ScalarQueryParameter("run_id", "STRING", run_id)]
        rows = self.query(sql, params)
        return dict(rows[0].items()) if rows else {}