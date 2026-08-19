const JSON_HEADERS = {
  "content-type": "application/json; charset=utf-8",
  "cache-control": "no-store",
};

export function json(payload, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { ...JSON_HEADERS, ...extraHeaders },
  });
}

export function config() {
  const url = (process.env.SUPABASE_URL || "").replace(/\/+$/, "");
  const key = (process.env.SUPABASE_SECRET_KEY || "").trim();
  if (!url || !key) {
    throw new Error("Configure SUPABASE_URL e SUPABASE_SECRET_KEY nas variáveis do Netlify.");
  }
  return { url, key };
}

export async function rpc(name, args = {}, timeoutMs = 48000) {
  const { url, key } = config();
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(`${url}/rest/v1/rpc/${encodeURIComponent(name)}`, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "accept": "application/json",
        "apikey": key,
        "authorization": `Bearer ${key}`,
      },
      body: JSON.stringify(args),
      signal: controller.signal,
      cache: "no-store",
    });
    const text = await response.text();
    let payload;
    try { payload = text ? JSON.parse(text) : null; } catch { payload = { error: text || `HTTP ${response.status}` }; }
    if (!response.ok) {
      const message = payload?.message || payload?.error || payload?.hint || `Supabase HTTP ${response.status}`;
      const err = new Error(message);
      err.status = response.status;
      err.payload = payload;
      throw err;
    }
    return payload;
  } catch (error) {
    if (error?.name === "AbortError") throw new Error("Tempo excedido ao processar os indicadores no Supabase.");
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}

export function dashboardFilters(body = {}) {
  return {
    periodStart: String(body.periodStart || ""),
    periodEnd: String(body.periodEnd || ""),
    unitFilter: String(body.unitFilter || ""),
    unitFilters: Array.isArray(body.unitFilters) ? body.unitFilters.join("||") : String(body.unitFilters || ""),
    ageFilter: String(body.ageFilter || ""),
    ageFilters: Array.isArray(body.ageFilters) ? body.ageFilters.join("||") : String(body.ageFilters || ""),
    genderFilter: String(body.genderFilter || ""),
    genderFilters: Array.isArray(body.genderFilters) ? body.genderFilters.join("||") : String(body.genderFilters || ""),
  };
}
