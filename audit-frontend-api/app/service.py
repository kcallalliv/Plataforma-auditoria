from app.bigquery_repository import BigQueryRepository

class AuditFrontendService:
    def __init__(self, repository: BigQueryRepository | None = None):
        self.repository = repository or BigQueryRepository()

    def get_navigation(self):
        return {
            "platform_name": "Claro Personas Web Audit",
            "modules": [
                {"key": "overview", "label": "Resumen", "enabled": True, "route": "/"},
                {"key": "sitemap", "label": "Módulo 1 · Sitemap", "enabled": True, "route": "/modules/sitemap"},
                {"key": "technical", "label": "Módulo 2 · Técnico", "enabled": True, "route": "/modules/technical"},
                {"key": "seo", "label": "Módulo 3 · SEO", "enabled": True, "route": "/modules/seo"},
                {"key": "tagging", "label": "Módulo 4 · Tagging", "enabled": True, "route": "/modules/tagging"},
            ]
        }

    def get_overview_latest(self):
        return self.repository.get_overview_latest()

    def get_module_latest(self, module_key: str):
        mapping = {
            "sitemap": "sitemap_run_log",
            "technical": "technical_crawl_run_log",
            "seo": "seo_validation_run_log",
            "tagging": "tagging_validation_run_log",
        }
        return self.repository.get_latest_run(mapping[module_key])

    def get_module_runs(self, module_key: str, limit: int = 10):
        mapping = {
            "sitemap": "sitemap_run_log",
            "technical": "technical_crawl_run_log",
            "seo": "seo_validation_run_log",
            "tagging": "tagging_validation_run_log",
        }
        return self.repository.get_recent_runs(mapping[module_key], limit)

    def get_url_detail(self, normalized_url: str):
        return self.repository.get_url_detail(normalized_url)