"use server";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { z } from "zod";
import { adminApi, ApiError } from "@/lib/api";
import { back } from "./labels";

const Create = z.object({
  name: z.string().trim().min(2, "Naam: minstens 2 tekens").max(80),
  slug: z.string().trim().toLowerCase().regex(/^[a-z0-9](?:[a-z0-9-]{0,30}[a-z0-9])?$/, "Code: kleine letters, cijfers en streepjes"),
  kind: z.enum(["school", "opvang", "vereniging", "bedrijf", "overig"]),
});

export async function createOrganization(formData: FormData) {
  const parsed = Create.safeParse(Object.fromEntries(formData));
  if (!parsed.success) redirect(back("/organisaties", "fout", parsed.error.issues[0]!.message));
  let slug = "";
  try {
    slug = (await adminApi.createOrganization(parsed.data!)).slug;
  } catch (e) {
    redirect(back("/organisaties", "fout", e instanceof ApiError ? e.message : "Aanmaken mislukt"));
  }
  revalidatePath("/organisaties");
  redirect(back(`/organisaties/${slug}?tab=huisstijl`, "melding", "Organisatie aangemaakt. Kies nu de huisstijl."));
}
