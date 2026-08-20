import { json } from "./_lib/supabase.mjs";

function int(v){ return new Intl.NumberFormat("pt-BR",{maximumFractionDigits:0}).format(Number(v||0)); }
function pct(v){ return `${Number(v||0).toLocaleString("pt-BR",{minimumFractionDigits:1,maximumFractionDigits:1})}%`; }

export default async (request) => {
  if (request.method !== "POST") return json({error:"Use POST."},405);
  try {
    const body = await request.json();
    const q = String(body.question || "").toLowerCase();
    const ctx = body?.dashboard?.chatContext || {};
    const base = `Base analisada: ${int(ctx.active)} ativos, ${int(ctx.sales)} contratos vendidos, ${int(ctx.cancellations)} cancelamentos e ${int(ctx.access)} acessos.`;
    const finance = `Caixa: ticket vendido ${ctx.salesTicket || "R$ 0,00"} versus ticket recebido ${ctx.receivedTicket || "R$ 0,00"}.`;
    const retention = `Retenção: ${int(ctx.inadimplentes)} ativos inadimplentes (${pct(ctx.inadimplentesPct)}).`;
    const frequency = `Frequência: média de ${Number(ctx.ownAccessMean||0).toFixed(1).replace(".",",")} acessos por aluno próprio e ${Number(ctx.aggregatorAccessMean||0).toFixed(1).replace(".",",")} por agregador.`;
    let answer = `${base} ${finance} ${retention} ${frequency}`;
    if (q.includes("venda") || q.includes("ticket") || q.includes("fatur")) answer = `${base} ${finance}`;
    else if (q.includes("churn") || q.includes("cancel") || q.includes("inadimpl")) answer = `${base} ${retention}`;
    else if (q.includes("frequ") || q.includes("acesso")) answer = `${base} ${frequency}`;
    return json({ answer, mode:"local_semantic", model:"biofisic-analytics" });
  } catch (error) { return json({error:error?.message || String(error)},500); }
};
