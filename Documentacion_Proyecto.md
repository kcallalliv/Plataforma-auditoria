# Documentación integral del proyecto Plataforma-auditoria

## 1) Resumen ejecutivo
Plataforma de auditoría web compuesta por **5 servicios** desacoplados:
1. `sitemap-reader`: descubre y normaliza URLs desde sitemap(s).
2. `technical_crawler`: valida estado técnico HTTP y tiempos de respuesta.
3. `seo-validator`: evalúa metadatos y señales SEO on-page.
4. `tagging-validator`: valida implementación de tagging/medición.
5. `audit-frontend-api` + `claro-audit-front-aligned`: API de consulta + frontend para visualizar resultados.

Todos los módulos persisten y consultan información en BigQuery bajo un dataset común configurable por variables de entorno.

---

## 2) Arquitectura y responsabilidades

### 2.1 Frontend (`claro-audit-front-aligned`)
- SPA ligera en HTML/CSS/JS.
- Consume la API `audit-frontend-api`.
- Presenta navegación por módulos: Resumen, Sitemap, Técnico, SEO, Tagging.

### 2.2 API de visualización (`audit-frontend-api`)
- Expone endpoints de consulta para:
  - último estado general,
  - ejecuciones recientes por módulo,
  - detalle por URL.
- No ejecuta crawls; solo lee de BigQuery.

### 2.3 Motor de ingesta de URLs (`sitemap-reader`)
- Descarga XML de sitemap.
- Extrae URLs y metadatos (`lastmod`, `changefreq`, `priority`).
- Normaliza URL/path, calcula hash, clasifica página, filtra dominio/extensión/duplicados.
- Valida estado HTTP de cada URL detectada.
- Inserta en tablas:
  - `sitemap_run_log`
  - `sitemap_raw_entries`
  - `sitemap_master_urls`

### 2.4 Motor técnico (`technical_crawler`)
- Selecciona URLs de `sitemap_master_urls` con `should_audit=TRUE`.
- Ejecuta requests HTTP, sigue redirecciones.
- Calcula métricas técnicas (status, latency, headers, content-length, etc.).
- Genera findings técnicos.
- Inserta en:
  - `technical_crawl_run_log`
  - `technical_crawl_results`
  - `technical_crawl_findings`

### 2.5 Motor SEO (`seo-validator`)
- Selecciona URLs auditables (opcionalmente solo status 200 uniendo con módulo técnico).
- Parsea HTML y calcula indicadores SEO (title, meta description, H1, canonical, OG, schema, etc.).
- Genera findings SEO.
- Inserta en:
  - `seo_validation_run_log`
  - `seo_validation_results`
  - `seo_validation_findings`

### 2.6 Motor de Tagging (`tagging-validator`)
- Selecciona URLs auditables (igual criterio del módulo SEO).
- Inspecciona scripts y DOM para señales de GTM, GA4, datalayer, hints de eventos y parámetros requeridos.
- Calcula cobertura de interacción (CTA, forms, clickables).
- Genera findings de tagging.
- Inserta en:
  - `tagging_validation_run_log`
  - `tagging_validation_results`
  - `tagging_validation_findings`

---

## 3) Flujo end-to-end recomendado

1. **Ejecución sitemap-reader**
   - Entrada: lista de root sitemaps + reglas de dominio/extensiones.
   - Salida: universo de URLs normalizadas priorizadas y auditables.

2. **Ejecución technical_crawler**
   - Entrada: run_id de sitemap (opcional), filtros de prioridad/cantidad.
   - Salida: salud HTTP/técnica por URL + findings técnicos.

3. **Ejecución seo-validator**
   - Entrada: run_id sitemap + (opcional) run_id técnico y filtro `only_status_200`.
   - Salida: validación SEO por URL + findings SEO.

4. **Ejecución tagging-validator**
   - Entrada: run_id sitemap + (opcional) run_id técnico/seo.
   - Salida: validación de medición/tagging por URL + findings tagging.

5. **Consulta por frontend/API**
   - Overview consolidado del último run de cada módulo.
   - Histórico de corridas por módulo.
   - Drill-down por URL con datos de los 4 módulos.

---

## 4) Modelo de datos (tablas y diccionario)

> Nota: los tipos abajo son inferidos desde los payloads insertados (Python dict) y consultas SQL.

## 4.1 Tabla `sitemap_run_log`
| Campo | Tipo | Descripción |
|---|---|---|
| run_id | STRING | Identificador único de corrida sitemap (`sr_...`). |
| run_ts | TIMESTAMP | Fecha/hora de ejecución. |
| audit_date | DATE | Fecha lógica de auditoría. |
| source_root_sitemap | STRING | Sitemap raíz usado como fuente. |
| run_type | STRING | Tipo de ejecución (manual/otro). |
| execution_status | STRING | Estado final (success/partial_success/failed). |
| total_sitemaps_found | INT64 | Cantidad de sitemaps objetivo. |
| total_sitemaps_read_ok | INT64 | Sitemaps leídos correctamente. |
| total_sitemaps_failed | INT64 | Sitemaps con error. |
| total_urls_found | INT64 | URLs totales detectadas. |
| total_urls_unique | INT64 | URLs únicas. |
| total_urls_excluded | INT64 | URLs excluidas por reglas. |
| total_urls_ready_for_audit | INT64 | URLs listas para auditoría. |
| duration_seconds | FLOAT64 | Duración de corrida. |
| error_summary | STRING | Resumen de errores. |

## 4.2 Tabla `sitemap_raw_entries`
| Campo | Tipo | Descripción |
|---|---|---|
| run_id | STRING | Corrida asociada. |
| discovered_ts | TIMESTAMP | Momento de descubrimiento del entry. |
| source_sitemap | STRING | Sitemap fuente. |
| parent_sitemap | STRING | Sitemap padre (si aplica). |
| entry_type | STRING | Tipo de entrada (`url`, `urlset`, etc.). |
| loc | STRING | URL cruda encontrada en XML. |
| lastmod_raw | STRING | `lastmod` en bruto desde XML. |
| changefreq_raw | STRING | `changefreq` en bruto desde XML. |
| priority_raw | STRING | `priority` en bruto desde XML. |
| http_status | INT64 | Status HTTP del sitemap leído. |
| read_status | STRING | Estado de lectura/parseo. |
| error_message | STRING | Error puntual del entry. |

## 4.3 Tabla `sitemap_master_urls`
| Campo | Tipo | Descripción |
|---|---|---|
| run_id | STRING | Corrida fuente sitemap. |
| audit_date | DATE | Fecha de auditoría. |
| created_ts | TIMESTAMP | Timestamp de inserción. |
| page_url | STRING | URL original de la página. |
| normalized_url | STRING | URL normalizada para joins. |
| url_hash | STRING | Hash estable de URL. |
| domain | STRING | Dominio de la URL. |
| path | STRING | Path original. |
| query_string | STRING | Query string (si existe). |
| source_sitemap | STRING | Sitemap que reportó la URL. |
| lastmod_ts | TIMESTAMP | `lastmod` parseado. |
| changefreq | STRING | Frecuencia declarada. |
| priority_value | FLOAT64 | Prioridad declarada en sitemap. |
| url_type | STRING | Tipo de URL clasificado por reglas. |
| page_group | STRING | Grupo funcional de página. |
| is_duplicate | BOOL | Marca de duplicado en la corrida. |
| is_excluded | BOOL | Marca de exclusión. |
| exclusion_reason | STRING | Motivo de exclusión. |
| should_audit | BOOL | Indica si pasa a módulos de validación. |
| priority_group | STRING | Grupo de prioridad de negocio. |
| is_priority | BOOL | Indica si pertenece a paths prioritarios MVP. |
| priority_source | STRING | Fuente de priorización. |
| normalized_path | STRING | Path normalizado para reglas. |
| http_status | INT64 | Status al validar URL del sitemap. |
| redirect_type | STRING | Tipo de redirección detectada (301/302). |
| final_url | STRING | URL final en caso de redirect. |
| is_valid_status | BOOL | Cumple estado esperado (200). |
| sitemap_issue | STRING | Descripción de hallazgo de sitemap. |

## 4.4 Tabla `technical_crawl_run_log`
| Campo | Tipo | Descripción |
|---|---|---|
| run_id | STRING | ID de corrida técnica (`tc_...`). |
| source_run_id | STRING | ID de corrida sitemap origen. |
| run_ts | TIMESTAMP | Timestamp de ejecución. |
| audit_date | DATE | Fecha de auditoría. |
| execution_status | STRING | Estado de la corrida. |
| device_priority | STRING | Contexto dispositivo (ej. mobile). |
| only_priority | BOOL | Si auditó solo URLs prioritarias. |
| total_urls_target | INT64 | URLs objetivo. |
| total_urls_processed | INT64 | URLs procesadas. |
| total_urls_ok | INT64 | URLs exitosas. |
| total_urls_error | INT64 | URLs con error. |
| duration_seconds | FLOAT64 | Duración total. |
| error_summary | STRING | Resumen de errores. |

## 4.5 Tabla `technical_crawl_results`
| Campo | Tipo | Descripción |
|---|---|---|
| run_id | STRING | Corrida técnica. |
| source_run_id | STRING | Corrida sitemap fuente. |
| audit_date | DATE | Fecha de auditoría. |
| checked_ts | TIMESTAMP | Momento de chequeo. |
| page_url | STRING | URL solicitada. |
| normalized_url | STRING | URL normalizada. |
| url_hash | STRING | Hash de URL. |
| url_type | STRING | Tipo de URL. |
| page_group | STRING | Grupo de página. |
| is_priority | BOOL | Indicador prioridad. |
| device_priority | STRING | Contexto dispositivo. |
| request_user_agent | STRING | User-agent usado en request. |
| final_url | STRING | URL final resuelta. |
| final_domain | STRING | Dominio final resuelto. |
| status_code | INT64 | HTTP status final. |
| is_success | BOOL | Éxito HTTP (2xx). |
| response_time_ms | FLOAT64 | Tiempo de respuesta en ms. |
| redirect_count | INT64 | Cantidad de redirecciones. |
| content_type | STRING | Header `Content-Type`. |
| content_length | INT64 | Header `Content-Length` parseado. |
| server_header | STRING | Header `Server`. |
| cache_control | STRING | Header `Cache-Control`. |
| crawl_status | STRING | Estado técnico (ok/timeout/ssl_error/etc.). |
| error_message | STRING | Error técnico detallado. |
| mobile_context | STRING | Contexto del enfoque mobile-first. |

## 4.6 Tabla `technical_crawl_findings`
| Campo | Tipo | Descripción |
|---|---|---|
| run_id | STRING | Corrida técnica. |
| audit_date | DATE | Fecha de auditoría. |
| created_ts | TIMESTAMP | Momento de creación del hallazgo. |
| page_url | STRING | URL auditada. |
| normalized_url | STRING | URL normalizada. |
| finding_code | STRING | Código de hallazgo. |
| finding_category | STRING | Categoría del hallazgo. |
| severity | STRING | Severidad (low/medium/high). |
| finding_detail | STRING | Descripción del problema. |
| recommendation | STRING | Recomendación de remediación. |
| component_type | STRING | Tipo de componente afectado. |
| component_id | STRING | Identificador de componente. |
| component_selector | STRING | Selector relevante. |
| html_section | STRING | Sección HTML asociada. |
| element_value | STRING | Valor observado. |
| expected_value | STRING | Valor esperado. |

## 4.7 Tabla `seo_validation_run_log`
| Campo | Tipo | Descripción |
|---|---|---|
| run_id | STRING | ID de corrida SEO (`seo_...`). |
| source_run_id | STRING | Referencia al run de sitemap. |
| technical_run_id | STRING | Referencia al run técnico usado como filtro/contexto. |
| run_ts | TIMESTAMP | Timestamp de ejecución SEO. |
| audit_date | DATE | Fecha lógica de auditoría. |
| execution_status | STRING | Estado final de ejecución (success/partial_success/failed). |
| total_urls_target | INT64 | URLs objetivo para validar. |
| total_urls_processed | INT64 | URLs procesadas por el módulo. |
| total_urls_ok | INT64 | URLs evaluadas sin error de extracción. |
| total_urls_error | INT64 | URLs con error técnico o parsing. |
| duration_seconds | FLOAT64 | Duración total del proceso SEO. |
| error_summary | STRING | Resumen acotado de errores detectados. |

## 4.8 Tabla `seo_validation_results`
| Campo | Tipo | Descripción |
|---|---|---|
| run_id | STRING | Corrida SEO. |
| source_run_id | STRING | Corrida sitemap asociada. |
| technical_run_id | STRING | Corrida técnica asociada. |
| audit_date | DATE | Fecha de auditoría. |
| checked_ts | TIMESTAMP | Timestamp de validación por URL. |
| page_url | STRING | URL original consultada. |
| normalized_url | STRING | URL normalizada para joins entre módulos. |
| url_hash | STRING | Hash de URL para deduplicación y trazabilidad. |
| url_type | STRING | Tipo de URL (clasificación de negocio). |
| page_group | STRING | Grupo funcional de página. |
| title | STRING | Contenido de etiqueta `<title>`. |
| title_length | INT64 | Longitud de título. |
| has_title | BOOL | Indica presencia de `<title>`. |
| meta_description | STRING | Contenido de meta description. |
| meta_description_length | INT64 | Longitud de meta description. |
| has_meta_description | BOOL | Indica presencia de meta description. |
| h1_count | INT64 | Cantidad de etiquetas H1 detectadas. |
| has_h1 | BOOL | Indica si existe al menos un H1. |
| canonical_url | STRING | URL canónica declarada. |
| has_canonical | BOOL | Indica presencia de canonical. |
| robots_content | STRING | Valor de meta robots. |
| has_noindex | BOOL | Indica si robots contiene `noindex`. |
| lang | STRING | Idioma declarado en HTML. |
| has_lang | BOOL | Indica presencia del atributo de idioma. |
| has_og_title | BOOL | Indica presencia de `og:title`. |
| has_og_description | BOOL | Indica presencia de `og:description`. |
| has_twitter_card | BOOL | Indica presencia de `twitter:card`. |
| images_total | INT64 | Número total de imágenes detectadas. |
| images_without_alt | INT64 | Número de imágenes sin atributo ALT. |
| has_schema | BOOL | Indica presencia de marcado estructurado. |
| schema_types | STRING | Tipos de schema detectados (serializados). |
| seo_status | STRING | Estado de validación SEO por URL (`ok`/`error`). |
| error_message | STRING | Error de proceso cuando `seo_status=error`. |
| has_terms_conditions_hint | BOOL | Señal de términos y condiciones detectada. |
| has_service_keywords | BOOL | Señal de keywords de servicios detectada. |

## 4.9 Tabla `seo_validation_findings`
| Campo | Tipo | Descripción |
|---|---|---|
| run_id | STRING | Corrida SEO. |
| audit_date | DATE | Fecha de auditoría. |
| created_ts | TIMESTAMP | Momento de creación del hallazgo. |
| page_url | STRING | URL auditada. |
| normalized_url | STRING | URL normalizada. |
| finding_code | STRING | Código único de hallazgo SEO. |
| finding_category | STRING | Categoría del hallazgo SEO. |
| severity | STRING | Severidad del hallazgo. |
| finding_detail | STRING | Detalle técnico/funcional del problema. |
| recommendation | STRING | Recomendación de mejora. |
| component_type | STRING | Tipo de componente HTML/SEO asociado. |
| component_id | STRING | ID lógico del componente. |
| component_selector | STRING | Selector del elemento observado. |
| html_section | STRING | Sección del HTML analizada. |
| element_value | STRING | Valor real encontrado. |
| expected_value | STRING | Valor esperado según regla. |

## 4.10 Tabla `tagging_validation_run_log`
| Campo | Tipo | Descripción |
|---|---|---|
| run_id | STRING | ID de corrida tagging (`tag_...`). |
| source_run_id | STRING | Referencia al run de sitemap. |
| technical_run_id | STRING | Referencia al run técnico. |
| seo_run_id | STRING | Referencia al run SEO usado como trazabilidad. |
| run_ts | TIMESTAMP | Timestamp de ejecución. |
| audit_date | DATE | Fecha lógica de auditoría. |
| execution_status | STRING | Estado de ejecución (success/partial_success/failed). |
| device_priority | STRING | Contexto de dispositivo evaluado. |
| total_urls_target | INT64 | URLs objetivo para validar tagging. |
| total_urls_processed | INT64 | URLs procesadas por el módulo. |
| total_urls_ok | INT64 | URLs validadas sin error de extracción. |
| total_urls_error | INT64 | URLs con error de request/procesamiento. |
| duration_seconds | FLOAT64 | Duración total del proceso. |
| error_summary | STRING | Resumen de errores detectados. |

## 4.11 Tabla `tagging_validation_results`
| Campo | Tipo | Descripción |
|---|---|---|
| run_id | STRING | Corrida de tagging. |
| source_run_id | STRING | Corrida sitemap asociada. |
| technical_run_id | STRING | Corrida técnica asociada. |
| seo_run_id | STRING | Corrida SEO asociada. |
| audit_date | DATE | Fecha de auditoría. |
| checked_ts | TIMESTAMP | Timestamp de validación por URL. |
| page_url | STRING | URL original evaluada. |
| normalized_url | STRING | URL normalizada para joins. |
| url_hash | STRING | Hash de URL. |
| normalized_path | STRING | Path normalizado de la URL. |
| url_type | STRING | Tipo de URL. |
| page_group | STRING | Grupo funcional de página. |
| device_priority | STRING | Contexto de dispositivo priorizado. |
| has_gtm | BOOL | Indica presencia de Google Tag Manager. |
| has_ga4 | BOOL | Indica presencia de Google Analytics 4. |
| has_datalayer | BOOL | Indica presencia de dataLayer. |
| cta_elements_count | INT64 | Cantidad de CTAs detectados. |
| form_elements_count | INT64 | Cantidad de formularios detectados. |
| clickable_elements_count | INT64 | Cantidad de elementos clicables detectados. |
| has_interactions | BOOL | Indica si la página tiene elementos de interacción. |
| has_cta_click_hint | BOOL | Señal de evento `cta_click`. |
| has_generate_lead_hint | BOOL | Señal de evento `generate_lead`. |
| has_form_start_hint | BOOL | Señal de evento `form_start`. |
| has_form_submit_hint | BOOL | Señal de evento `form_submit`. |
| has_contact_click_hint | BOOL | Señal de evento `contact_click`. |
| has_whatsapp_click_hint | BOOL | Señal de evento `whatsapp_click`. |
| has_portabilidad_click_hint | BOOL | Señal de evento `portabilidad_click`. |
| has_renovacion_click_hint | BOOL | Señal de evento `renovacion_click`. |
| has_cobertura_click_hint | BOOL | Señal de evento `cobertura_click`. |
| cta_required_params | BOOL | Valida parámetros mínimos esperados en eventos CTA. |
| lead_required_params | BOOL | Valida parámetros mínimos esperados en eventos de lead. |
| form_required_params | BOOL | Valida parámetros mínimos esperados en eventos de formulario. |
| duplicate_gtm_detected | BOOL | Detecta carga duplicada de GTM. |
| duplicate_ga4_detected | BOOL | Detecta carga duplicada de GA4. |
| duplicate_event_hint_detected | BOOL | Detecta hints de eventos duplicados. |
| double_tagging_detected | BOOL | Detecta doble etiquetado entre herramientas/eventos. |
| tagging_status | STRING | Estado de validación tagging por URL (`ok`/`error`). |
| error_message | STRING | Error de procesamiento cuando aplica. |

## 4.12 Tabla `tagging_validation_findings`
| Campo | Tipo | Descripción |
|---|---|---|
| run_id | STRING | Corrida de tagging. |
| audit_date | DATE | Fecha de auditoría. |
| created_ts | TIMESTAMP | Momento de creación del hallazgo. |
| page_url | STRING | URL auditada. |
| normalized_url | STRING | URL normalizada. |
| finding_code | STRING | Código de hallazgo de tagging. |
| finding_category | STRING | Categoría del hallazgo. |
| severity | STRING | Severidad del hallazgo. |
| finding_detail | STRING | Detalle del problema detectado. |
| recommendation | STRING | Recomendación de implementación. |
| component_type | STRING | Tipo de componente afectado. |
| component_id | STRING | Identificador del componente. |
| component_selector | STRING | Selector del elemento asociado. |
| html_section | STRING | Sección del HTML relacionada. |
| element_value | STRING | Valor observado en la validación. |
| expected_value | STRING | Valor esperado por la regla de tagging. |

---

## 5) Relación entre tablas (llaves lógicas)

- Llave de corrida por módulo: `run_id`.
- Llaves de trazabilidad entre módulos:
  - `source_run_id` (referencia al run de sitemap).
  - `technical_run_id` (referencia al run técnico).
  - `seo_run_id` (referencia al run SEO, en tagging).
- Llave de entidad URL transversal: `normalized_url` (y/o `url_hash`).

Con esto se habilita:
- análisis histórico por corrida,
- análisis por URL entre módulos,
- construcción de dashboard consolidado.

---

## 6) Flujo de API de consulta (audit-frontend-api)

- **Navegación:** devuelve módulos habilitados del dashboard.
- **Overview latest:** último run de cada módulo (subconsultas sobre tablas de log).
- **Runs por módulo:** histórico paginado de corridas.
- **Detalle URL:** join lógico por `normalized_url` entre:
  - `sitemap_master_urls`
  - `technical_crawl_results`
  - `seo_validation_results`
  - `tagging_validation_results`

---

## 7) Recomendaciones operativas

1. **Orquestación**: ejecutar módulos en cascada (Sitemap → Técnico → SEO → Tagging).
2. **Versionado de esquema**: documentar cambios en columnas por módulo para evitar roturas de dashboard.
3. **Particionado/cluster en BigQuery**:
   - particionar por `audit_date` o `DATE(checked_ts/run_ts)` según tabla,
   - cluster por `run_id`, `normalized_url`, `url_hash` para bajar costos.
4. **Calidad de datos**:
   - validar nulabilidad de columnas críticas (`normalized_url`, `run_id`),
   - monitorear `error_summary` y `*_status`.
5. **KPIs mínimos recomendados**:
   - Técnico: tasa 2xx, p95 response time, errores por tipo.
   - SEO: % sin H1, % title fuera de rango, % sin meta description.
   - Tagging: % con GTM+GA4, % con eventos críticos, % doble etiquetado.

---

## 8) Inventario de componentes del repositorio

- `claro-audit-front-aligned/`: frontend estático.
- `audit-frontend-api/`: API de lectura para dashboard.
- `sitemap-reader/`: módulo de descubrimiento y normalización de URLs.
- `technical_crawler/`: validación técnica HTTP.
- `seo-validator/`: validación SEO on-page.
- `tagging-validator/`: validación tagging/analytics.