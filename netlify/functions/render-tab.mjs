import { json, rpc, dashboardFilters } from "./_lib/supabase.mjs";

export default async (request) => {
  if (request.method !== "POST") return json({ error: "Use POST." }, 405);
  try {
    const body = await request.json();
    const tab = String(body.activeTab || "ativos").toLowerCase();
    const force = ["1","true","yes","sim"].includes(String(body.force || "").toLowerCase());
    const payload = await rpc("biofisic_dashboard_tab", {
      p_tab: tab,
      p_filters: dashboardFilters(body),
      p_force: force,
    });
    return json(payload);
  } catch (error) {
    return json({ error: error?.message || String(error) }, error?.status || 500);
  }
};

export const config = { rateLimit: { windowLimit: 180, windowSize: 60, aggregateBy: ["ip", "domain"] } };
