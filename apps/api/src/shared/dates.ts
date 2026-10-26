const ZONES: Record<string, string> = { NL: "Europe/Amsterdam", BE: "Europe/Brussels", DE: "Europe/Berlin", AT: "Europe/Vienna", CH: "Europe/Zurich", FR: "Europe/Paris", GB: "Europe/London", IE: "Europe/Dublin", ES: "Europe/Madrid", IT: "Europe/Rome", PL: "Europe/Warsaw", US: "America/New_York", CA: "America/Toronto", AU: "Australia/Sydney", NZ: "Pacific/Auckland", LU: "Europe/Luxembourg", LI: "Europe/Vaduz", MX: "America/Mexico_City", AR: "America/Argentina/Buenos_Aires", CO: "America/Bogota", BR: "America/Sao_Paulo", PT: "Europe/Lisbon", SE: "Europe/Stockholm", DK: "Europe/Copenhagen", NO: "Europe/Oslo", FI: "Europe/Helsinki", CZ: "Europe/Prague", SK: "Europe/Bratislava", HU: "Europe/Budapest", RO: "Europe/Bucharest", MD: "Europe/Chisinau", GR: "Europe/Athens", CY: "Asia/Nicosia", MT: "Europe/Malta", MC: "Europe/Monaco", AD: "Europe/Andorra", SM: "Europe/San_Marino" };

/** De datum van vandaag in de tijdzone van een land, als YYYY-MM-DD. */
export function todayIn(country: string, now = new Date()): string {
  return new Intl.DateTimeFormat("en-CA", { timeZone: ZONES[country] ?? "UTC", year: "numeric", month: "2-digit", day: "2-digit" }).format(now);
}
