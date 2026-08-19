import { json, rpc } from "./_lib/supabase.mjs";
export default async () => {
  try { return json(await rpc("biofisic_analytics_health", {}, 15000)); }
  catch (error) { return json({ status:"error", error:error?.message || String(error) }, error?.status || 500); }
};
