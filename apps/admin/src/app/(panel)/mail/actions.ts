"use server";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { adminApi, ApiError, type MailCampaign, type MailTemplateInput, type MailWorkflow } from "@/lib/api";
import { viewer } from "@/lib/session";

export type ActionResult = { error: string | null };
const message = (e: unknown) => (e instanceof ApiError ? e.message : "Dat lukte niet. Probeer het opnieuw.");

/** Voorbeeld van een template zoals hij nu in de editor staat (ADR 0037). */
export async function previewTemplate(template: MailTemplateInput, market: string) {
  try { return { ok: true as const, ...(await adminApi.previewMail(template, market)) }; } catch (e) { return { ok: false as const, error: message(e) }; }
}

export async function saveTemplate(slug: string, template: MailTemplateInput, isNew: boolean): Promise<ActionResult> {
  try { await adminApi.saveMailTemplate(slug, template); } catch (e) { return { error: message(e) }; }
  revalidatePath("/mail/templates");
  if (isNew) redirect(`/mail/templates/${slug}?melding=${encodeURIComponent("Template opgeslagen.")}`);
  return { error: null };
}

/** Testmail naar het adres van de ingelogde beheerder. */
export async function testTemplate(template: MailTemplateInput, market: string): Promise<ActionResult & { to?: string }> {
  const who = await viewer();
  if (!who.email) return { error: "Je beheeraccount heeft geen e-mailadres." };
  try { await adminApi.testMail(template, market, who.email); return { error: null, to: who.email }; } catch (e) { return { error: message(e) }; }
}

export async function deleteTemplate(formData: FormData) {
  const slug = String(formData.get("slug") ?? "");
  let melding = "Template verwijderd.";
  try { await adminApi.deleteMailTemplate(slug); } catch (e) { melding = message(e); }
  revalidatePath("/mail/templates");
  redirect(`/mail/templates?melding=${encodeURIComponent(melding)}`);
}

export async function saveWorkflow(slug: string, body: Pick<MailWorkflow, "name" | "enabled" | "trigger" | "steps">, isNew: boolean): Promise<ActionResult> {
  try { await adminApi.saveMailWorkflow(slug, body); } catch (e) { return { error: message(e) }; }
  revalidatePath("/mail/workflows");
  redirect(`/mail/workflows?melding=${encodeURIComponent(isNew ? "Workflow aangemaakt." : "Workflow opgeslagen.")}`);
}

export async function deleteWorkflow(formData: FormData) {
  const slug = String(formData.get("slug") ?? "");
  let melding = "Workflow verwijderd.";
  try { await adminApi.deleteMailWorkflow(slug); } catch (e) { melding = message(e); }
  revalidatePath("/mail/workflows");
  redirect(`/mail/workflows?melding=${encodeURIComponent(melding)}`);
}

export async function audienceSize(audience: MailCampaign["audience"]) {
  try { return await adminApi.mailAudience(audience); } catch { return null; }
}

export async function createCampaign(_prev: ActionResult, formData: FormData): Promise<ActionResult> {
  const topics = formData.getAll("topics").map(String) as MailCampaign["audience"]["topics"];
  const markets = formData.getAll("markets").map(String);
  try {
    await adminApi.createMailCampaign({ name: String(formData.get("name") ?? ""), template: String(formData.get("template") ?? ""), audience: { topics, markets: markets.length ? markets : null } });
  } catch (e) { return { error: message(e) }; }
  revalidatePath("/mail/campagnes");
  redirect(`/mail/campagnes?melding=${encodeURIComponent("Campagne aangemaakt. Controleer het voorbeeld en verstuur hem.")}`);
}

export async function scheduleCampaign(formData: FormData) {
  const id = String(formData.get("id") ?? "");
  const when = String(formData.get("at") ?? "");
  // datetime-local is zonder tijdzone: tijd in Nederland.
  const at = when ? new Date(`${when}:00${amsterdamOffset(when)}`).toISOString() : null;
  let melding = at ? "Campagne gepland." : "Campagne staat in de wachtrij en gaat nu weg.";
  try { await adminApi.scheduleMailCampaign(id, at); } catch (e) { melding = message(e); }
  revalidatePath("/mail/campagnes");
  redirect(`/mail/campagnes?melding=${encodeURIComponent(melding)}`);
}

export async function cancelCampaign(formData: FormData) {
  let melding = "Campagne geannuleerd.";
  try { await adminApi.cancelMailCampaign(String(formData.get("id") ?? "")); } catch (e) { melding = message(e); }
  revalidatePath("/mail/campagnes");
  redirect(`/mail/campagnes?melding=${encodeURIComponent(melding)}`);
}

export async function removeSubscriber(formData: FormData) {
  let melding = "Abonnee verwijderd.";
  try { await adminApi.removeMailSubscriber(String(formData.get("id") ?? "")); } catch (e) { melding = message(e); }
  redirect(`/mail?melding=${encodeURIComponent(melding)}`);
}

/** UTC-verschil van Amsterdam op een datum, als "+01:00" of "+02:00". */
function amsterdamOffset(local: string): string {
  const d = new Date(`${local}:00Z`);
  const name = new Intl.DateTimeFormat("en-US", { timeZone: "Europe/Amsterdam", timeZoneName: "shortOffset" }).formatToParts(d).find((p) => p.type === "timeZoneName")?.value ?? "GMT+1";
  const h = Number(name.replace("GMT", "") || "0");
  return `${h >= 0 ? "+" : "-"}${String(Math.abs(h)).padStart(2, "0")}:00`;
}
