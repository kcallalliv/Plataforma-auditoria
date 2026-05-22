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
                {"key": "links", "label": "Módulo 3 · Links", "enabled": True, "route": "/modules/links"},
                {"key": "content", "label": "Módulo 5 · Content/UI", "enabled": True, "route": "/modules/content"},
                {"key": "performance", "label": "Módulo 6 · Performance", "enabled": True, "route": "/modules/performance"},
                {"key": "change-history", "label": "Módulo 7 · Change History", "enabled": True, "route": "/modules/change-history"},
                {"key": "alerts", "label": "Módulo 9 · Alertas", "enabled": True, "route": "/modules/alerts"},
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
            "links": "link_validation_run_log",
            "content": "content_validation_run_log",
            "performance": "performance_validation_run_log",
            "change-history": "change_history_run_log",
            "alerts": "alert_run_log",
        }
        if module_key == "links":
            return self.repository.get_link_latest_run()
        if module_key == "content":
            return self.repository.get_content_latest_run()
        if module_key == "performance":
            return self.repository.get_performance_latest_run()
        if module_key == "change-history":
            return self.repository.get_change_history_latest_run()
        if module_key == "alerts":
            return self.repository.get_alert_latest_run()
        return self.repository.get_latest_run(mapping[module_key])

    def get_module_runs(self, module_key: str, limit: int = 10):
        mapping = {
            "sitemap": "sitemap_run_log",
            "technical": "technical_crawl_run_log",
            "seo": "seo_validation_run_log",
            "tagging": "tagging_validation_run_log",
            "links": "link_validation_run_log",
            "content": "content_validation_run_log",
            "performance": "performance_validation_run_log",
            "change-history": "change_history_run_log",
            "alerts": "alert_run_log",
        }
        return self.repository.get_recent_runs(mapping[module_key], limit)

    def get_url_detail(self, normalized_url: str):
        return self.repository.get_url_detail(normalized_url)