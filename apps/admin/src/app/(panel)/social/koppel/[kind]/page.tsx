import { redirect } from "next/navigation";
import { adminApi, ApiError } from "@/lib/api";

export const dynamic = "force-dynamic";

/** Terug van Pinterest of Meta (ADR 0063): de code gaat naar de API, die de sleutels versleuteld bewaart. */
export default async function Callback({ params, searchParams }: { params: Promise<{ kind: string }>; searchParams: Promise<{ code?: string; state?: string; error?: string; error_description?: string }> }) {
  const { kind } = await params;
  const q = await searchParams;
  const k = kind === "meta" ? "meta" : kind === "pinterest" ? "pinterest" : null;
  let message: string;
  if (!k) message = "Onbekend kanaal.";
  else if (q.error || !q.code || !q.state) message = `Koppelen afgebroken${q.error_description ? `: ${q.error_description}` : "."}`;
  else {
    const overview = await adminApi.social();
    try {
      const r = await adminApi.socialConnect(k, { code: q.code, state: q.state, redirectUri: `${overview.redirectBase}/${k}` });
      message = k === "pinterest" ? "Pinterest gekoppeld." : `Gekoppeld: Facebook-pagina ${r.page ?? ""}${r.instagram ? ` en Instagram @${r.instagram}` : " (geen Instagram-account aan deze pagina gevonden)"}.`;
    } catch (e) { message = e instanceof ApiError ? e.message : "Koppelen mislukt."; }
  }
  redirect(`/social?tab=kanalen&melding=${encodeURIComponent(message)}`);
}
