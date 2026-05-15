from bs4 import BeautifulSoup
import json

def get_meta_content(soup: BeautifulSoup, name=None, property_name=None):
    if name:
        tag = soup.find("meta", attrs={"name": name})
        if tag:
            return tag.get("content")
    if property_name:
        tag = soup.find("meta", attrs={"property": property_name})
        if tag:
            return tag.get("content")
    return None

def get_canonical(soup: BeautifulSoup):
    tag = soup.find("link", attrs={"rel": "canonical"})
    return tag.get("href") if tag else None

def count_h1(soup: BeautifulSoup):
    return len(soup.find_all("h1"))

def get_h1_analysis(soup: BeautifulSoup):
    h1_tags = soup.find_all("h1")
    h1_texts = [h1.get_text(strip=True) for h1 in h1_tags if h1.get_text(strip=True)]

    duplicated = sorted(set([text for text in h1_texts if h1_texts.count(text) > 1]))

    return {
        "h1_count": len(h1_tags),
        "has_h1": len(h1_tags) > 0,
        "has_duplicated_h1": len(duplicated) > 0,
        "duplicated_h1_values": " | ".join(duplicated) if duplicated else None,
    }

def get_lang(soup: BeautifulSoup):
    html = soup.find("html")
    return html.get("lang") if html else None

def get_images_without_alt(soup: BeautifulSoup):
    imgs = soup.find_all("img")
    total = len(imgs)
    without_alt = sum(1 for img in imgs if not img.get("alt"))
    return total, without_alt

def detect_schema(soup: BeautifulSoup):
    schema_types = []
    scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
    for script in scripts:
        try:
            content = script.string or script.text
            data = json.loads(content)
            if isinstance(data, dict):
                t = data.get("@type")
                if t:
                    schema_types.append(str(t))
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and item.get("@type"):
                        schema_types.append(str(item["@type"]))
        except Exception:
            continue

    schema_types = list(dict.fromkeys(schema_types))
    return len(schema_types) > 0, ",".join(schema_types) if schema_types else None

def build_seo_findings(result: dict):
    findings = []

    def finding(
        code,
        category,
        severity,
        detail,
        recommendation,
        component_type,
        html_section,
        element_value=None,
        expected_value=None,
        component_id=None,
        component_selector=None,
    ):
        return {
            "finding_code": code,
            "finding_category": category,
            "severity": severity,
            "finding_detail": detail,
            "recommendation": recommendation,
            "component_type": component_type,
            "component_id": component_id,
            "component_selector": component_selector,
            "html_section": html_section,
            "element_value": element_value,
            "expected_value": expected_value,
        }

    title = result.get("title")
    title_length = result.get("title_length")

    if not result["has_title"]:
        findings.append(finding(
            "SEO_TITLE_MISSING",
            "seo",
            "alta",
            "La página no tiene title",
            "Agregar una etiqueta title descriptiva y optimizada.",
            "title",
            "head",
            None,
            "Title entre 30 y 60 caracteres",
            None,
            "head > title",
        ))
    elif title_length < 30:
        findings.append(finding(
            "SEO_TITLE_TOO_SHORT",
            "seo",
            "media",
            "El title es demasiado corto",
            "Ampliar el title para describir mejor el contenido de la página.",
            "title",
            "head",
            title,
            "Mínimo 30 caracteres",
            None,
            "head > title",
        ))
    elif title_length > 60:
        findings.append(finding(
            "SEO_TITLE_TOO_LONG",
            "seo",
            "media",
            "El title es demasiado largo",
            "Reducir el title para evitar truncamiento en buscadores.",
            "title",
            "head",
            title,
            "Máximo 60 caracteres",
            None,
            "head > title",
        ))

    meta_description = result.get("meta_description")
    meta_description_length = result.get("meta_description_length")

    if not result["has_meta_description"]:
        findings.append(finding(
            "SEO_META_MISSING",
            "seo",
            "alta",
            "La página no tiene meta description",
            "Agregar una meta description clara y orientada a conversión.",
            "meta_description",
            "head",
            None,
            "Meta description entre 70 y 160 caracteres",
            None,
            'head > meta[name="description"]',
        ))
    elif meta_description_length < 70:
        findings.append(finding(
            "SEO_META_TOO_SHORT",
            "seo",
            "media",
            "La meta description es demasiado corta",
            "Ampliar la meta description para describir mejor el contenido de la página.",
            "meta_description",
            "head",
            meta_description,
            "Mínimo 70 caracteres",
            None,
            'head > meta[name="description"]',
        ))
    elif meta_description_length > 160:
        findings.append(finding(
            "SEO_META_TOO_LONG",
            "seo",
            "media",
            "La meta description es demasiado larga",
            "Reducir la meta description para evitar truncamiento.",
            "meta_description",
            "head",
            meta_description,
            "Máximo 160 caracteres",
            None,
            'head > meta[name="description"]',
        ))

    if result["h1_count"] == 0:
        findings.append(finding(
            "SEO_H1_MISSING",
            "seo",
            "alta",
            "La página no tiene H1",
            "Agregar un único H1 descriptivo y alineado al contenido principal.",
            "h1",
            "body",
            None,
            "Un H1 único por página",
            None,
            "body h1",
        ))
    elif result["h1_count"] > 1:
        findings.append(finding(
            "SEO_H1_MULTIPLE",
            "seo",
            "media",
            "La página tiene más de un H1",
            "Mantener un solo H1 principal y convertir los demás encabezados en H2 o H3.",
            "h1",
            "body",
            str(result["h1_count"]),
            "1",
            None,
            "body h1",
        ))

    if result.get("has_duplicated_h1"):
        findings.append(finding(
            "SEO_H1_DUPLICATED",
            "seo",
            "media",
            "La página contiene H1 duplicado",
            "Usar un H1 único, descriptivo y no repetido dentro de la misma página.",
            "h1",
            "body",
            result.get("duplicated_h1_values"),
            "H1 único",
            None,
            "body h1",
        ))

    if not result["has_canonical"]:
        findings.append(finding(
            "SEO_CANONICAL_MISSING",
            "seo",
            "alta",
            "La página no tiene canonical",
            "Agregar canonical.",
            "canonical",
            "head",
            None,
            'link rel="canonical"',
            None,
            'head > link[rel="canonical"]',
        ))

    if result["has_noindex"] and result["page_group"] == "comercial":
        findings.append(finding(
            "SEO_NOINDEX_COMMERCIAL",
            "indexacion",
            "alta",
            "La página comercial tiene noindex",
            "Corregir meta robots.",
            "meta_robots",
            "head",
            result.get("robots_content"),
            "index,follow",
            None,
            'head > meta[name="robots"]',
        ))

    if not result["has_lang"]:
        findings.append(finding(
            "SEO_LANG_MISSING",
            "seo",
            "media",
            "La página no declara lang",
            "Agregar atributo lang.",
            "html",
            "html",
            None,
            'lang="es"',
            None,
            "html[lang]",
        ))

    if result["images_without_alt"] > 0:
        findings.append(finding(
            "SEO_ALT_MISSING",
            "seo",
            "media",
            f"La página tiene {result['images_without_alt']} imágenes sin alt",
            "Completar atributo alt.",
            "img",
            "body",
            str(result["images_without_alt"]),
            "Todas las imágenes relevantes con atributo alt",
            None,
            "body img:not([alt])",
        ))

    if not result["has_og_title"] or not result["has_og_description"]:
        findings.append(finding(
            "SEO_OG_MISSING",
            "social",
            "media",
            "Faltan etiquetas Open Graph básicas",
            "Agregar og:title y og:description.",
            "open_graph",
            "head",
            None,
            "og:title y og:description",
            None,
            'head > meta[property^="og:"]',
        ))

    if not result["has_twitter_card"]:
        findings.append(finding(
            "SEO_TWITTER_MISSING",
            "social",
            "baja",
            "Falta twitter card",
            "Agregar twitter:card.",
            "twitter_card",
            "head",
            None,
            'meta name="twitter:card"',
            None,
            'head > meta[name="twitter:card"]',
        ))

    if result["page_group"] == "comercial" and not result.get("has_terms_conditions_hint", False):
        findings.append(finding(
            "SEO_TYC_HINT_MISSING",
            "contenido",
            "media",
            "No se detectó hint de términos y condiciones",
            "Validar presencia de TyC o referencia legal.",
            "content_text",
            "body",
            None,
            "Texto o enlace a términos y condiciones",
            None,
            "body",
        ))

    if result["page_group"] == "comercial" and not result.get("has_service_keywords", False):
        findings.append(finding(
            "SEO_SERVICE_KEYWORDS_MISSING",
            "contenido",
            "baja",
            "No se detectaron keywords principales del servicio",
            "Revisar consistencia del contenido.",
            "content_text",
            "body",
            None,
            "Keyword principal del servicio",
            None,
            "body",
        ))

    if not result["has_schema"]:
        findings.append(finding(
            "SEO_SCHEMA_MISSING",
            "seo",
            "baja",
            "No se detectó schema",
            "Evaluar incorporación de datos estructurados.",
            "schema",
            "head/body",
            None,
            'script type="application/ld+json"',
            None,
            'script[type="application/ld+json"]',
        ))

    return findings

def detect_terms_conditions_hint(soup: BeautifulSoup) -> bool:
    text = soup.get_text(" ", strip=True).lower()
    return "términos y condiciones" in text or "terminos y condiciones" in text

def detect_service_keywords(soup: BeautifulSoup) -> bool:
    text = soup.get_text(" ", strip=True).lower()
    keywords = [
        "postpago",
        "prepago",
        "portabilidad",
        "renovación",
        "renovacion",
        "internet",
        "cobertura",
    ]
    return any(k in text for k in keywords)