import re
from bs4 import BeautifulSoup

GTM_PATTERNS = [
    "googletagmanager.com/gtm.js",
    "GTM-",
]

GA4_PATTERNS = [
    "googletagmanager.com/gtag/js",
    "gtag(",
    "G-",
]

DATALAYER_PATTERNS = [
    "dataLayer",
    "window.dataLayer",
    "dataLayer.push",
]

EVENT_PATTERNS = {
    "cta_click": ["cta_click", "cta click", "click_cta"],
    "generate_lead": ["generate_lead", "lead_submit", "lead_generated"],
    "form_start": ["form_start", "formstart"],
    "form_submit": ["form_submit", "formsubmit", "submit_form"],
    "contact_click": ["contact_click", "contactclick"],
    "whatsapp_click": ["whatsapp_click", "whatsappclick"],
    "portabilidad_click": ["portabilidad_click", "portabilidadclick"],
    "renovacion_click": ["renovacion_click", "renovación_click", "renovacionclick"],
    "cobertura_click": ["cobertura_click", "coberturaclick"],
}

def get_script_text(soup: BeautifulSoup) -> str:
    scripts = soup.find_all("script")
    content = []
    for script in scripts:
        txt = script.string or script.text or ""
        if txt:
            content.append(txt)
    return "\n".join(content)

def contains_any(text: str, patterns: list[str]) -> bool:
    text_low = text.lower()
    return any(p.lower() in text_low for p in patterns)

def detect_gtm(text: str) -> bool:
    return contains_any(text, GTM_PATTERNS)

def detect_ga4(text: str) -> bool:
    return contains_any(text, GA4_PATTERNS)

def detect_datalayer(text: str) -> bool:
    return contains_any(text, DATALAYER_PATTERNS)

def detect_event_hint(text: str, event_name: str) -> bool:
    return contains_any(text, EVENT_PATTERNS[event_name])

def count_cta_elements(soup: BeautifulSoup) -> int:
    selectors = soup.find_all(["button", "a", "input"])
    count = 0
    for el in selectors:
        text = " ".join([
            el.get_text(" ", strip=True) if hasattr(el, "get_text") else "",
            el.get("aria-label", "") or "",
            el.get("value", "") or "",
            el.get("href", "") or "",
        ]).lower()
        if any(k in text for k in ["solicita", "quiero", "ver planes", "me interesa", "contrata", "llámanos", "whatsapp", "portabilidad", "renovación", "renovacion"]):
            count += 1
    return count

def count_form_elements(soup: BeautifulSoup) -> int:
    return len(soup.find_all("form"))

def count_clickable_elements(soup: BeautifulSoup) -> int:
    return len(soup.find_all(["button", "a"]))

def has_required_params(text: str, rule_type: str) -> bool:
    text_low = text.lower()
    if rule_type == "cta":
        return any(p in text_low for p in ["event", "category", "label", "cta"])
    if rule_type == "lead":
        return any(p in text_low for p in ["lead", "form", "service", "plan"])
    if rule_type == "form":
        return any(p in text_low for p in ["form", "step", "submit"])
    return False

def detect_double_tagging(text: str) -> tuple[bool, bool, bool, bool]:
    gtm_count = len(re.findall(r"GTM-[A-Z0-9]+", text))
    ga4_count = len(re.findall(r"G-[A-Z0-9]+", text))
    dl_push_count = text.lower().count("datalayer.push")
    event_repeat = any(text.lower().count(k) > 1 for k in ["generate_lead", "form_submit", "cta_click"])

    duplicate_gtm = gtm_count > 1
    duplicate_ga4 = ga4_count > 1
    duplicate_event = event_repeat or dl_push_count > 10
    double_tagging = duplicate_gtm or duplicate_ga4 or duplicate_event

    return duplicate_gtm, duplicate_ga4, duplicate_event, double_tagging

def build_tagging_findings(result: dict):
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

    if not result["has_gtm"]:
        findings.append(finding(
            "TAG_GTM_MISSING",
            "tagging",
            "alta",
            "No se detectó GTM",
            "Validar implementación de Google Tag Manager.",
            "script",
            "head/body",
            "GTM no detectado",
            "Script de GTM implementado",
            None,
            'script[src*="googletagmanager.com/gtm.js"]',
        ))

    if not result["has_ga4"]:
        findings.append(finding(
            "TAG_GA4_MISSING",
            "tagging",
            "alta",
            "No se detectó GA4",
            "Validar implementación de GA4.",
            "script",
            "head/body",
            "GA4 no detectado",
            "Script de GA4 implementado",
            None,
            'script[src*="googletagmanager.com/gtag/js"]',
        ))

    if result["has_interactions"] and not result["has_datalayer"]:
        findings.append(finding(
            "TAG_DATALAYER_MISSING",
            "tagging",
            "alta",
            "La página tiene interacciones pero no se detectó dataLayer",
            "Agregar dataLayer para registrar eventos de interacción.",
            "script",
            "head/body",
            "dataLayer no detectado",
            "window.dataLayer o dataLayer.push",
            None,
            "script:contains('dataLayer')",
        ))

    if result["double_tagging_detected"]:
        findings.append(finding(
            "TAG_DOUBLE_TAGGING",
            "tagging",
            "alta",
            "Se detectó posible doble etiquetado",
            "Revisar duplicidad de GTM, GA4 o eventos enviados múltiples veces.",
            "script",
            "head/body",
            "Duplicidad detectada",
            "Una sola implementación controlada de GTM/GA4/eventos",
            None,
            "script",
        ))

    if result["has_interactions"] and not (
        result["has_cta_click_hint"]
        or result["has_generate_lead_hint"]
        or result["has_form_start_hint"]
        or result["has_form_submit_hint"]
        or result["has_contact_click_hint"]
        or result["has_whatsapp_click_hint"]
        or result["has_portabilidad_click_hint"]
        or result["has_renovacion_click_hint"]
        or result["has_cobertura_click_hint"]
    ):
        findings.append(finding(
            "TAG_INTERACTION_NOT_TAGGED",
            "tagging",
            "media",
            "La página tiene interacciones pero no se detectaron hints de etiquetado",
            "Validar eventos sobre CTAs, formularios, WhatsApp o botones principales.",
            "cta/form/button/a",
            "body",
            f"CTA: {result['cta_elements_count']} | Forms: {result['form_elements_count']} | Clickables: {result['clickable_elements_count']}",
            "Eventos de interacción implementados",
            None,
            "button, a, form, input",
        ))

    if result["has_cta_click_hint"] and not result["cta_required_params"]:
        findings.append(finding(
            "TAG_CTA_PARAMS_MISSING",
            "tagging",
            "media",
            "Se detectó hint de CTA pero faltan parámetros mínimos",
            "Completar parámetros del evento CTA.",
            "event",
            "script",
            "Evento CTA sin parámetros mínimos",
            "event, category, label, cta",
            None,
            "dataLayer.push / gtag event",
        ))

    if result["has_generate_lead_hint"] and not result["lead_required_params"]:
        findings.append(finding(
            "TAG_LEAD_PARAMS_MISSING",
            "tagging",
            "media",
            "Se detectó hint de lead pero faltan parámetros mínimos",
            "Completar parámetros del evento de lead.",
            "event",
            "script",
            "Lead sin parámetros mínimos",
            "lead, form, service, plan",
            None,
            "dataLayer.push / gtag event",
        ))

    if result["has_form_submit_hint"] and not result["form_required_params"]:
        findings.append(finding(
            "TAG_FORM_PARAMS_MISSING",
            "tagging",
            "media",
            "Se detectó form_submit pero faltan parámetros mínimos",
            "Completar parámetros del formulario.",
            "form",
            "body/script",
            "form_submit sin parámetros mínimos",
            "form, step, submit",
            None,
            "form / dataLayer.push",
        ))

    if not result["has_contact_click_hint"] and result["cta_elements_count"] > 0:
        findings.append(finding(
            "TAG_CONTACT_HINT_MISSING",
            "tagging",
            "baja",
            "No se detectó hint de contacto en una página con CTA",
            "Evaluar evento de contacto para CTAs principales.",
            "cta",
            "body",
            f"{result['cta_elements_count']} CTA(s) detectados",
            "Evento contact_click o equivalente",
            None,
            "button, a",
        ))

    return findings