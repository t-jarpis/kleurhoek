"use server";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { adminApi, ApiError, type GoalMetric, type GoalMilestone } from "@/lib/api";

const METRICS: GoalMetric[] = ["visits", "plates", "clicks"];
const ROWS = 6;

function back(message: string): never {
  revalidatePath("/doelen");
  redirect(`/doelen?melding=${encodeURIComponent(message)}`);
}

/** Doelen opslaan: per meetwaarde de ingevulde rijen (maand na de start, doel, ambitie); lege rijen tellen niet. */
export async function saveGoals(formData: FormData) {
  const start = String(formData.get("start") ?? "");
  const metrics = {} as Record<GoalMetric, GoalMilestone[]>;
  for (const m of METRICS) {
    const rows: GoalMilestone[] = [];
    for (let i = 0; i < ROWS; i++) {
      const v = (k: string) => String(formData.get(`${m}.${i}.${k}`) ?? "").trim().replace(/\./g, "");
      if (!v("month") && !v("target")) continue;
      const target = Number(v("target")), stretch = v("stretch") ? Number(v("stretch")) : target;
      rows.push({ month: Number(v("month")), target, stretch });
    }
    if (!rows.length) back("Vul per meetwaarde minstens één rij in");
    if (rows.some((r) => [r.month, r.target, r.stretch].some((n) => !Number.isInteger(n) || n < 0))) back("Gebruik hele getallen van 0 of meer");
    metrics[m] = rows;
  }
  try { await adminApi.saveGoals({ start, metrics }); } catch (e) { if (e instanceof ApiError) back(e.message); throw e; }
  back("Doelen opgeslagen");
}
