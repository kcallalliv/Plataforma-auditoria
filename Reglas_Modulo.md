# Reglas mapeadas por módulo

Este documento resume, de forma operativa, **qué reglas aplica cada módulo** de la plataforma y cómo se traducen en campos/tablas.

---

## 1) Módulo Sitemap Reader (`sitemap-reader`)

## 1.1 Reglas de descubrimiento y parsing
- Descarga XML de cada sitemap raíz.
- Parsea nodos `url` y extrae:
  - `loc`
  - `lastmod`
  - `changefreq`
  - `priority`
- Registra cada entrada cruda en `sitemap_raw_entries`.

## 1.2 Reglas de normalización
- Normaliza URL (`normalized_url`).
- Separa dominio, path y query string.
- Normaliza path (`normalized_path`) para aplicar reglas de priorización.
- Genera `url_hash` para deduplicación.

## 1.3 Reglas de exclusión y elegibilidad
- **Dominio permitido**: excluye si no pertenece a `allowed_domains`.
- **Extensiones excluidas**: excluye si el path termina en extensiones bloqueadas.
- **Duplicados**: excluye URLs repetidas por `url_hash` dentro de la corrida.
- **Prioridad MVP**: solo marca auditables las URLs cuyo `normalized_path` esté en `PRIORITY_PATHS`.
- Resultado final:
  - `is_excluded`, `exclusion_reason`
  - `is_priority`, `priority_source`
  - `should_audit`

## 1.4 Reglas de validación HTTP de URL en sitemap
- Hace request sin seguir redirecciones (`allow_redirects=False`) para validar salud de URL publicada.
- Mapeo:
  - 200 → `is_valid_status = TRUE`
  - 301/302 → issue por redirección
  - >=400 → issue por error HTTP
  - excepción → issue por fallo de validación
- Persistencia en `sitemap_master_urls`:
  - `http_status`, `redirect_type`, `final_url`, `is_valid_status`, `sitemap_issue`.

## 1.5 Tablas impactadas
- `sitemap_run_log`
- `sitemap_raw_entries`
- `sitemap_master_urls`

---

## 2) Módulo Technical Crawler (`technical_crawler`)

## 2.1 Reglas de selección de URLs
Fuente: `sitemap_master_urls`.
- Filtro base: `should_audit = TRUE`.
- Filtro opcional por corrida: `run_id = source_run_id`.
- Filtro opcional de prioridad: `is_priority = TRUE` cuando `only_priority` está activo.
- Límite opcional: `max_urls`.

## 2.2 Reglas de crawling técnico
- Request HTTP con redirecciones habilitadas (`allow_redirects=True`).
- Captura:
  - `status_code`, `final_url`, `final_domain`
  - `response_time_ms`
  - `redirect_count`
  - headers: `content_type`, `content_length`, `server_header`, `cache_control`
- Resultado técnico:
  - `is_success` para códigos 2xx
  - `crawl_status` (`ok`, `timeout`, `ssl_error`, `connection_error`, `http_error`)
  - `error_message`

## 2.3 Reglas de hallazgos técnicos
- Construye findings mediante `build_finding(status_code, response_time_ms, page_group, is_priority, crawl_status)`.
- Cada finding se normaliza al contrato estándar:
  - `finding_code`, `finding_category`, `severity`, `finding_detail`, `recommendation`, etc.

## 2.4 Tablas impactadas
- `technical_crawl_run_log`
- `technical_crawl_results`
- `technical_crawl_findings`

---

## 3) Módulo SEO Validator (`seo-validator`)

## 3.1 Reglas de selección de URLs
Fuente: `sitemap_master_urls`.
- Filtro base: `m.should_audit = TRUE`.
- Filtro opcional por corrida sitemap: `m.run_id = source_run_id`.
- Si `only_status_200 = TRUE`:
  - hace join con `technical_crawl_results` por `normalized_url`.
  - exige `t.status_code = 200`.
  - opcionalmente filtra por `technical_run_id`.
- Límite opcional: `max_urls`.

## 3.2 Reglas SEO de extracción
Por cada página válida:
- Title y longitud:
  - `title`, `title_length`, `has_title`
- Meta descripción:
  - `meta_description`, `meta_description_length`, `has_meta_description`
- Encabezados:
  - `h1_count`, `has_h1`
- Canónico/robots/lang:
  - `canonical_url`, `has_canonical`, `robots_content`, `has_noindex`, `lang`, `has_lang`
- Metadatos sociales:
  - `has_og_title`, `has_og_description`, `has_twitter_card`
- Imágenes y schema:
  - `images_total`, `images_without_alt`, `has_schema`, `schema_types`
- Reglas de negocio específicas:
  - `has_terms_conditions_hint`, `has_service_keywords`

## 3.3 Reglas de estado y error
- Si request/parsing OK → `seo_status = "ok"`.
- Si falla request/parsing → `seo_status = "error"`, `error_message` poblado y métricas fallback.

## 3.4 Reglas de hallazgos SEO
- Construye findings desde `build_seo_findings(result)`.
- Usa contrato estándar de hallazgos:
  - código, categoría, severidad, detalle, recomendación y contexto del componente.

## 3.5 Tablas impactadas
- `seo_validation_run_log`
- `seo_validation_results`
- `seo_validation_findings`

---

## 4) Módulo Tagging Validator (`tagging-validator`)

## 4.1 Reglas de selección de URLs
Fuente: `sitemap_master_urls` (+ opcional técnico).
- Filtro base: `m.should_audit = TRUE`.
- Filtro por `source_run_id` opcional.
- Si `only_status_200 = TRUE`, join con `technical_crawl_results` y `t.status_code = 200`.
- Filtro opcional por `technical_run_id`.
- Límite opcional: `max_urls`.

## 4.2 Reglas de detección de stack de medición
Sobre el HTML/script de la página:
- `has_gtm`
- `has_ga4`
- `has_datalayer`

## 4.3 Reglas de interacción y cobertura
- Cuenta elementos:
  - `cta_elements_count`
  - `form_elements_count`
  - `clickable_elements_count`
- Deriva:
  - `has_interactions` si existe al menos una señal interactiva.

## 4.4 Reglas de hints de eventos
Detecta señales de eventos clave:
- `has_cta_click_hint`
- `has_generate_lead_hint`
- `has_form_start_hint`
- `has_form_submit_hint`
- `has_contact_click_hint`
- `has_whatsapp_click_hint`
- `has_portabilidad_click_hint`
- `has_renovacion_click_hint`
- `has_cobertura_click_hint`

## 4.5 Reglas de calidad de implementación
- Valida parámetros esperados:
  - `cta_required_params`
  - `lead_required_params`
  - `form_required_params`
- Detecta duplicidades:
  - `duplicate_gtm_detected`
  - `duplicate_ga4_detected`
  - `duplicate_event_hint_detected`
  - `double_tagging_detected`

## 4.6 Reglas de estado y error
- OK → `tagging_status = "ok"`.
- Error request/parsing → `tagging_status = "error"` + `error_message`.

## 4.7 Reglas de hallazgos Tagging
- Construye findings con `build_tagging_findings(result)`.
- Estructura estándar de hallazgos reutilizada para reporting transversal.

## 4.8 Tablas impactadas
- `tagging_validation_run_log`
- `tagging_validation_results`
- `tagging_validation_findings`

---

## 5) API de visualización (`audit-frontend-api`) y reglas de consulta

Este módulo no genera auditorías; **mapea reglas de lectura** sobre BigQuery:
- `get_overview_latest`: último run de cada módulo (subconsultas por run log).
- `get_module_latest`: último run por módulo (`sitemap`, `technical`, `seo`, `tagging`).
- `get_module_runs`: histórico limitado por módulo.
- `get_url_detail`: vista unificada por `normalized_url` combinando
  `sitemap_master_urls`, `technical_crawl_results`, `seo_validation_results`, `tagging_validation_results`.

---

## 6) Mapa rápido de reglas por tipo

- **Reglas de entrada/fuente**: módulos 1 a 4 seleccionan URLs desde `sitemap_master_urls`.
- **Reglas de elegibilidad**: `should_audit`, `is_priority`, `only_status_200`, `max_urls`.
- **Reglas de calidad técnica**: HTTP status, latency, errores de conexión, redirecciones.
- **Reglas SEO**: title/meta/H1/canonical/robots/lang/OG/schema/alt.
- **Reglas tagging**: GTM/GA4/datalayer/event hints/parámetros/duplicados.
- **Reglas de trazabilidad**: `run_id`, `source_run_id`, `technical_run_id`, `seo_run_id`, `normalized_url`, `url_hash`.