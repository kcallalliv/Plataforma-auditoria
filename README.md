# Claro Personas Audit - Plan de ejecución por fases

## Fase 1 (actual)
- Revalidación completa de `checklist_reglas_auditoria_web_claro.csv`.
- Documentación técnica y roadmap.
- DDL BigQuery para nuevos módulos y ampliaciones.

## Validación de salida Fase 2
- Ver checklist operativo en: `docs/fase2_exit_checklist.md`.
- Ver smoke validation paso a paso en: `docs/fase2_smoke_validation.md`.

## Validación de salida Fase 4
- Ver checklist operativo M6 en: `docs/fase4_exit_checklist.md`.

## Validación de salida Fase 5
- Ver checklist operativo M5 en: `docs/fase5_exit_checklist.md`.
- Ver smoke validation M5 en: `docs/fase5_smoke_validation.md`.

## Validación de salida Fase 6
- Ver checklist operativo M7 en: `docs/fase6_exit_checklist.md`.
- Ver smoke validation M7 en: `docs/fase6_smoke_validation.md`.

## Validación de salida Fase 7
- Ver checklist operativo M9 en: `docs/fase7_exit_checklist.md`.
- Ver smoke validation M9 en: `docs/fase7_smoke_validation.md`.

## Validación de salida Fase 8
- Ver checklist operativo M10 en: `docs/fase8_exit_checklist.md`.
- Ver smoke validation M10 en: `docs/fase8_smoke_validation.md`.

## Módulos y ejecución (objetivo)
1. M1 Sitemap Reader
2. M2 Technical Crawler
3. M3 Link Validator
4. M4 SEO Validator
5. M5 Content/UI Compliance
6. M6 Performance Validator
7. M7 Change History
8. M8 Tagging Validator
9. M9 Alert Engine
10. M10 Data & Dashboard

## Variables de entorno base (referenciales)
- `GOOGLE_CLOUD_PROJECT=prd-claro-mktg-data-storage`
- `BQ_DATASET=seo_audit`
- `GCP_REGION`
- `ALLOWED_DOMAIN`
- `RUNTIME_SCAN_ENABLED`
- `PAGESPEED_API_KEY` (M6)
- `PAGESPEED_BASE_URL` (default: `https://www.googleapis.com/pagespeedonline/v5/runPagespeed`)
- `PAGESPEED_TIMEOUT_SECONDS` (default: `30`)
- `PAGESPEED_MAX_RETRIES` (default: `2`)
- `PAGESPEED_MAX_WORKERS` (default: `4`)
- `PAGESPEED_SLEEP_MS` (default: `150`)
- `PLAYWRIGHT_ENABLED` (M5; `true/false`)
- `ALLOWED_FONTS` (M5; default: `Roboto,AMX`)
- `FORBIDDEN_TERMS` (M5; CSV)
- `COMPETITOR_TERMS` (M5; CSV)
- `PLACEHOLDER_TERMS` (M5; CSV)
- `REQUIRED_DISCLAIMERS` (M5; CSV)

> **Dónde configurar API key de PageSpeed (Fase 4):**\n
> En Cloud Run del servicio `performance-validator`, configurar variable de entorno `PAGESPEED_API_KEY`.\n
> Si no se configura, el módulo ejecuta estructura base y registra error de configuración sin romper el flujo.

## Ejecución local (patrón)
```bash
cd <modulo>
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

## Ejemplos curl (referenciales)
```bash
curl -X POST http://localhost:8080/run/sitemap-reader -H 'Content-Type: application/json' -d '{"sitemap_url":"https://dominio/sitemap.xml"}'
curl -X POST http://localhost:8080/run/technical-crawler -H 'Content-Type: application/json' -d '{"source_run_id":"...","device_profiles":["mobile","desktop"]}'
curl -X POST http://localhost:8080/run/link-validator -H 'Content-Type: application/json' -d '{"source_run_id":"...","technical_run_id":"...","only_priority":true,"max_urls":100,"device_profile":"mobile"}'
curl -X POST http://localhost:8080/run/content-validator -H 'Content-Type: application/json' -d '{"source_run_id":"...","max_urls":100,"device_profile":"mobile"}'
curl -X POST http://localhost:8080/run/performance-validator -H 'Content-Type: application/json' -d '{"source_run_id":"...","only_priority":true,"max_urls":20,"strategies":["mobile","desktop"]}'
curl -X POST http://localhost:8080/run/change-history -H 'Content-Type: application/json' -d '{"source_run_id":"...","technical_run_id":"..."}'
curl -X POST http://localhost:8080/run/alert-engine -H 'Content-Type: application/json' -d '{"source_run_id":"...","technical_run_id":"..."}'
```

## Despliegue Cloud Run (patrón)
```bash
gcloud builds submit --tag ${REGION}-docker.pkg.dev/${GOOGLE_CLOUD_PROJECT}/audit/<service>:latest

gcloud run deploy <service> \
  --image ${REGION}-docker.pkg.dev/${GOOGLE_CLOUD_PROJECT}/audit/<service>:latest \
  --region ${REGION} \
  --platform managed \
  --allow-unauthenticated
```

## Orden recomendado de ejecución
1. Sitemap Reader
2. Technical Crawler
3. SEO Validator / Tagging Validator
4. Link Validator
5. Content Validator
6. Performance Validator
7. Change History
8. Alert Engine
9. Consulta consolidada en BFF + Frontend

## Nota BigQuery (particionado)
- Las tablas históricas previas del proyecto no usan `PARTITION BY`.
- Recomendación para nuevas tablas de alto volumen: `PARTITION BY DATE(created_ts)` y `CLUSTER BY page_url, severity, device_profile`.
- Para tablas existentes, aplicar migración controlada (CTAS + swap) en una ventana planificada para evitar impacto operativo.