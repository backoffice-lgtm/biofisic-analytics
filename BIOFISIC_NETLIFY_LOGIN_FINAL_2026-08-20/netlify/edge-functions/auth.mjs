const SESSION_COOKIE = "biofisic_dashboard_session";
const SESSION_DURATION_SECONDS = 60 * 60 * 8;
const encoder = new TextEncoder();

const publicPaths = new Set([
  "/login.html",
  "/assets/login-unit-lorena.jpeg",
  "/favicon.ico",
  "/robots.txt",
]);

function bytesToBase64Url(bytes) {
  let binary = "";
  bytes.forEach(byte => { binary += String.fromCharCode(byte); });
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

function stringToBase64Url(value) {
  return bytesToBase64Url(encoder.encode(value));
}

function base64UrlToString(value) {
  const padded = value.replace(/-/g, "+").replace(/_/g, "/").padEnd(Math.ceil(value.length / 4) * 4, "=");
  const binary = atob(padded);
  return new TextDecoder().decode(Uint8Array.from(binary, character => character.charCodeAt(0)));
}

async function hmac(value, secret) {
  const key = await crypto.subtle.importKey(
    "raw",
    encoder.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  return bytesToBase64Url(new Uint8Array(await crypto.subtle.sign("HMAC", key, encoder.encode(value))));
}

async function constantTimeTextEqual(left, right) {
  const [leftHash, rightHash] = await Promise.all([
    crypto.subtle.digest("SHA-256", encoder.encode(left)),
    crypto.subtle.digest("SHA-256", encoder.encode(right)),
  ]);
  const leftBytes = new Uint8Array(leftHash);
  const rightBytes = new Uint8Array(rightHash);
  let mismatch = 0;
  for (let index = 0; index < leftBytes.length; index += 1) mismatch |= leftBytes[index] ^ rightBytes[index];
  return mismatch === 0;
}

async function createSession(user, secret) {
  const payload = stringToBase64Url(JSON.stringify({
    sub: user,
    exp: Math.floor(Date.now() / 1000) + SESSION_DURATION_SECONDS,
  }));
  return `${payload}.${await hmac(payload, secret)}`;
}

async function validateSession(token, expectedUser, secret) {
  if (!token || !token.includes(".")) return false;
  const [payload, suppliedSignature] = token.split(".", 2);
  const expectedSignature = await hmac(payload, secret);
  if (!(await constantTimeTextEqual(suppliedSignature, expectedSignature))) return false;
  try {
    const session = JSON.parse(base64UrlToString(payload));
    return session.sub === expectedUser && Number(session.exp) > Math.floor(Date.now() / 1000);
  } catch {
    return false;
  }
}

function cookieValue(request, name) {
  const cookieHeader = request.headers.get("cookie") || "";
  const item = cookieHeader.split(";").map(part => part.trim()).find(part => part.startsWith(`${name}=`));
  return item ? decodeURIComponent(item.slice(name.length + 1)) : "";
}

function safeNextPath(value) {
  return typeof value === "string" && value.startsWith("/") && !value.startsWith("//") && !value.startsWith("/login.html")
    ? value
    : "/";
}

function jsonResponse(payload, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      ...extraHeaders,
    },
  });
}

export default async (request, context) => {
  const url = new URL(request.url);
  const user = Netlify.env.get("DASHBOARD_USER") || "";
  const password = Netlify.env.get("DASHBOARD_PASSWORD") || "";
  const sessionSecret = Netlify.env.get("DASHBOARD_SESSION_SECRET") || password;

  if (!user || !password || !sessionSecret) {
    return new Response("BioFisic Analytics: configure DASHBOARD_USER e DASHBOARD_PASSWORD no Netlify.", {
      status: 503,
      headers: { "content-type": "text/plain; charset=utf-8", "cache-control": "no-store" },
    });
  }

  if (url.pathname === "/api/auth/login") {
    if (request.method !== "POST") return jsonResponse({ error: "Método não permitido." }, 405, { allow: "POST" });
    let credentials;
    try {
      credentials = await request.json();
    } catch {
      return jsonResponse({ error: "Credenciais inválidas." }, 400);
    }
    const validUser = await constantTimeTextEqual(String(credentials.user || ""), user);
    const validPassword = await constantTimeTextEqual(String(credentials.password || ""), password);
    if (!validUser || !validPassword) return jsonResponse({ error: "Usuário ou senha incorretos." }, 401);
    const session = await createSession(user, sessionSecret);
    return jsonResponse(
      { ok: true, redirect: safeNextPath(credentials.next) },
      200,
      { "set-cookie": `${SESSION_COOKIE}=${encodeURIComponent(session)}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=${SESSION_DURATION_SECONDS}` },
    );
  }

  if (url.pathname === "/api/auth/logout") {
    return new Response(null, {
      status: 302,
      headers: {
        location: "/login.html",
        "cache-control": "no-store",
        "set-cookie": `${SESSION_COOKIE}=; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=0`,
      },
    });
  }

  if (publicPaths.has(url.pathname)) return context.next();

  const session = cookieValue(request, SESSION_COOKIE);
  if (!(await validateSession(session, user, sessionSecret))) {
    const next = safeNextPath(`${url.pathname}${url.search}`);
    return Response.redirect(new URL(`/login.html?next=${encodeURIComponent(next)}`, request.url), 302);
  }

  return context.next();
};
