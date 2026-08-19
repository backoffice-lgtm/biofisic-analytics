export default async (request, context) => {
  const user = Netlify.env.get("DASHBOARD_USER") || "";
  const password = Netlify.env.get("DASHBOARD_PASSWORD") || "";
  if (!user || !password) {
    return new Response("BioFisic Analytics: configure DASHBOARD_USER e DASHBOARD_PASSWORD no Netlify.", { status:503, headers:{"content-type":"text/plain; charset=utf-8","cache-control":"no-store"} });
  }
  const supplied = request.headers.get("authorization") || "";
  const expected = "Basic " + btoa(`${user}:${password}`);
  if (supplied !== expected) {
    return new Response("Acesso restrito ao BioFisic Analytics.", { status:401, headers:{"WWW-Authenticate":'Basic realm="BioFisic Analytics"',"content-type":"text/plain; charset=utf-8","cache-control":"no-store"} });
  }
  return context.next();
};
