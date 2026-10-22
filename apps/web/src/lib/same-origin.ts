/**
 * Alleen verzoeken van onze eigen pagina's mogen iets wijzigen (uitloggen, account verwijderen).
 * Sec-Fetch-Site zet de browser zelf; een andere site kan die niet vervalsen. Oudere browsers: Origin.
 */
export function sameOrigin(request: Request): boolean {
  const site = request.headers.get("sec-fetch-site");
  if (site) return site === "same-origin";
  const origin = request.headers.get("origin");
  return origin !== null && origin === new URL(request.url).origin;
}
