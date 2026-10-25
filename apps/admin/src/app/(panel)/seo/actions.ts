"use server";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { adminApi, ApiError, type SeoSettings } from "@/lib/api";

const text = (v: FormDataEntryValue | null) => (typeof v === "string" && v.trim() ? v.trim() : null);

/** Zoekcijfers nu ophalen (ADR 0041); de cijfers staan er na een minuut. */
export async function refreshSearch() {
  let message = "Ophalen gestart. Ververs de pagina over een minuut.";
  try { await adminApi.refreshSearch(); } catch (e) { if (e instanceof ApiError) message = e.message; else throw e; }
  redirect(`/seo?melding=${encodeURIComponent(message)}`);
}

/** Verificatiecodes en per markt de titel en omschrijving van de voorpagina. */
export async function saveSeo(formData: FormData) {
  const markets = formData.getAll("market").map(String);
  const body: SeoSettings = {
    googleVerification: text(formData.get("googleVerification")),
    bingVerification: text(formData.get("bingVerification")),
    home: Object.fromEntries(markets.map((m) => [m, { title: text(formData.get(`title-${m}`)), description: text(formData.get(`description-${m}`)) }])),
  };
  let message = "Opgeslagen. De site neemt het binnen een minuut over.";
  try { await adminApi.saveSeo(body); } catch (e) { if (e instanceof ApiError) message = e.message; else throw e; }
  revalidatePath("/seo");
  redirect(`/seo?melding=${encodeURIComponent(message)}`);
}
