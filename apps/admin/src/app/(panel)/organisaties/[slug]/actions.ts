"use server";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { z } from "zod";
import { adminApi, ApiError, type OrgInput } from "@/lib/api";
import { back } from "../labels";

const SLUG = /^[a-z0-9](?:[a-z0-9-]{0,30}[a-z0-9])?$/;
const LOGO_TYPES = ["image/png", "image/webp", "image/jpeg", "image/svg+xml"];

function slugOf(formData: FormData): string {
  const slug = String(formData.get("slug") ?? "");
  if (!SLUG.test(slug)) redirect(back("/organisaties", "fout", "Onbekende organisatie"));
  return slug;
}

async function save(slug: string, tab: string, run: () => Promise<unknown>, melding: string) {
  const path = `/organisaties/${slug}?tab=${tab}`;
  try {
    await run();
  } catch (e) {
    redirect(back(path, "fout", e instanceof ApiError ? e.message : "Opslaan mislukt"));
  }
  revalidatePath("/organisaties");
  revalidatePath(`/organisaties/${slug}`);
  redirect(back(path, "melding", melding));
}

const General = z.object({
  name: z.string().trim().min(2).max(80),
  kind: z.enum(["platform", "school", "opvang", "vereniging", "bedrijf", "overig"]).optional(),
  hosts: z.string().max(2000).optional(),
});

export async function saveGeneral(formData: FormData) {
  const slug = slugOf(formData);
  const parsed = General.safeParse(Object.fromEntries(formData));
  if (!parsed.success) redirect(back(`/organisaties/${slug}?tab=algemeen`, "fout", "Naam: 2 tot 80 tekens"));
  const { name, kind, hosts } = parsed.data!;
  const body: OrgInput = { name, ...(kind ? { kind } : {}) };
  if (hosts !== undefined) body.hosts = hosts.split(/[\s,]+/).map((h) => h.trim().toLowerCase().replace(/^https?:\/\//, "").replace(/\/.*$/, "")).filter(Boolean);
  if (formData.has("active-field")) body.active = formData.get("active") === "on";
  await save(slug, "algemeen", () => adminApi.updateOrganization(slug, body), "Opgeslagen. De site toont het binnen 30 seconden.");
}

const Color = z.string().trim().toLowerCase().regex(/^(#[0-9a-f]{6})?$/, "Kleur als #rrggbb");
const Brand = z.object({
  theme: z.string().max(40), font: z.string().max(40), primary: Color, accent: Color, wordmark: z.string().trim().max(30),
});

export async function saveBrand(formData: FormData) {
  const slug = slugOf(formData);
  const parsed = Brand.safeParse(Object.fromEntries(formData));
  if (!parsed.success) redirect(back(`/organisaties/${slug}?tab=huisstijl`, "fout", parsed.error.issues[0]!.message));
  const b = parsed.data!;
  await save(slug, "huisstijl", () => adminApi.updateOrganization(slug, {
    brand: { theme: b.theme || null, font: b.font || null, colors: { primary: b.primary || null, accent: b.accent || null }, wordmark: b.wordmark || null },
  }), "Huisstijl opgeslagen. De site toont hem binnen 30 seconden.");
}

export async function uploadLogo(formData: FormData) {
  const slug = slugOf(formData);
  const file = formData.get("logo");
  const path = `/organisaties/${slug}?tab=huisstijl`;
  if (!(file instanceof File) || file.size === 0) redirect(back(path, "fout", "Kies eerst een bestand."));
  const f = file as File;
  if (!LOGO_TYPES.includes(f.type)) redirect(back(path, "fout", "Logo: PNG, WebP, JPEG of SVG."));
  if (f.size > 256 * 1024) redirect(back(path, "fout", "Logo: maximaal 256 kB."));
  const data = Buffer.from(await f.arrayBuffer()).toString("base64");
  await save(slug, "huisstijl", () => adminApi.setOrganizationLogo(slug, f.type, data), "Logo opgeslagen.");
}

export async function removeLogo(formData: FormData) {
  const slug = slugOf(formData);
  await save(slug, "huisstijl", () => adminApi.removeOrganizationLogo(slug), "Logo verwijderd; de site gebruikt weer het woordmerk.");
}

/** Alles aangevinkt = alles (ook wat er later bij komt); niets aangevinkt mag niet. */
function pick(formData: FormData, field: string, all: string[], label: string, slug: string): string[] | null {
  const chosen = formData.getAll(field).map(String).filter((v) => all.includes(v));
  if (chosen.length === 0) redirect(back(`/organisaties/${slug}?tab=aanbod`, "fout", `Kies minstens één ${label}.`));
  return chosen.length === all.length ? null : chosen;
}

export async function saveOffer(formData: FormData) {
  const slug = slugOf(formData);
  const choices = await adminApi.organization(slug);
  const o = choices.options;
  const offer = {
    markets: pick(formData, "markets", o.markets, "markt", slug),
    categories: pick(formData, "categories", o.categories.map((c) => c.slug), "onderwerp", slug),
    ages: pick(formData, "ages", o.ages.map((a) => a.slug), "leeftijd", slug),
    kinds: pick(formData, "kinds", o.kinds.map((k) => k.slug), "soort plaat", slug) as ("kleurplaat" | "knutselen")[] | null,
  };
  const features = { shop: formData.get("shop") === "on", accounts: formData.get("accounts") === "on" };
  await save(slug, "aanbod", () => adminApi.updateOrganization(slug, { offer, features }), "Aanbod opgeslagen. De site toont het binnen 30 seconden.");
}
