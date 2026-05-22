from __future__ import annotations

from typing import Any


def run_runtime_capture(url: str, device_profile: str = "mobile", timeout_seconds: int = 20) -> dict[str, Any]:
    """
    Captura técnica runtime opcional con Playwright.
    Si Playwright no está disponible en runtime, devuelve estado `not_available`
    para mantener compatibilidad sin romper corridas existentes.
    """
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception:
        return {
            "runtime_status": "not_available",
            "has_console_errors": False,
            "console_error_count": 0,
            "console_warning_count": 0,
            "page_error_count": 0,
            "failed_resource_count": 0,
            "failed_js_count": 0,
            "failed_css_count": 0,
            "failed_font_count": 0,
            "failed_image_count": 0,
            "has_js_conflicts": False,
            "events": [],
        }

    events: list[dict[str, Any]] = []
    counts = {
        "console_error_count": 0,
        "console_warning_count": 0,
        "page_error_count": 0,
        "failed_resource_count": 0,
        "failed_js_count": 0,
        "failed_css_count": 0,
        "failed_font_count": 0,
        "failed_image_count": 0,
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        viewport = {"width": 390, "height": 844} if device_profile == "mobile" else {"width": 1366, "height": 768}
        context = browser.new_context(viewport=viewport)
        page = context.new_page()

        def on_console(msg):
            t = msg.type
            if t == "error":
                counts["console_error_count"] += 1
            elif t == "warning":
                counts["console_warning_count"] += 1
            events.append({"browser_event_type": "console", "console_message_type": t, "message": msg.text})

        def on_pageerror(exc):
            counts["page_error_count"] += 1
            events.append({"browser_event_type": "pageerror", "message": str(exc)})

        def on_requestfailed(req):
            counts["failed_resource_count"] += 1
            rtype = req.resource_type
            if rtype == "script":
                counts["failed_js_count"] += 1
            elif rtype == "stylesheet":
                counts["failed_css_count"] += 1
            elif rtype == "font":
                counts["failed_font_count"] += 1
            elif rtype == "image":
                counts["failed_image_count"] += 1
            events.append({"browser_event_type": "requestfailed", "resource_url": req.url, "resource_type": rtype})

        page.on("console", on_console)
        page.on("pageerror", on_pageerror)
        page.on("requestfailed", on_requestfailed)
        page.goto(url, wait_until="networkidle", timeout=timeout_seconds * 1000)
        browser.close()

    has_js_conflicts = any("undefined" in str(e.get("message", "")).lower() for e in events)
    return {
        "runtime_status": "captured",
        "has_console_errors": counts["console_error_count"] > 0,
        **counts,
        "has_js_conflicts": has_js_conflicts,
        "events": events,
    }
