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

    def get_results_by_run(self, table_name: str, run_id: str, limit: int = 100, device_profile: str | None = None, page_url: str | None = None):
        sql = f"""
        SELECT *
        FROM `{self.project_id}.{self.dataset_id}.{table_name}`
        WHERE run_id = @run_id
          AND (@device_profile IS NULL OR device_profile = @device_profile)
          AND (@page_url IS NULL OR page_url = @page_url)
        ORDER BY checked_ts DESC
        LIMIT @limit
        """
        params = [
            bigquery.ScalarQueryParameter("run_id", "STRING", run_id),
            bigquery.ScalarQueryParameter("device_profile", "STRING", device_profile),
            bigquery.ScalarQueryParameter("page_url", "STRING", page_url),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
        return [dict(r.items()) for r in self.query(sql, params)]

    def get_findings_by_run(
        self,
        table_name: str,
        run_id: str,
        limit: int = 100,
        severity: str | None = None,
        finding_code: str | None = None,
        page_url: str | None = None,
    ):
        sql = f"""
        SELECT *
        FROM `{self.project_id}.{self.dataset_id}.{table_name}`
        WHERE run_id = @run_id
          AND (@severity IS NULL OR LOWER(severity) = LOWER(@severity))
          AND (@finding_code IS NULL OR finding_code = @finding_code)
          AND (@page_url IS NULL OR page_url = @page_url)
        ORDER BY created_ts DESC
        LIMIT @limit
        """
        params = [
            bigquery.ScalarQueryParameter("run_id", "STRING", run_id),
            bigquery.ScalarQueryParameter("severity", "STRING", severity),
            bigquery.ScalarQueryParameter("finding_code", "STRING", finding_code),
            bigquery.ScalarQueryParameter("page_url", "STRING", page_url),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
        return [dict(r.items()) for r in self.query(sql, params)]
    
    def get_link_latest_run(self):
        sql = f"""
        SELECT *
        FROM `{self.project_id}.{self.dataset_id}.link_validation_run_log`
        ORDER BY created_ts DESC
        LIMIT 1
        """
        rows = self.query(sql)
        return dict(rows[0].items()) if rows else None

    def get_link_results_by_run(self, run_id: str, limit: int = 100, device_profile: str | None = None, page_url: str | None = None):
        sql = f"""
        SELECT *
        FROM `{self.project_id}.{self.dataset_id}.link_validation_results`
        WHERE link_run_id = @run_id
          AND (@device_profile IS NULL OR device_profile = @device_profile)
          AND (@page_url IS NULL OR page_url = @page_url)
        ORDER BY created_ts DESC
        LIMIT @limit
        """
        params = [
            bigquery.ScalarQueryParameter("run_id", "STRING", run_id),
            bigquery.ScalarQueryParameter("device_profile", "STRING", device_profile),
            bigquery.ScalarQueryParameter("page_url", "STRING", page_url),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
        return [dict(r.items()) for r in self.query(sql, params)]

    def get_link_findings_by_run(self, run_id: str, limit: int = 100, severity: str | None = None, finding_code: str | None = None, page_url: str | None = None):
        sql = f"""
        SELECT *
        FROM `{self.project_id}.{self.dataset_id}.link_validation_findings`
        WHERE link_run_id = @run_id
          AND (@severity IS NULL OR LOWER(severity) = LOWER(@severity))
          AND (@finding_code IS NULL OR finding_type = @finding_code)
          AND (@page_url IS NULL OR page_url = @page_url)
        ORDER BY created_ts DESC
        LIMIT @limit
        """
        params = [
            bigquery.ScalarQueryParameter("run_id", "STRING", run_id),
            bigquery.ScalarQueryParameter("severity", "STRING", severity),
            bigquery.ScalarQueryParameter("finding_code", "STRING", finding_code),
            bigquery.ScalarQueryParameter("page_url", "STRING", page_url),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
        return [dict(r.items()) for r in self.query(sql, params)]

    def get_link_kpis_by_run(self, run_id: str):
        sql = f"""
        SELECT
          COUNT(*) AS total_links,
          COUNTIF(is_broken = TRUE) AS broken_links,
          COUNTIF(link_type = 'internal') AS internal_links,
          COUNTIF(link_type = 'external') AS external_links,
          COUNTIF(link_type = 'pdf') AS pdf_links,
          COUNTIF(link_type = 'image') AS image_links,
          COUNTIF(link_type = 'anchor') AS anchor_links,
          COUNTIF(is_broken = TRUE AND link_type = 'internal') AS broken_internal_links,
          COUNTIF(is_broken = TRUE AND link_type = 'external') AS broken_external_links
        FROM `{self.project_id}.{self.dataset_id}.link_validation_results`
        WHERE link_run_id = @run_id
        """
        params = [bigquery.ScalarQueryParameter("run_id", "STRING", run_id)]
        rows = self.query(sql, params)
        return dict(rows[0].items()) if rows else {}

    def get_link_summary_by_run(self, run_id: str):
        sql = f"""
        SELECT
          finding_type,
          severity,
          COUNT(*) AS findings_count
        FROM `{self.project_id}.{self.dataset_id}.link_validation_findings`
        WHERE link_run_id = @run_id
        GROUP BY finding_type, severity
        ORDER BY findings_count DESC
        """
        params = [bigquery.ScalarQueryParameter("run_id", "STRING", run_id)]
        return [dict(r.items()) for r in self.query(sql, params)]

    def get_link_top_broken_pages(self, run_id: str, limit: int = 10):
        sql = f"""
        SELECT
          page_url,
          COUNTIF(is_broken = TRUE) AS broken_links,
          COUNT(*) AS total_links
        FROM `{self.project_id}.{self.dataset_id}.link_validation_results`
        WHERE link_run_id = @run_id
        GROUP BY page_url
        HAVING broken_links > 0
        ORDER BY broken_links DESC, total_links DESC
        LIMIT @limit
        """
        params = [
            bigquery.ScalarQueryParameter("run_id", "STRING", run_id),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
        return [dict(r.items()) for r in self.query(sql, params)]

    def get_performance_latest_run(self):
        sql = f"""
        SELECT *
        FROM `{self.project_id}.{self.dataset_id}.performance_validation_run_log`
        ORDER BY created_ts DESC
        LIMIT 1
        """
        rows = self.query(sql)
        return dict(rows[0].items()) if rows else None

    def get_performance_results_by_run(self, run_id: str, limit: int = 100, strategy: str | None = None, page_url: str | None = None):
        sql = f"""
        SELECT *
        FROM `{self.project_id}.{self.dataset_id}.performance_validation_results`
        WHERE performance_run_id = @run_id
          AND (@strategy IS NULL OR strategy = @strategy)
          AND (@page_url IS NULL OR page_url = @page_url)
        ORDER BY created_ts DESC
        LIMIT @limit
        """
        params = [
            bigquery.ScalarQueryParameter("run_id", "STRING", run_id),
            bigquery.ScalarQueryParameter("strategy", "STRING", strategy),
            bigquery.ScalarQueryParameter("page_url", "STRING", page_url),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
        return [dict(r.items()) for r in self.query(sql, params)]

    def get_performance_findings_by_run(self, run_id: str, limit: int = 100, severity: str | None = None, finding_code: str | None = None, page_url: str | None = None):
        sql = f"""
        SELECT *
        FROM `{self.project_id}.{self.dataset_id}.performance_validation_findings`
        WHERE performance_run_id = @run_id
          AND (@severity IS NULL OR LOWER(severity) = LOWER(@severity))
          AND (@finding_code IS NULL OR finding_code = @finding_code)
          AND (@page_url IS NULL OR page_url = @page_url)
        ORDER BY created_ts DESC
        LIMIT @limit
        """
        params = [
            bigquery.ScalarQueryParameter("run_id", "STRING", run_id),
            bigquery.ScalarQueryParameter("severity", "STRING", severity),
            bigquery.ScalarQueryParameter("finding_code", "STRING", finding_code),
            bigquery.ScalarQueryParameter("page_url", "STRING", page_url),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
        return [dict(r.items()) for r in self.query(sql, params)]

    def get_content_latest_run(self):
        sql = f"""
        SELECT *
        FROM `{self.project_id}.{self.dataset_id}.content_validation_run_log`
        ORDER BY created_ts DESC
        LIMIT 1
        """
        rows = self.query(sql)
        return dict(rows[0].items()) if rows else None

    def get_content_results_by_run(self, run_id: str, limit: int = 100, device_profile: str | None = None, page_url: str | None = None):
        sql = f"""
        SELECT *
        FROM `{self.project_id}.{self.dataset_id}.content_validation_results`
        WHERE content_run_id = @run_id
          AND (@device_profile IS NULL OR device_profile = @device_profile)
          AND (@page_url IS NULL OR page_url = @page_url)
        ORDER BY created_ts DESC
        LIMIT @limit
        """
        params = [
            bigquery.ScalarQueryParameter("run_id", "STRING", run_id),
            bigquery.ScalarQueryParameter("device_profile", "STRING", device_profile),
            bigquery.ScalarQueryParameter("page_url", "STRING", page_url),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
        return [dict(r.items()) for r in self.query(sql, params)]

    def get_content_findings_by_run(self, run_id: str, limit: int = 100, severity: str | None = None, finding_code: str | None = None, page_url: str | None = None):
        sql = f"""
        SELECT *
        FROM `{self.project_id}.{self.dataset_id}.content_validation_findings`
        WHERE content_run_id = @run_id
          AND (@severity IS NULL OR LOWER(severity) = LOWER(@severity))
          AND (@finding_code IS NULL OR finding_type = @finding_code OR rule_id = @finding_code)
          AND (@page_url IS NULL OR page_url = @page_url)
        ORDER BY created_ts DESC
        LIMIT @limit
        """
        params = [
            bigquery.ScalarQueryParameter("run_id", "STRING", run_id),
            bigquery.ScalarQueryParameter("severity", "STRING", severity),
            bigquery.ScalarQueryParameter("finding_code", "STRING", finding_code),
            bigquery.ScalarQueryParameter("page_url", "STRING", page_url),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
        return [dict(r.items()) for r in self.query(sql, params)]

    def get_content_kpis_by_run(self, run_id: str):
        sql = f"""
        SELECT
          COUNT(*) AS total_pages,
          COUNTIF(thin_content_detected = TRUE) AS thin_content_pages,
          SUM(COALESCE(invalid_font_count, 0)) AS invalid_font_total,
          SUM(COALESCE(invalid_button_font_count, 0)) AS invalid_button_font_total,
          SUM(COALESCE(invalid_text_font_count, 0)) AS invalid_text_font_total,
          COUNTIF(ARRAY_LENGTH(detected_terms) > 0) AS pages_with_forbidden_terms,
          COUNTIF(placeholder_detected = TRUE) AS pages_with_placeholder
        FROM `{self.project_id}.{self.dataset_id}.content_validation_results`
        WHERE content_run_id = @run_id
        """
        params = [bigquery.ScalarQueryParameter("run_id", "STRING", run_id)]
        rows = self.query(sql, params)
        return dict(rows[0].items()) if rows else {}

    def get_content_summary_by_run(self, run_id: str):
        sql = f"""
        SELECT
          finding_type,
          severity,
          COUNT(*) AS findings_count
        FROM `{self.project_id}.{self.dataset_id}.content_validation_findings`
        WHERE content_run_id = @run_id
        GROUP BY finding_type, severity
        ORDER BY findings_count DESC
        """
        params = [bigquery.ScalarQueryParameter("run_id", "STRING", run_id)]
        return [dict(r.items()) for r in self.query(sql, params)]

    def get_change_history_latest_run(self):
        sql = f"""
        SELECT *
        FROM `{self.project_id}.{self.dataset_id}.change_history_run_log`
        ORDER BY created_ts DESC
        LIMIT 1
        """
        rows = self.query(sql)
        return dict(rows[0].items()) if rows else None

    def get_change_history_results_by_run(self, run_id: str, limit: int = 100, page_url: str | None = None):
        sql = f"""
        SELECT *
        FROM `{self.project_id}.{self.dataset_id}.change_history_results`
        WHERE change_run_id = @run_id
          AND (@page_url IS NULL OR page_url = @page_url)
        ORDER BY detected_ts DESC
        LIMIT @limit
        """
        params = [
            bigquery.ScalarQueryParameter("run_id", "STRING", run_id),
            bigquery.ScalarQueryParameter("page_url", "STRING", page_url),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
        return [dict(r.items()) for r in self.query(sql, params)]

    def get_change_history_summary_by_run(self, run_id: str):
        sql = f"""
        SELECT
          change_type,
          COUNT(*) AS changes_count
        FROM `{self.project_id}.{self.dataset_id}.change_history_results`
        WHERE change_run_id = @run_id
        GROUP BY change_type
        ORDER BY changes_count DESC
        """
        params = [bigquery.ScalarQueryParameter("run_id", "STRING", run_id)]
        return [dict(r.items()) for r in self.query(sql, params)]

    def compare_runs(self, current_run_id: str, previous_run_id: str, limit: int = 500):
        sql = f"""
        SELECT *
        FROM `{self.project_id}.{self.dataset_id}.change_history_results`
        WHERE current_run_id = @current_run_id
          AND previous_run_id = @previous_run_id
        ORDER BY detected_ts DESC
        LIMIT @limit
        """
        params = [
            bigquery.ScalarQueryParameter("current_run_id", "STRING", current_run_id),
            bigquery.ScalarQueryParameter("previous_run_id", "STRING", previous_run_id),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
        return [dict(r.items()) for r in self.query(sql, params)]

    def get_findings_summary_latest(self):
        sql = f"""
        WITH latest_runs AS (
          SELECT
            (SELECT run_id FROM `{self.project_id}.{self.dataset_id}.technical_crawl_run_log` ORDER BY run_ts DESC LIMIT 1) AS technical_run_id,
            (SELECT run_id FROM `{self.project_id}.{self.dataset_id}.seo_validation_run_log` ORDER BY run_ts DESC LIMIT 1) AS seo_run_id,
            (SELECT run_id FROM `{self.project_id}.{self.dataset_id}.tagging_validation_run_log` ORDER BY run_ts DESC LIMIT 1) AS tagging_run_id
        ),
        union_findings AS (
          SELECT 'technical' AS module_name, finding_code, severity
          FROM `{self.project_id}.{self.dataset_id}.technical_crawl_findings`
          WHERE run_id = (SELECT technical_run_id FROM latest_runs)
          UNION ALL
          SELECT 'seo' AS module_name, finding_code, severity
          FROM `{self.project_id}.{self.dataset_id}.seo_validation_findings`
          WHERE run_id = (SELECT seo_run_id FROM latest_runs)
          UNION ALL
          SELECT 'tagging' AS module_name, finding_code, severity
          FROM `{self.project_id}.{self.dataset_id}.tagging_validation_findings`
          WHERE run_id = (SELECT tagging_run_id FROM latest_runs)
        )
        SELECT module_name, finding_code, severity, COUNT(*) AS findings_count
        FROM union_findings
        GROUP BY module_name, finding_code, severity
        ORDER BY findings_count DESC
        """
        return [dict(r.items()) for r in self.query(sql)]

    def get_findings_by_url(self, page_url: str, limit: int = 200):
        sql = f"""
        SELECT *
        FROM (
          SELECT 'technical' AS module_name, page_url, finding_code, finding_detail, severity, recommendation, created_ts
          FROM `{self.project_id}.{self.dataset_id}.technical_crawl_findings`
          WHERE page_url = @page_url
          UNION ALL
          SELECT 'seo' AS module_name, page_url, finding_code, finding_detail, severity, recommendation, created_ts
          FROM `{self.project_id}.{self.dataset_id}.seo_validation_findings`
          WHERE page_url = @page_url
          UNION ALL
          SELECT 'tagging' AS module_name, page_url, finding_code, finding_detail, severity, recommendation, created_ts
          FROM `{self.project_id}.{self.dataset_id}.tagging_validation_findings`
          WHERE page_url = @page_url
        )
        ORDER BY created_ts DESC
        LIMIT @limit
        """
        params = [
            bigquery.ScalarQueryParameter("page_url", "STRING", page_url),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
        return [dict(r.items()) for r in self.query(sql, params)]

    def get_alert_latest_run(self):
        sql = f"""
        SELECT *
        FROM `{self.project_id}.{self.dataset_id}.alert_run_log`
        ORDER BY created_ts DESC
        LIMIT 1
        """
        rows = self.query(sql)
        return dict(rows[0].items()) if rows else None

    def get_alert_events_by_run(self, run_id: str, limit: int = 100, severity: str | None = None, page_url: str | None = None):
        sql = f"""
        SELECT *
        FROM `{self.project_id}.{self.dataset_id}.alert_events`
        WHERE alert_run_id = @run_id
          AND (@severity IS NULL OR LOWER(severity) = LOWER(@severity))
          AND (@page_url IS NULL OR page_url = @page_url)
        ORDER BY created_ts DESC
        LIMIT @limit
        """
        params = [
            bigquery.ScalarQueryParameter("run_id", "STRING", run_id),
            bigquery.ScalarQueryParameter("severity", "STRING", severity),
            bigquery.ScalarQueryParameter("page_url", "STRING", page_url),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
        return [dict(r.items()) for r in self.query(sql, params)]

    def get_alert_summary_by_run(self, run_id: str):
        sql = f"""
        SELECT
          alert_type,
          severity,
          COUNT(*) AS alerts_count
        FROM `{self.project_id}.{self.dataset_id}.alert_events`
        WHERE alert_run_id = @run_id
        GROUP BY alert_type, severity
        ORDER BY alerts_count DESC
        """
        params = [bigquery.ScalarQueryParameter("run_id", "STRING", run_id)]
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