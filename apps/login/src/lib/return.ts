/** Alleen terug naar een eigen site (open redirect voorkomen); lokaal ook localhost. */
export function allowedReturn(url: string | null): string | null {
  if (!url) return null;
  try {
    const u = new URL(url);
    const local = process.env.NODE_ENV !== "production" && (u.hostname === "localhost" || u.hostname === "127.0.0.1");
    const ours = u.protocol === "https:" && (u.hostname === "kleurhoek.nl" || u.hostname.endsWith(".kleurhoek.nl"));
    return ours || local ? u.toString() : null;
  } catch {
    return null;
  }
}
