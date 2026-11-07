"use server";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { adminApi, ApiError, type WishStatus } from "@/lib/api";

const LABEL: Record<WishStatus, string> = { open: "weer open", made: "gemaakt", hidden: "verborgen" };

/** Gezocht (ADR 0084): een zoekwoord op gemaakt, verborgen of weer open zetten. Ongedaan maken kan bij Wijzigingen. */
export async function setWishStatus(f: FormData) {
  const term = String(f.get("term") ?? "");
  const status = String(f.get("status") ?? "") as WishStatus;
  let message = `"${term}" staat op ${LABEL[status] ?? status}.`;
  try { await adminApi.setWishStatus(term, status); } catch (e) { if (e instanceof ApiError) message = e.message; else throw e; }
  revalidatePath("/analytics");
  redirect(`/analytics?tab=gezocht&melding=${encodeURIComponent(message)}`);
}
