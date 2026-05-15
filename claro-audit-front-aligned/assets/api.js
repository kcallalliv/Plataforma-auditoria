const API_BASE = window.AUDIT_CONFIG?.API_BASE || "";

async function apiGet(endpoint, fallbackData = null) {
  const url = `${API_BASE}${endpoint}`;
  try {
    const response = await fetch(url, {
      method: "GET",
      mode: "cors",
      headers: { Accept: "application/json" }
    });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const contentType = response.headers.get("content-type") || "";
    if (!contentType.toLowerCase().includes("application/json")) {
      const preview = (await response.text()).slice(0, 120).replace(/\s+/g, " ").trim();
      throw new Error(`Respuesta no JSON desde ${endpoint}. Content-Type: ${contentType || "desconocido"}. Preview: ${preview}`);
    }
    return await response.json();
  } catch (error) {
    console.error("API ERROR:", endpoint, error?.message || error);
    globalThis.showToast?.(`No se pudo cargar ${endpoint}`);
    return fallbackData;
  }
}
