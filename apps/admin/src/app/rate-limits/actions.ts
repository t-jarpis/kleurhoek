"use server";
import { revalidatePath } from "next/cache";
import { z } from "zod";
import { adminApi } from "@/lib/api";

const Form = z.object({ slug: z.string().regex(/^[a-z0-9-]+$/), limit: z.coerce.number().int().min(1).max(1_000_000), windowSeconds: z.coerce.number().int().min(1).max(86_400) });

export async function saveRule(formData: FormData) {
  const data = Form.parse(Object.fromEntries(formData));
  await adminApi.updateRateLimit(data.slug, { limit: data.limit, windowSeconds: data.windowSeconds });
  revalidatePath("/rate-limits");
}

export async function toggleRule(formData: FormData) {
  const slug = z.string().regex(/^[a-z0-9-]+$/).parse(formData.get("slug"));
  await adminApi.updateRateLimit(slug, { enabled: formData.get("enabled") === "true" });
  revalidatePath("/rate-limits");
}
