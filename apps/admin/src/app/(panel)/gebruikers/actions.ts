"use server";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { z } from "zod";
import { adminApi, ApiError } from "@/lib/api";

const Id = z.string().uuid();
const Back = z.string().regex(/^\/gebruikers(\?[\w=&%.+-]*)?$/).catch("/gebruikers");

function back(formData: FormData, message?: string): never {
  const url = new URL(Back.parse(formData.get("back")), "http://x");
  if (message) url.searchParams.set("melding", message); else url.searchParams.delete("melding");
  redirect(url.pathname + url.search);
}

async function run(formData: FormData, work: () => Promise<unknown>, done: string) {
  try {
    await work();
  } catch (e) {
    if (e instanceof ApiError) back(formData, e.message);
    throw e;
  }
  revalidatePath("/gebruikers");
  back(formData, done);
}

export async function saveRoles(formData: FormData) {
  const id = Id.parse(formData.get("id"));
  const roles = formData.getAll("role").map((r) => z.string().regex(/^[a-z][a-z0-9-]{1,40}$/).parse(r));
  await run(formData, () => adminApi.setRoles(id, roles), "Rollen opgeslagen");
}

export async function setStatus(formData: FormData) {
  const id = Id.parse(formData.get("id"));
  const status = z.enum(["active", "blocked"]).parse(formData.get("status"));
  await run(formData, () => adminApi.setStatus(id, status), status === "blocked" ? "Gebruiker geblokkeerd" : "Gebruiker gedeblokkeerd");
}
