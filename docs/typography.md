# Arquitectura propuesta: auditoría de tipografía dentro de imágenes (futuro)

## Por qué no se resuelve con HTML/CSS
Las fuentes embebidas en una imagen rasterizada no existen como nodos DOM ni estilos CSS computables; por lo tanto no se pueden validar con parser HTML ni con `getComputedStyle`.

## Opciones tecnológicas
- Google Vision AI
- Gemini Vision
- Vertex AI Vision
- OCR tradicional (Tesseract u otro)

## Flujo propuesto
1. Extraer URLs de imágenes del HTML (`img`, `picture`, `srcset`, CSS backgrounds).
2. Descargar imágenes y normalizar formato/tamaño.
3. Aplicar OCR/Vision para detectar texto.
4. Generar features visuales del texto detectado (contorno, kerning aproximado, grosor, altura x).
5. Comparar con heurísticas visuales de guía de marca (Roboto/AMX y variantes aprobadas).
6. Registrar hallazgos en `content_validation_findings` con evidencia y score de confianza.

## Limitaciones
- OCR no identifica fuente exacta con 100% de precisión.
- Requiere heurísticas o modelo visual entrenado para clasificación tipográfica.
- Costo por imagen procesada.
- Riesgo de falsos positivos/negativos.

## Estimación referencial de costo (escenarios)
> Rango referencial, depende del proveedor/API/tier y resolución de imagen.

- 100 imágenes: bajo (piloto).
- 1,000 imágenes: medio (operación mensual pequeña).
- 10,000 imágenes: alto (requiere optimización de muestreo, caché y priorización).

## Recomendación técnica
Mantener esta capacidad como **submódulo futuro de M5 Content / UI Compliance**, inicialmente en modo investigación/arquitectura y fuera de producción.