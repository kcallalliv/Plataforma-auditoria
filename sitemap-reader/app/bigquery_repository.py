import logging
from typing import Iterable

from google.cloud import bigquery

from app.config import settings

logger = logging.getLogger(__name__)


class BigQueryRepository:
    def __init__(self) -> None:
        self.client = bigquery.Client(project=settings.project_id)
        self.project_id = settings.project_id
        self.dataset_id = settings.dataset_id

    def _table_id(self, table_name: str) -> str:
        return f"{self.project_id}.{self.dataset_id}.{table_name}"

    def insert_rows(self, table_name: str, rows: Iterable[dict]) -> None:
        rows = list(rows)
        if not rows:
            return

        table_id = self._table_id(table_name)
        errors = self.client.insert_rows_json(table_id, rows)

        if errors:
            logger.error("Error insertando en %s: %s", table_id, errors)
            raise RuntimeError(f"BigQuery insert error in {table_id}: {errors}")

    def insert_run_log(self, row: dict) -> None:
        self.insert_rows("sitemap_run_log", [row])

    def insert_raw_entries(self, rows: Iterable[dict]) -> None:
        self.insert_rows("sitemap_raw_entries", rows)

    def insert_master_urls(self, rows: Iterable[dict]) -> None:
        self.insert_rows("sitemap_master_urls", rows)