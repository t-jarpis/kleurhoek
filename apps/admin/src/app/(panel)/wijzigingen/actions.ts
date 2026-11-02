"use server";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { z } from "zod";
import { adminApi, ApiError } from "@/lib/api";

/** Zet een wijziging terug (ADR 0066). Een fout komt als melding boven de lijst. */
export async function undoChange(formData: FormData) {
  const id = z.string().uuid().parse(formData.get("id"));
  let done = "teruggezet";
  try { await adminApi.undoChange(id); } catch (e) { done = e instanceof ApiError ? `fout:${e.message}` : "fout:Dat lukte niet"; }
  revalidatePath("/wijzigingen");
  redirect(`/wijzigingen?${new URLSearchParams({ m: done })}`);
}
