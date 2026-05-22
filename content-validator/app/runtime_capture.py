from __future__ import annotations

from typing import Any


def run_typography_capture(url: str, device_profile: str, allowed_fonts: list[str]) -> dict[str, Any]:
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        return {"status": "not_available", "findings": []}

    viewport = {"width": 390, "height": 844} if device_profile == "mobile" else {"width": 1366, "height": 768}
    selectors = [
        "body",
        "h1, h2, h3, h4, h5, h6",
        "p, span, li",
        "button, input[type='button'], input[type='submit']",
        "a",
        "form",
        "nav",
        "footer",
    ]

    findings: list[dict[str, Any]] = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(viewport=viewport)
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(1000)

        for group_selector in selectors:
            handles = page.query_selector_all(group_selector)
            for node in handles[:50]:
                data = node.evaluate(
                    """
                    (el) => {
                      const s = window.getComputedStyle(el);
                      const html = el.outerHTML || '';
                      const text = (el.innerText || el.textContent || '').trim();
                      const toSelector = (e) => {
                        if (e.id) return `#${e.id}`;
                        const cls = (e.className || '').toString().trim().split(/\\s+/).filter(Boolean);
                        if (cls.length) return `${e.tagName.toLowerCase()}.` + cls.slice(0,2).join('.');
                        return e.tagName.toLowerCase();
                      };
                      return {
                        tag: el.tagName.toLowerCase(),
                        id: el.id || null,
                        className: (el.className || '').toString() || null,
                        text: text.slice(0, 300),
                        css_selector: toSelector(el),
                        xpath: null,
                        html_snippet: html.slice(0, 500),
                        computed_font_family: (s.fontFamily || '').toString(),
                        computed_font_size: (s.fontSize || '').toString(),
                        computed_font_weight: (s.fontWeight || '').toString(),
                      }
                    }
                    """
                )

                font_family = (data.get("computed_font_family") or "").lower()
                is_valid = any(font.lower() in font_family for font in allowed_fonts)
                if not is_valid:
                    tag = str(data.get("tag") or "")
                    if tag in {"button", "input"}:
                        finding_code = "BRAND_INVALID_FONT_BUTTON"
                    elif tag in {"a"}:
                        finding_code = "BRAND_INVALID_FONT_CTA"
                    elif tag in {"nav"}:
                        finding_code = "BRAND_INVALID_FONT_NAV"
                    elif tag in {"footer"}:
                        finding_code = "BRAND_INVALID_FONT_FOOTER"
                    else:
                        finding_code = "BRAND_INVALID_FONT_TEXT"
                    findings.append({
                        "finding_code": finding_code,
                        "rule_id": "CONT_FONT_ALLOWED",
                        "finding_type": "invalid_font",
                        "severity": "Alta",
                        "element_tag": data.get("tag"),
                        "element_id": data.get("id"),
                        "element_class": data.get("className"),
                        "element_text": data.get("text"),
                        "css_selector": data.get("css_selector"),
                        "xpath": data.get("xpath"),
                        "dom_section": data.get("tag"),
                        "html_snippet": data.get("html_snippet"),
                        "expected_value": " / ".join(allowed_fonts),
                        "actual_value": data.get("computed_font_family"),
                        "computed_font_family": data.get("computed_font_family"),
                        "computed_font_size": data.get("computed_font_size"),
                        "computed_font_weight": data.get("computed_font_weight"),
                        "resource_url": None,
                        "recommendation": "Aplicar fuente Roboto/AMX aprobada según guideline de marca.",
                    })

        context.close()
        browser.close()

    return {"status": "captured", "findings": findings}