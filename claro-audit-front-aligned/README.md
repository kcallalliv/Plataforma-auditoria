# Claro Personas Audit - Aligned Frontend

Frontend HTML + JavaScript + CSS alineado a las plantillas de Stitch y conectado al audit-frontend-api.

## Deploy

```bash
gcloud builds submit . --tag us-central1-docker.pkg.dev/prd-claro-mktg-data-storage/seo-audit/claro-audit-front-js:v12
```

```bash
gcloud run deploy claro-audit-front-js \
  --image us-central1-docker.pkg.dev/prd-claro-mktg-data-storage/seo-audit/claro-audit-front-js:v12 \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated
```
