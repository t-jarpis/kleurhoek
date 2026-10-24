"use server";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { z } from "zod";
import { adminApi, ApiError } from "@/lib/api";
import { back } from "./labels";

const Slug = z.string().regex(/^[a-z0-9-]{1,64}$/);
const Id = z.uuid();
const msg = (e: unknown, fallback: string) => (e instanceof ApiError ? e.message : fallback);
const text = (f: FormData, k: string) => String(f.get(k) ?? "").trim();
const done = (path: string, melding: string) => { revalidatePath("/bronnen", "layout"); redirect(back(path, "melding", melding)); };

export async function createTheme(f: FormData) {
  const body = { slug: text(f, "slug").toLowerCase(), name: text(f, "name"), description: text(f, "description"), makerName: text(f, "makerName"), makerUrl: text(f, "makerUrl") };
  try { await adminApi.createTheme(body); } catch (e) { redirect(back("/bronnen", "fout", msg(e, "Aanmaken mislukt"))); }
  done(`/bronnen/${body.slug}`, "Thema aangemaakt. Voeg nu links naar de maker toe.");
}

export async function updateTheme(f: FormData) {
  const slug = Slug.parse(f.get("slug"));
  const body = {
    name: text(f, "name"), description: text(f, "description"), makerName: text(f, "makerName"), makerUrl: text(f, "makerUrl"),
    productSlugs: f.getAll("products").map(String).filter((p) => /^[a-z0-9-]{2,64}$/.test(p)),
  };
  try { await adminApi.updateTheme(slug, body); } catch (e) { redirect(back(`/bronnen/${slug}`, "fout", msg(e, "Opslaan mislukt"))); }
  done(`/bronnen/${slug}`, "Thema opgeslagen");
}

export async function publishTheme(f: FormData) {
  const slug = Slug.parse(f.get("slug"));
  const status = z.enum(["draft", "published"]).parse(f.get("status"));
  try { await adminApi.updateTheme(slug, { status }); } catch (e) { redirect(back(`/bronnen/${slug}`, "fout", msg(e, "Opslaan mislukt"))); }
  done(`/bronnen/${slug}`, status === "published" ? "Thema staat online" : "Thema is offline gehaald");
}

export async function addSource(f: FormData) {
  const theme = Slug.parse(f.get("theme"));
  const basis = z.enum(["link", "license"]).parse(f.get("basis"));
  const body = {
    url: text(f, "url"), title: text(f, "title"), description: text(f, "description") || null, basis,
    licenseNote: basis === "license" ? text(f, "licenseNote") || null : null,
    licenseDate: basis === "license" && text(f, "licenseDate") ? text(f, "licenseDate") : null,
  };
  let checked;
  try { checked = await adminApi.addSource(theme, body); } catch (e) { redirect(back(`/bronnen/${theme}`, "fout", msg(e, "Toevoegen mislukt"))); }
  done(`/bronnen/${theme}`, checked.health === "ok" ? "Link toegevoegd en gecontroleerd. Bekijk de pagina en keur hem goed." : `Link toegevoegd, maar de controle lukte niet: ${checked.checkNote ?? "onbekend"}`);
}

export async function sourceAction(f: FormData) {
  const id = Id.parse(f.get("id"));
  const theme = Slug.parse(f.get("theme"));
  const action = z.enum(["check", "approve", "reject", "delete"]).parse(f.get("action"));
  const to = f.get("from") === "nakijken" ? "/bronnen/nakijken" : `/bronnen/${theme}`;
  try {
    if (action === "delete") await adminApi.deleteSource(id);
    else await adminApi.sourceAction(id, action);
  } catch (e) { redirect(back(to, "fout", msg(e, "Mislukt"))); }
  done(to, { check: "Opnieuw gecontroleerd", approve: "Goedgekeurd: de link staat online (als het thema online staat)", reject: "Afgewezen", delete: "Verwijderd" }[action]);
}

export async function updateSource(f: FormData) {
  const id = Id.parse(f.get("id"));
  const theme = Slug.parse(f.get("theme"));
  const basis = z.enum(["link", "license"]).parse(f.get("basis"));
  try {
    await adminApi.updateSource(id, {
      title: text(f, "title"), description: text(f, "description") || null, basis,
      licenseNote: basis === "license" ? text(f, "licenseNote") || null : null,
      licenseDate: basis === "license" && text(f, "licenseDate") ? text(f, "licenseDate") : null,
    });
  } catch (e) { redirect(back(`/bronnen/${theme}`, "fout", msg(e, "Opslaan mislukt"))); }
  done(`/bronnen/${theme}`, "Link opgeslagen");
}
