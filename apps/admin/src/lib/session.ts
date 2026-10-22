import "server-only";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { getBff } from "./auth";

export interface Viewer { name: string | null; email: string | null; dev: boolean }

/**
 * Het access token waarmee het admin panel de API aanroept, namens de ingelogde beheerder.
 * De proxy heeft de sessie al gecontroleerd en zo nodig ververst. Zonder Zitadel-configuratie
 * alleen lokaal met ADMIN_DEV_TOKEN; in productie weigert het panel dan te werken.
 */
export async function adminToken(): Promise<string> {
  const bff = getBff();
  if (bff) {
    const { session } = await bff.session((await cookies()).toString());
    if (!session) redirect("/auth/login");
    return session.accessToken;
  }
  if (process.env.NODE_ENV === "production") throw new Error("Inloggen is niet ingesteld (OIDC_ISSUER, OIDC_CLIENT_ID, ADMIN_URL, SESSION_SECRET, ADMIN_ORG_ID).");
  const token = process.env.ADMIN_DEV_TOKEN;
  if (!token || token.length < 32) throw new Error("Zet ADMIN_DEV_TOKEN (minstens 32 tekens), gelijk aan die van de API, of configureer Zitadel.");
  return token;
}

export async function viewer(): Promise<Viewer> {
  const bff = getBff();
  if (!bff) return { name: "Lokale beheerder", email: null, dev: true };
  const { session } = await bff.session((await cookies()).toString());
  return { name: session?.name ?? null, email: session?.email ?? null, dev: false };
}
