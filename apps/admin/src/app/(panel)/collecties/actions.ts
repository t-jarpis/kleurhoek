"use server";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { adminApi, ApiError } from "@/lib/api";

const LANGS = ["nl", "de", "en", "fr", "es", "it", "pl"] as const;
export type CollectionState = { error: string | null };

/** Collectie opslaan (ADR 0036): naam per taal, omschrijving per taal en de gekozen platen op volgorde. */
export async function saveCollection(_prev: CollectionState, formData: FormData): Promise<CollectionState> {
  const slug = String(formData.get("slug") ?? "").trim();
  if (!/^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$/.test(slug)) return { error: "Code: kleine letters, cijfers en streepjes, bijvoorbeeld rekenen-groep-3." };
  const names = Object.fromEntries(LANGS.map((l) => [l, String(formData.get(`name-${l}`) ?? "").trim()]).filter(([, v]) => v));
  const descriptions = Object.fromEntries(LANGS.map((l) => [l, String(formData.get(`description-${l}`) ?? "").trim()]).filter(([, v]) => v));
  let plates: string[] = [];
  try { plates = JSON.parse(String(formData.get("plates") ?? "[]")) as string[]; } catch { return { error: "De platenlijst kon niet worden gelezen." }; }
  try {
    await adminApi.saveCollection(slug, { names, descriptions, plates });
  } catch (e) {
    if (e instanceof ApiError) return { error: e.message };
    throw e;
  }
  revalidatePath("/collecties");
  redirect(`/collecties?melding=${encodeURIComponent(`Collectie ${names.nl ?? slug} opgeslagen.`)}`);
}

export async function deleteCollection(formData: FormData) {
  const slug = String(formData.get("slug") ?? "");
  let message = "Collectie verwijderd.";
  try { await adminApi.deleteCollection(slug); } catch (e) { if (e instanceof ApiError) message = e.message; else throw e; }
  revalidatePath("/collecties");
  redirect(`/collecties?melding=${encodeURIComponent(message)}`);
}
