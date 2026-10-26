"use server";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { z } from "zod";
import { adminApi, ApiError } from "@/lib/api";
import { back } from "./labels";

const Id = z.uuid();
const message = (e: unknown, fallback: string) => (e instanceof ApiError ? e.message : fallback);

export async function setStatus(formData: FormData) {
  const id = Id.parse(formData.get("id"));
  const status = z.enum(["new", "open", "answered", "closed", "spam"]).parse(formData.get("status"));
  try { await adminApi.setConversationStatus(id, status); } catch (e) { redirect(back(`/contact/${id}`, "fout", message(e, "Opslaan mislukt"))); }
  revalidatePath("/contact", "layout");
  redirect(back(`/contact/${id}`, "melding", "Status bijgewerkt"));
}

export async function addMessage(formData: FormData) {
  const id = Id.parse(formData.get("id"));
  const direction = z.enum(["out", "note"]).parse(formData.get("direction"));
  const body = String(formData.get("body") ?? "").trim();
  if (!body) redirect(back(`/contact/${id}`, "fout", "Schrijf eerst iets"));
  try { await adminApi.addConversationMessage(id, direction, body); } catch (e) { redirect(back(`/contact/${id}`, "fout", message(e, "Opslaan mislukt"))); }
  revalidatePath("/contact", "layout");
  redirect(back(`/contact/${id}`, "melding", direction === "out" ? "Antwoord vastgelegd" : "Notitie toegevoegd"));
}

export async function deleteConversation(formData: FormData) {
  const id = Id.parse(formData.get("id"));
  if (formData.get("confirm") !== "ja") redirect(back(`/contact/${id}`, "fout", "Vink eerst aan dat je het gesprek wilt verwijderen"));
  try { await adminApi.deleteConversation(id); } catch (e) { redirect(back(`/contact/${id}`, "fout", message(e, "Verwijderen mislukt"))); }
  revalidatePath("/contact", "layout");
  redirect(back("/contact", "melding", "Gesprek verwijderd"));
}

export async function toggleChannel(formData: FormData) {
  const slug = z.enum(["web", "whatsapp"]).parse(formData.get("slug"));
  try { await adminApi.updateContactChannel(slug, { enabled: formData.get("enabled") === "true" }); } catch (e) { redirect(back("/contact/kanalen", "fout", message(e, "Opslaan mislukt"))); }
  revalidatePath("/contact/kanalen");
  redirect(back("/contact/kanalen", "melding", "Kanaal bijgewerkt"));
}
