"use server";
import { isIP } from "node:net";
import { revalidatePath } from "next/cache";
import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { z } from "zod";
import { adminApi, ApiError } from "@/lib/api";

/** Het IP-adres van de beheerder zelf, zoals Cloudflare het doorgeeft. */
export async function myIp(): Promise<string | null> {
  const ip = (await headers()).get("cf-connecting-ip");
  return ip && isIP(ip) ? ip : null;
}

/** IPv6 wisselt binnen het eigen netwerk (privacy-adressen); dan het hele /64-blok van de aansluiting. */
function cidrFor(ip: string): string {
  if (isIP(ip) === 4) return `${ip}/32`;
  const groups = ip.split("::")[0]!.split(":").concat(["0", "0", "0", "0"]).slice(0, 4);
  return `${groups.join(":")}::/64`;
}

async function save(body: Parameters<typeof adminApi.updateSiteAccess>[0], melding: string) {
  try {
    await adminApi.updateSiteAccess(body);
  } catch (e) {
    redirect(`/toegang?fout=${encodeURIComponent(e instanceof ApiError ? e.message : "Opslaan mislukt")}`);
  }
  revalidatePath("/toegang");
  redirect(`/toegang?melding=${encodeURIComponent(melding)}`);
}

const plain = (entries: { cidr: string; label: string }[]) => entries.map(({ cidr, label }) => ({ cidr, label }));

export async function addEntry(formData: FormData) {
  const data = z.object({ cidr: z.string().trim().min(1).max(64), label: z.string().trim().min(1).max(80) }).parse(Object.fromEntries(formData));
  const current = await adminApi.siteAccess();
  await save({ entries: [...plain(current.entries), data] }, `${data.cidr} toegevoegd. Binnen 30 seconden actief.`);
}

export async function addMine() {
  const ip = await myIp();
  if (!ip) redirect(`/toegang?fout=${encodeURIComponent("Je IP-adres is niet bekend (alleen via Cloudflare).")}`);
  const current = await adminApi.siteAccess();
  const cidr = cidrFor(ip!);
  if (current.entries.some((e) => e.cidr === cidr)) redirect(`/toegang?melding=${encodeURIComponent("Je IP-adres staat al in de lijst.")}`);
  await save({ entries: [...plain(current.entries), { cidr, label: "Mijn verbinding" }] }, `${cidr} toegevoegd. Binnen 30 seconden actief.`);
}

export async function removeEntry(formData: FormData) {
  const cidr = z.string().max(64).parse(formData.get("cidr"));
  const current = await adminApi.siteAccess();
  const rest = current.entries.filter((e) => e.cidr !== cidr);
  if (current.enabled && rest.length === 0) redirect(`/toegang?fout=${encodeURIComponent("Dit is het laatste adres. Zet de afscherming eerst uit.")}`);
  await save({ entries: plain(rest) }, `${cidr} verwijderd.`);
}

/** Aanzetten voegt je eigen adres toe als het er nog niet in staat, zodat je jezelf niet buitensluit. */
export async function setEnabled(formData: FormData) {
  const enabled = formData.get("enabled") === "true";
  if (!enabled) return save({ enabled: false }, "Afscherming uit: de website is weer voor iedereen.");
  const current = await adminApi.siteAccess();
  const ip = await myIp();
  const entries = plain(current.entries);
  if (ip && !entries.some((e) => e.cidr === cidrFor(ip))) entries.push({ cidr: cidrFor(ip), label: "Mijn verbinding" });
  await save({ enabled: true, entries }, "Afscherming aan: alleen adressen uit de lijst zien de website.");
}
