"use server";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { adminApi, ApiError, type SocialSettings } from "@/lib/api";

/** Server-acties voor Social (ADR 0063). Na elke actie terug naar dezelfde tab, met een melding. */
const back = (tab: string, message: string): never => { revalidatePath("/social"); redirect(`/social?tab=${tab}&melding=${encodeURIComponent(message)}`); };
const tabOf = (f: FormData) => (typeof f.get("tab") === "string" ? String(f.get("tab")) : "voorstellen");

async function attempt(tab: string, ok: string, fn: () => Promise<unknown>) {
  let message = ok;
  try { await fn(); } catch (e) { if (e instanceof ApiError) message = e.message; else throw e; }
  back(tab, message);
}

export async function decide(f: FormData) {
  const ids = f.getAll("id").map(String);
  const approve = f.get("approve") === "1";
  await attempt(tabOf(f), approve ? (ids.length > 1 ? `${ids.length} posts goedgekeurd.` : "Goedgekeurd.") : "Afgewezen.", () => adminApi.decideSocial(ids, approve));
}

export async function saveText(f: FormData) {
  const body = String(f.get("body") ?? "").trim();
  await attempt(tabOf(f), "Tekst opgeslagen.", () => adminApi.updateSocialPost(String(f.get("id")), { body }));
}

export async function markShared(f: FormData) {
  await attempt("delen", "Gemarkeerd als gedeeld.", () => adminApi.sharedSocial(String(f.get("id"))));
}

export async function generate() {
  let message = "";
  try { const r = await adminApi.generateSocial(); message = r.made ? `${r.made} nieuwe voorstellen.` : "Geen nieuwe voorstellen: alles voor de komende dagen staat er al."; }
  catch (e) { if (e instanceof ApiError) message = e.message; else throw e; }
  back("voorstellen", message);
}

export async function saveSettings(f: FormData) {
  const body: SocialSettings = {
    notifyEmail: String(f.get("notifyEmail") ?? "").trim() || null,
    pinsPerDay: Number(f.get("pinsPerDay") ?? 5),
    feedDays: f.getAll("feedDays").map(Number),
    feedTime: String(f.get("feedTime") ?? "19:30"),
  };
  await attempt("instellingen", "Instellingen opgeslagen.", () => adminApi.saveSocialSettings(body));
}

/** Naar de officiële inlogpagina van Pinterest of Meta; daarna komt Thijs terug op /social/koppel/<soort>. */
export async function connect(f: FormData) {
  const kind = f.get("kind") === "meta" ? "meta" : "pinterest";
  const base = String(f.get("redirectBase"));
  let url: string;
  try { url = await adminApi.socialConnectUrl(kind, `${base}/${kind}`); }
  catch (e) { if (e instanceof ApiError) back("kanalen", e.message); throw e; }
  redirect(url!);
}

export async function channel(f: FormData) {
  const kind = String(f.get("kind"));
  const action = String(f.get("action"));
  await attempt("kanalen", action === "ontkoppelen" ? "Ontkoppeld." : "Opgeslagen.", () =>
    adminApi.socialChannel(kind, action === "ontkoppelen" ? { connected: false } : { enabled: action === "aan" }));
}
