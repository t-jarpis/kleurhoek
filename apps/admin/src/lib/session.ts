import "server-only";

/**
 * De token waarmee het admin panel de API aanroept, namens de ingelogde beheerder.
 * Tot Zitadel gekoppeld is werkt dit alleen lokaal met ADMIN_DEV_TOKEN. In productie staat het
 * admin panel bovendien achter Cloudflare Access (zie ADR 0003 in de platform-repo).
 */
export function adminToken(): string {
  if (process.env.NODE_ENV === "production") throw new Error("Inloggen via Zitadel is nog niet gekoppeld; het admin panel draait nog niet in productie.");
  const token = process.env.ADMIN_DEV_TOKEN;
  if (!token || token.length < 32) throw new Error("Zet ADMIN_DEV_TOKEN (minstens 32 tekens), gelijk aan die van de API.");
  return token;
}
