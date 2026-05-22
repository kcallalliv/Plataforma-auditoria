# Revalidación del checklist de auditoría web Claro

- Total de reglas procesadas: **113**.
- Fuente de verdad: `checklist_reglas_auditoria_web_claro.csv`.
- Severidades normalizadas permitidas: **Alta / Media / Baja**.

## Conteo por estado original (CSV)
- Considerado: 36
- No considerado: 61
- Parcial: 16

## Conteo por estado revalidado
- Considerada: 26
- No considerada: 58
- Parcial: 29

## Reglas potencialmente mal clasificadas en CSV
| Regla ID | Regla | Estado CSV | Estado revalidado | Módulo correcto | Acción técnica |
|---|---|---|---|---|---|
| TECH_001 | Página con status inválido | Considerado | Considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| TECH_002 | Redirects | Considerado | Considerada | M3 Link Validator | Crear Link Validator y findings detallados por enlace/asset con selector/xpath. |
| TECH_003 | Soft 404 | No considerado | No considerada | M3 Link Validator | Crear Link Validator y findings detallados por enlace/asset con selector/xpath. |
| TECH_004 | Redirect chain controlada | Considerado | Considerada | M3 Link Validator | Crear Link Validator y findings detallados por enlace/asset con selector/xpath. |
| TECH_006 | Tiempo de respuesta base | Considerado | Considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| TECH_007 | Compresión habilitada | No considerado | No considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| TECH_008 | HTTPS obligatorio | No considerado | No considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| CONT_001 | Palabras prohibidas | No considerado | No considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| CONT_003 | Campañas vencidas | No considerado | No considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| CONT_004 | Menciones de competidores prohibidas | No considerado | No considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| CONT_007 | Contenido placeholder | No considerado | No considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| TAG_001 | GTM presente | Considerado | Considerada | M8 Tagging Validator | Ampliar validación de tagging con trazabilidad por elemento y verificación runtime de píxeles/eventos. |
| TAG_002 | GA4 presente | Considerado | Considerada | M8 Tagging Validator | Ampliar validación de tagging con trazabilidad por elemento y verificación runtime de píxeles/eventos. |
| LINK_001 | Links internos rotos | No considerado | No considerada | M3 Link Validator | Crear Link Validator y findings detallados por enlace/asset con selector/xpath. |
| LINK_002 | Enlaces externos rotos críticos | No considerado | No considerada | M3 Link Validator | Crear Link Validator y findings detallados por enlace/asset con selector/xpath. |
| LINK_003 | Imágenes rotas | No considerado | No considerada | M3 Link Validator | Crear Link Validator y findings detallados por enlace/asset con selector/xpath. |
| LINK_004 | PDFs o descargables rotos | No considerado | No considerada | M3 Link Validator | Crear Link Validator y findings detallados por enlace/asset con selector/xpath. |
| LINK_005 | Anchors internos inválidos | No considerado | No considerada | M3 Link Validator | Crear Link Validator y findings detallados por enlace/asset con selector/xpath. |
| PERF_001 | Performance bajo | No considerado | No considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| PERF_002 | Performance crítico | No considerado | No considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| PERF_003 | Caída de performance | No considerado | No considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| PERF_004 | Mejora de performance | No considerado | No considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| PERF_005 | LCP crítico | No considerado | No considerada | M6 Performance | Implementar validación con PageSpeed Insights API/Lighthouse y guardar métricas por estrategia mobile/desktop. |
| PERF_006 | LCP alto | No considerado | No considerada | M6 Performance | Implementar validación con PageSpeed Insights API/Lighthouse y guardar métricas por estrategia mobile/desktop. |
| PERF_007 | CLS crítico | No considerado | No considerada | M6 Performance | Implementar validación con PageSpeed Insights API/Lighthouse y guardar métricas por estrategia mobile/desktop. |
| PERF_008 | CLS alto | No considerado | No considerada | M6 Performance | Implementar validación con PageSpeed Insights API/Lighthouse y guardar métricas por estrategia mobile/desktop. |
| PERF_009 | INP alto | No considerado | No considerada | M6 Performance | Implementar validación con PageSpeed Insights API/Lighthouse y guardar métricas por estrategia mobile/desktop. |
| PERF_010 | LCP empeoró | No considerado | No considerada | M6 Performance | Implementar validación con PageSpeed Insights API/Lighthouse y guardar métricas por estrategia mobile/desktop. |
| PERF_011 | LCP mejoró | No considerado | No considerada | M6 Performance | Implementar validación con PageSpeed Insights API/Lighthouse y guardar métricas por estrategia mobile/desktop. |
| PERF_012 | CLS empeoró | No considerado | No considerada | M6 Performance | Implementar validación con PageSpeed Insights API/Lighthouse y guardar métricas por estrategia mobile/desktop. |
| PERF_013 | CLS mejoró | No considerado | No considerada | M6 Performance | Implementar validación con PageSpeed Insights API/Lighthouse y guardar métricas por estrategia mobile/desktop. |
| PERF_016 | Imágenes pesadas | No considerado | No considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| PERF_017 | Imágenes sin formato moderno | No considerado | No considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| PERF_018 | Imágenes sin lazy load | No considerado | No considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| PERF_019 | Imágenes pesadas sin optimizar | No considerado | No considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| PERF_020 | JS rotos | No considerado | Parcial | M3 Link Validator | Crear Link Validator y findings detallados por enlace/asset con selector/xpath. |
| PERF_021 | CSS rotos | No considerado | No considerada | M3 Link Validator | Crear Link Validator y findings detallados por enlace/asset con selector/xpath. |
| IDX_001 | Página con status no válido | Considerado | Considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| IDX_002 | Canonical presente | Considerado | Considerada | M4 SEO Validator | Ampliar reglas SEO y findings con trazabilidad universal del componente afectado. |
| IDX_004 | Página con noindex | Considerado | Considerada | M4 SEO Validator | Ampliar reglas SEO y findings con trazabilidad universal del componente afectado. |
| IDX_006 | Bloqueo en robots.txt | No considerado | No considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| IDX_007 | URL no en sitemap | No considerado | No considerada | M1 Sitemap Reader | Ampliar snapshots sitemap y detección de cambios (new/removed/modified/unchanged). |
| IDX_009 | Redirección incorrecta | Considerado | Considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| IDX_010 | Redirección temporal incorrecta | No considerado | No considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| IDX_011 | URLs con parámetros indexables | No considerado | No considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| IDX_012 | Página huérfana | No considerado | No considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| IDX_013 | Página no rastreable | No considerado | No considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| IDX_014 | Duplicidad por canonicalización | No considerado | No considerada | M4 SEO Validator | Ampliar reglas SEO y findings con trazabilidad universal del componente afectado. |
| ONP_001 | Title obligatorio | Considerado | Considerada | M4 SEO Validator | Ampliar reglas SEO y findings con trazabilidad universal del componente afectado. |
| ONP_002 | Extensión de Title | Considerado | Considerada | M4 SEO Validator | Ampliar reglas SEO y findings con trazabilidad universal del componente afectado. |
| ONP_004 | Meta description obligatoria | Considerado | Considerada | M4 SEO Validator | Ampliar reglas SEO y findings con trazabilidad universal del componente afectado. |
| ONP_005 | Extensión de meta description | Considerado | Considerada | M4 SEO Validator | Ampliar reglas SEO y findings con trazabilidad universal del componente afectado. |
| ONP_007 | Un solo H1 | Considerado | Considerada | M4 SEO Validator | Ampliar reglas SEO y findings con trazabilidad universal del componente afectado. |
| ONP_008 | H1 faltante | Considerado | Considerada | M4 SEO Validator | Ampliar reglas SEO y findings con trazabilidad universal del componente afectado. |
| ONP_009 | H1 duplicado | Considerado | Considerada | M4 SEO Validator | Ampliar reglas SEO y findings con trazabilidad universal del componente afectado. |
| ONP_010 | Jerarquía de headings | No considerado | No considerada | M3 Link Validator | Crear Link Validator y findings detallados por enlace/asset con selector/xpath. |
| ONP_011 | ALT en imágenes | Considerado | Considerada | M4 SEO Validator | Ampliar reglas SEO y findings con trazabilidad universal del componente afectado. |
| ONP_012 | Contenido thin | No considerado | No considerada | M3 Link Validator | Crear Link Validator y findings detallados por enlace/asset con selector/xpath. |
| ONP_013 | Contenido duplicado | No considerado | No considerada | M3 Link Validator | Crear Link Validator y findings detallados por enlace/asset con selector/xpath. |
| ONP_017 | Enlaces internos insuficientes | No considerado | No considerada | M3 Link Validator | Crear Link Validator y findings detallados por enlace/asset con selector/xpath. |
| TAG_003 | Doble etiquetado en elemento con interacción | Considerado | Considerada | M8 Tagging Validator | Ampliar validación de tagging con trazabilidad por elemento y verificación runtime de píxeles/eventos. |
| TAG_005 | dataLayer presente | Considerado | Considerada | M8 Tagging Validator | Ampliar validación de tagging con trazabilidad por elemento y verificación runtime de píxeles/eventos. |
| TAG_006 | Tracking en WhatsApp | Considerado | Considerada | M8 Tagging Validator | Ampliar validación de tagging con trazabilidad por elemento y verificación runtime de píxeles/eventos. |
| TAG_007 | Tracking de generación de lead | Considerado | Considerada | M8 Tagging Validator | Ampliar validación de tagging con trazabilidad por elemento y verificación runtime de píxeles/eventos. |
| TAG_008 | Parámetros GA4 mínimos | No considerado | No considerada | M8 Tagging Validator | Ampliar validación de tagging con trazabilidad por elemento y verificación runtime de píxeles/eventos. |
| TECH_009 | Errores en consola | Considerado | Considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| PERF_022 | CSS minificado | No considerado | No considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| PERF_023 | JS minificado | No considerado | Parcial | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| PERF_024 | Número de requests | No considerado | No considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| PERF_025 | Fuentes (Web Fonts) | No considerado | Parcial | M5 Content / UI Compliance | Implementar validador de contenido/UI con Playwright (computed styles y trazabilidad de elementos). |
| PERF_026 | Render-blocking resources | No considerado | No considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| PERF_027 | Browser Caching | No considerado | No considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| CONT_008 | Contenido E-E-A-T | No considerado | No considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| ACCE_001 | ARIA labels | No considerado | No considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| ACCE_002 | Semantic HTML | No considerado | No considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| SEG_001 | HTTPS + Security Headers | No considerado | No considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| SEG_002 | Mixed Content | No considerado | No considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| TECH_011 | SyntaxError | Considerado | Parcial | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| TECH_012 | ReferenceError | Considerado | Parcial | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| TECH_013 | TypeError | Considerado | Parcial | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| TECH_014 | RangeError | Considerado | Parcial | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| TECH_015 | URIError | Considerado | Parcial | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| TECH_016 | Unhandled Promise Rejection | Considerado | Considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| TECH_017 | Deprecated API | Considerado | Considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| TECH_018 | Conflicto de versiones JS | No considerado | No considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| TECH_019 | Namespace Collision JS | No considerado | No considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| TECH_020 | Dependency Conflict JS | No considerado | No considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| TECH_021 | JQuery undefined | Considerado | Parcial | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| PERF_028 | Fuente externa caída | Considerado | Considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| TAG_009 | Facebook Pixel roto | Parcial | No considerada | M8 Tagging Validator | Ampliar validación de tagging con trazabilidad por elemento y verificación runtime de píxeles/eventos. |
| TAG_010 | TikTok Pixel roto | No considerado | Parcial | M8 Tagging Validator | Ampliar validación de tagging con trazabilidad por elemento y verificación runtime de píxeles/eventos. |
| TECH_022 | Google Maps API error | No considerado | No considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| PERF_029 | YouTube embed roto | No considerado | No considerada | M2 Technical Crawler | Ampliar crawler técnico con device_profile dual y subcapacidad runtime opcional con Playwright. |
| TAG_011 | Facebook Pixel ausente | Considerado | Parcial | M8 Tagging Validator | Ampliar validación de tagging con trazabilidad por elemento y verificación runtime de píxeles/eventos. |
| TAG_012 | Facebook Pixel duplicado | Parcial | No considerada | M8 Tagging Validator | Ampliar validación de tagging con trazabilidad por elemento y verificación runtime de píxeles/eventos. |
| TAG_013 | Facebook Pixel mal configurado | Considerado | Parcial | M8 Tagging Validator | Ampliar validación de tagging con trazabilidad por elemento y verificación runtime de píxeles/eventos. |
| PERF_030 | Fuente "Roboto" | Considerado | Parcial | M5 Content / UI Compliance | Implementar validador de contenido/UI con Playwright (computed styles y trazabilidad de elementos). |
| PERF_031 | Fuente "AMX" | Considerado | Parcial | M5 Content / UI Compliance | Implementar validador de contenido/UI con Playwright (computed styles y trazabilidad de elementos). |
| PERF_033 | Fonts sin preload | No considerado | Parcial | M5 Content / UI Compliance | Implementar validador de contenido/UI con Playwright (computed styles y trazabilidad de elementos). |

## Reglas reclasificadas por requerir navegador real, PageSpeed u OCR

| rule_id | estado CSV | estado revalidado | motivo de reclasificación | módulo correcto | implementación requerida |
|---|---|---|---|---|---|
| TECH_009 | Considerado | Parcial/No considerado si no hay Playwright | Requiere ejecución JS real y captura de consola/runtime. | M2 Technical Crawler (runtime_scan) | `runtime_scan=true`, `device_profiles=[mobile,desktop]`, capturar `console`, `pageerror`, `requestfailed`, `response>=400`. |
| TECH_010 | Considerado | Parcial/No considerado si no hay Playwright | Errores runtime JS no visibles por crawler HTTP. | M2 Technical Crawler (runtime_scan) | Playwright + normalización de `finding_code` técnicos. |
| TECH_011 | Considerado | Parcial/No considerado si no hay Playwright | `SyntaxError/ReferenceError/TypeError` requieren navegador. | M2 Technical Crawler (runtime_scan) | Clasificación `TECH_SYNTAX_ERROR`, `TECH_REFERENCE_ERROR`, `TECH_TYPE_ERROR`. |
| TECH_012 | Considerado | Parcial/No considerado si no hay Playwright | `jQuery undefined` requiere runtime JS. | M2 Technical Crawler (runtime_scan) | `TECH_JQUERY_UNDEFINED`. |
| TECH_013 | Considerado | Parcial | Detectar librerías/recursos rotos requiere eventos runtime y red. | M2 Technical Crawler (runtime_scan) | `TECH_FAILED_JS_RESOURCE`, `TECH_FAILED_CSS_RESOURCE`, `TECH_FAILED_FONT_RESOURCE`, `TECH_FAILED_IMAGE_RESOURCE`. |
| TECH_014 | Considerado | Parcial | CORS/CSP/mixed content se detectan en navegador real. | M2 Technical Crawler (runtime_scan) | `TECH_CORS_ERROR`, `TECH_CSP_ERROR`, `TECH_MIXED_CONTENT`. |
| TECH_015 | Considerado | Parcial | Conflictos JS detectables por mensajes runtime. | M2 Technical Crawler (runtime_scan) | `TECH_JS_CONFLICT`. |
| TECH_016 | Considerado | Parcial | Advertencias/errores de consola requieren `page.on('console')`. | M2 Technical Crawler (runtime_scan) | `TECH_CONSOLE_ERROR`, `TECH_CONSOLE_WARNING`. |
| PERF_030 | Considerado | Reclasificada | Regla de identidad tipográfica (no performance). | M5 Content / UI Compliance | `finding_code=BRAND_INVALID_FONT_TEXT`, validación por `getComputedStyle`. |
| PERF_031 | Considerado | Reclasificada | Regla de identidad tipográfica en botones/CTA. | M5 Content / UI Compliance | `finding_code=BRAND_INVALID_FONT_BUTTON`, validación por `getComputedStyle`. |