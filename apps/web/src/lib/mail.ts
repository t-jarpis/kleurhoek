import "server-only";

/** Doorgeven aan de API (domein Berichten, ADR 0037). De API is niet publiek; de site is de enige ingang. */
export const API_URL = process.env.API_URL ?? "http://localhost:3001";
export const TOKEN = /^[A-Za-z0-9_.-]{20,80}$/;

export async function api(path: string, init: { method: string; body?: unknown; ip?: string | null } = { method: "GET" }) {
  return fetch(`${API_URL}/v1/mail/${path}`, {
    method: init.method, cache: "no-store", signal: AbortSignal.timeout(8000),
    headers: { ...(init.body !== undefined ? { "content-type": "application/json" } : {}), ...(init.ip ? { "cf-connecting-ip": init.ip } : {}) },
    ...(init.body !== undefined ? { body: JSON.stringify(init.body) } : {}),
  }).catch(() => null);
}
