"use server";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { z } from "zod";
import { adminApi, ApiError } from "@/lib/api";

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
    markets: String(formData.get("markets") ?? "nl-NL").split(",").map((m) => m.trim()).filter(Boolean),
    materials: formData.getAll("material").map(String),
    rank: Math.min(99, Math.max(0, Number(formData.get("rank") ?? 0) || 0)),
  }), "Product opgeslagen");
}

export type ProductFormState = { error?: string; values?: Record<string, string | string[]> } | null;

/** Product opslaan vanuit het formulier: bij een fout blijft alles staan wat iemand invulde. */
export async function saveProductForm(_prev: ProductFormState, formData: FormData): Promise<ProductFormState> {
  const values: Record<string, string | string[]> = {};
  for (const k of ["slug", "name", "partner", "url", "priceHint", "ean", "note", "markets", "rank"]) values[k] = String(formData.get(k) ?? "");
  values.material = formData.getAll("material").map(String);
  values.enabled = formData.get("enabled") === "on" ? "on" : "";
  const slug = Slug.safeParse(String(values.slug).trim());
  if (!slug.success) return { error: "Gebruik voor de code kleine letters, cijfers en streepjes (minstens 2 tekens).", values };
  const text = (k: string) => { const v = String(values[k] ?? "").trim(); return v || null; };
  try {
    await adminApi.saveProduct(slug.data, {
      partner: String(values.partner), url: String(values.url).trim(), name: String(values.name).trim(),
      note: text("note"), priceHint: text("priceHint"), ean: text("ean"), enabled: values.enabled === "on",
      markets: String(values.markets || "nl-NL").split(",").map((m) => m.trim()).filter(Boolean),
      materials: values.material as string[], rank: Math.min(99, Math.max(0, Number(values.rank) || 0)),
    });
  } catch (e) {
    if (e instanceof ApiError) return { error: e.message, values };
    throw e;
  }
  done("/winkel/producten", "Product opgeslagen");
}
