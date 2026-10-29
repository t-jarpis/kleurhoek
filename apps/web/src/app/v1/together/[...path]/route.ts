import { sameOrigin } from "@/lib/same-origin";

/**
 * Samen kleuren (ADR 0060) via het eigen domein; de API heeft geen publieke ingang. Alleen deze vier adressen:
 * POST rooms, GET rooms/<code>, GET en POST rooms/<code>/ops. Niets wordt gecachet.
 */
const API_URL = process.env.API_URL ?? "http://localhost:3001";
export const dynamic = "force-dynamic";
export const maxDuration = 30;

function target(path: string[], method: "GET" | "POST"): string | null {
  if (path[0] !== "rooms") return null;
  if (path.length === 1) return method === "POST" ? "rooms" : null;
  if (!/^[A-Za-z]{4}$/.test(path[1] ?? "")) return null;
  if (path.length === 2) return method === "GET" ? `rooms/${path[1]}` : null;
  if (path.length === 3 && path[2] === "ops") return `rooms/${path[1]}/ops`;
  return null;
}

async function forward(request: Request, path: string[], method: "GET" | "POST") {
  const t = target(path, method);
  if (!t) return new Response("Niet gevonden", { status: 404 });
  if (method === "POST" && !sameOrigin(request)) return new Response("Niet toegestaan", { status: 403 });
  const ip = request.headers.get("cf-connecting-ip");
  const query = new URL(request.url).search;
  const body = method === "POST" ? await request.text() : undefined;
  if (body && body.length > 250_000) return new Response("Te groot", { status: 413 });
  const upstream = await fetch(`${API_URL}/v1/together/${t}${method === "GET" ? query : ""}`, {
    method, cache: "no-store", body, signal: request.signal,
    headers: { ...(ip ? { "cf-connecting-ip": ip } : {}), ...(body ? { "content-type": "application/json" } : {}) },
  }).catch(() => null);
  if (!upstream) return new Response(null, { status: 502 });
  return new Response(upstream.body, { status: upstream.status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
}

type Ctx = { params: Promise<{ path: string[] }> };
export async function GET(request: Request, { params }: Ctx) { return forward(request, (await params).path, "GET"); }
export async function POST(request: Request, { params }: Ctx) { return forward(request, (await params).path, "POST"); }
