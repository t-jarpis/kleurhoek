const ZONES: Record<string, string> = { NL: "Europe/Amsterdam", BE: "Europe/Brussels", DE: "Europe/Berlin", AT: "Europe/Vienna", CH: "Europe/Zurich", FR: "Europe/Paris", GB: "Europe/London", IE: "Europe/Dublin", ES: "Europe/Madrid", IT: "Europe/Rome", PL: "Europe/Warsaw", US: "America/New_York" };

/** De datum van vandaag in de tijdzone van een land, als YYYY-MM-DD. */
export function todayIn(country: string, now = new Date()): string {
  return new Intl.DateTimeFormat("en-CA", { timeZone: ZONES[country] ?? "UTC", year: "numeric", month: "2-digit", day: "2-digit" }).format(now);
}
