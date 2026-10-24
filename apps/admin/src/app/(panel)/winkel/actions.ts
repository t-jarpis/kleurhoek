"use server";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { z } from "zod";
import { adminApi, ApiError, type SalesMapping, type SalesPreview } from "@/lib/api";

const Slug = z.string().regex(/^[a-z0-9-]{2,64}$/);

function done(path: string, message: string): never {
  revalidatePath("/winkel", "layout");
  redirect(`${path}${path.includes("?") ? "&" : "?"}melding=${encodeURIComponent(message)}`);
}

async function attempt(path: string, work: () => Promise<unknown>, ok: string) {
  try { await work(); } catch (e) { if (e instanceof ApiError) done(path, e.message); throw e; }
  done(path, ok);
}

/** De koppeling met een partner: aan/uit, het sjabloon en de waarden van jouw kant (zoals je site-ID). */
export async function savePartner(formData: FormData) {
  const slug = Slug.parse(formData.get("slug"));
  const settings: Record<string, string> = {};
  for (const [k, v] of formData.entries()) {
    if (k.startsWith("setting:") && typeof v === "string") settings[k.slice(8)] = v.trim();
  }
  const linkTemplate = String(formData.get("linkTemplate") ?? "").trim();
  await attempt("/winkel/koppelingen", () => adminApi.updatePartner(slug, { enabled: formData.get("enabled") === "on", linkTemplate, settings }), "Koppeling opgeslagen");
}

/** Een eigen partner, bijvoorbeeld een hobbywinkel via Daisycon of Awin. Start uitgeschakeld. */
export async function createPartner(formData: FormData) {
  const hosts = String(formData.get("allowedHosts") ?? "").split(/[\s,]+/).map((h) => h.trim().toLowerCase().replace(/^https?:\/\//, "").replace(/\/.*$/, "")).filter(Boolean);
  await attempt("/winkel/koppelingen", () => adminApi.createPartner({
    slug: String(formData.get("slug") ?? "").trim(),
    name: String(formData.get("name") ?? "").trim(),
    linkTemplate: String(formData.get("linkTemplate") ?? "").trim(),
    allowedHosts: hosts,
  }), "Partner toegevoegd. Vul de instellingen in en zet hem aan.");
}

export async function saveProduct(formData: FormData) {
  const slug = Slug.safeParse(String(formData.get("slug") ?? "").trim());
  if (!slug.success) done("/winkel/producten", "Gebruik voor de code kleine letters, cijfers en streepjes (minstens 2 tekens)");
  const text = (k: string) => { const v = String(formData.get(k) ?? "").trim(); return v || null; };
  await attempt(`/winkel/producten?bewerk=${slug.data}`, () => adminApi.saveProduct(slug.data, {
    partner: String(formData.get("partner") ?? ""),
    url: String(formData.get("url") ?? "").trim(),
    name: String(formData.get("name") ?? "").trim(),
    note: text("note"),
    priceHint: text("priceHint"),
    ean: text("ean"),
    enabled: formData.get("enabled") === "on",
    markets: formData.getAll("market").map(String),
    materials: formData.getAll("material").map(String),
    rank: Math.min(99, Math.max(0, Number(formData.get("rank") ?? 0) || 0)),
  }), "Product opgeslagen");
}

export type ProductFormState = { error?: string; values?: Record<string, string | string[]> } | null;

/** Product opslaan vanuit het formulier: bij een fout blijft alles staan wat iemand invulde. */
export async function saveProductForm(_prev: ProductFormState, formData: FormData): Promise<ProductFormState> {
  const values: Record<string, string | string[]> = {};
  for (const k of ["slug", "name", "partner", "url", "priceHint", "ean", "note", "rank"]) values[k] = String(formData.get(k) ?? "");
  values.material = formData.getAll("material").map(String);
  values.market = formData.getAll("market").map(String);
  if (!values.market.length) return { error: "Kies minstens één land.", values };
  values.enabled = formData.get("enabled") === "on" ? "on" : "";
  const slug = Slug.safeParse(String(values.slug).trim());
  if (!slug.success) return { error: "Gebruik voor de code kleine letters, cijfers en streepjes (minstens 2 tekens).", values };
  const text = (k: string) => { const v = String(values[k] ?? "").trim(); return v || null; };
  try {
    await adminApi.saveProduct(slug.data, {
      partner: String(values.partner), url: String(values.url).trim(), name: String(values.name).trim(),
      note: text("note"), priceHint: text("priceHint"), ean: text("ean"), enabled: values.enabled === "on",
      markets: values.market as string[],
      materials: values.material as string[], rank: Math.min(99, Math.max(0, Number(values.rank) || 0)),
    });
  } catch (e) {
    if (e instanceof ApiError) return { error: e.message, values };
    throw e;
  }
  done("/winkel/producten", "Product opgeslagen");
}

/** Voorgestelde producten overnemen: één (knop "Toevoegen") of alle (knop "Alles toevoegen"). */
export async function importSuggestions(formData: FormData) {
  const slugs = formData.getAll("slug").map(String).filter((s) => Slug.safeParse(s).success);
  if (!slugs.length) done("/winkel/producten", "Geen product gekozen");
  let added: string[];
  try { added = (await adminApi.importSuggestions(slugs)).added; } catch (e) { if (e instanceof ApiError) done("/winkel/producten", e.message); throw e; }
  done("/winkel/producten", added.length === 1 ? "1 product toegevoegd" : `${added.length} producten toegevoegd`);
}

/** Aan of uit vanuit de productlijst (ADR 0031); blijft op dezelfde pagina met hetzelfde filter. */
export async function toggleProduct(formData: FormData) {
  const slug = Slug.parse(formData.get("slug"));
  const back = String(formData.get("back") ?? "/winkel/producten");
  const path = back.startsWith("/winkel/") ? back : "/winkel/producten";
  const enabled = formData.get("enabled") === "true";
  await attempt(path, () => adminApi.setProductEnabled(slug, enabled), enabled ? "Product staat aan" : "Product staat uit");
}

export type AmazonState = { error?: string; added?: { slug: string; partner: string; url: string }[]; values?: Record<string, string | string[]> } | null;

/** Eén ASIN als product in meerdere Amazon-winkels (ADR 0031). Bij een fout blijft het formulier ingevuld. */
export async function amazonAdd(_prev: AmazonState, formData: FormData): Promise<AmazonState> {
  const values: Record<string, string | string[]> = {
    asin: String(formData.get("asin") ?? ""), name: String(formData.get("name") ?? ""), priceHint: String(formData.get("priceHint") ?? ""),
    material: formData.getAll("material").map(String), store: formData.getAll("store").map(String),
  };
  const names: Record<string, string> = {};
  for (const [k, v] of formData.entries()) if (k.startsWith("name:") && typeof v === "string" && v.trim()) { names[k.slice(5)] = v.trim(); values[k] = v; }
  if (!(values.material as string[]).length) return { error: "Kies minstens één materiaal.", values };
  if (!(values.store as string[]).length) return { error: "Kies minstens één winkel.", values };
  try {
    const r = await adminApi.amazonAdd({
      asin: String(values.asin).trim(), name: String(values.name).trim(), names,
      priceHint: String(values.priceHint).trim() || null, materials: values.material as string[], stores: values.store as string[],
    });
    revalidatePath("/winkel", "layout");
    return { added: r.added };
  } catch (e) {
    if (e instanceof ApiError) return { error: e.message, values };
    throw e;
  }
}

const FIELDS = ["date", "subId", "product", "items", "revenue", "commission", "currency"] as const;
export type SalesState = { partner?: string; fileName?: string; csv?: string; preview?: SalesPreview; error?: string; done?: { from: string; to: string; rows: number } } | null;

/**
 * Rapport van een partner (ADR 0033). Stap 1 (bestand gekozen): voorbeeld met herkende kolommen. Stap 2
 * (kolommen gekozen, "Bekijken" of "Importeren"): opnieuw voorbeeld of inlezen. De CSV blijft in het formulier.
 */
export async function salesStep(prev: SalesState, formData: FormData): Promise<SalesState> {
  const partner = String(formData.get("partner") ?? prev?.partner ?? "");
  const file = formData.get("file");
  let csv = String(formData.get("csv") ?? "");
  let fileName = String(formData.get("fileName") ?? "rapport.csv");
  if (file instanceof File && file.size > 0) {
    if (file.size > 900_000) return { error: "Het bestand is te groot (hooguit 900 kB). Exporteer een kortere periode." };
    csv = await file.text(); fileName = file.name;
  }
  if (!csv) return { error: "Kies een bestand." };
  const chosen = formData.has("map:date") ? Object.fromEntries(FIELDS.map((f) => [f, String(formData.get(`map:${f}`) ?? "") || null])) as SalesMapping : undefined;
  try {
    if (formData.get("intent") === "import" && chosen) {
      const r = await adminApi.salesImport({ partner, csv, fileName, mapping: chosen });
      revalidatePath("/winkel", "layout");
      return { done: r };
    }
    return { partner, fileName, csv, preview: await adminApi.salesPreview({ partner, csv, fileName, ...(chosen ? { mapping: chosen } : {}) }) };
  } catch (e) {
    if (e instanceof ApiError) return { partner, fileName, csv, error: e.message, ...(prev?.preview ? { preview: prev.preview } : {}) };
    throw e;
  }
}
