import { json, rpc } from "./_lib/supabase.mjs";
export default async (request) => {
  if (request.method !== "POST") return json({ error:"Use POST." }, 405);
  try { return json(await rpc("biofisic_dashboard_sync", {}, 48000)); }
  catch (error) { return json({ error:error?.message || String(error) }, error?.status || 500); }
};
