import type { MailStep, MailTrigger } from "@/lib/api";

export const DAYS = ["zondag", "maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag"];

/** Aanleiding in woorden, voor de lijst. */
export function describeTrigger(t: MailTrigger): string {
  if (t.type === "subscribed") return "Na aanmelden";
  if (t.type === "schedule") return `Elke ${DAYS[t.weekday]} om ${t.hour}:00`;
  if (t.type === "plates_published") return `Zodra er ${t.min} nieuwe ${t.min === 1 ? "plaat is" : "platen zijn"}`;
  return `${t.days} dagen voor een feestdag`;
}

export function describeStep(s: MailStep, templates: Map<string, string>): string {
  if (s.type === "filter") return `Filter: ${[...(s.topics ?? []), ...(s.markets ?? [])].join(", ") || "iedereen"}`;
  if (s.type === "require_plates") return `Alleen als er ${s.min} nieuwe platen zijn`;
  if (s.type === "wait") return `Wacht ${s.hours} uur`;
  return `Mail: ${templates.get(s.template) ?? s.template}`;
}
