import Link from "next/link";
import type { Source } from "@/lib/api";

export const back = (path: string, kind: "melding" | "fout", text: string) => `${path}${path.includes("?") ? "&" : "?"}${kind}=${encodeURIComponent(text)}`;
export const when = (iso: string | null) => (iso ? new Date(iso).toLocaleString("nl-NL", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit", timeZone: "Europe/Amsterdam" }) : "nog niet");

export function SourcesNav({ active, attention }: { active: "themas" | "nakijken"; attention?: number }) {
  return (
    <nav className="tabs" aria-label="Bronnengids">
      <Link href="/bronnen" aria-current={active === "themas" ? "page" : undefined}>Thema&apos;s</Link>
      <Link href="/bronnen/nakijken" aria-current={active === "nakijken" ? "page" : undefined}>Nakijken{attention ? ` (${attention})` : ""}</Link>
    </nav>
  );
}

/** Eén regel uitleg over de staat van een bron, met de toon van de pill. */
export function sourceState(s: Source): { label: string; on: boolean; bad: boolean } {
  if (s.status === "rejected") return { label: "Afgewezen", on: false, bad: false };
  if (s.health === "broken") return { label: "Offline: werkt niet meer", on: false, bad: true };
  if (s.status === "pending") return { label: s.health === "ok" ? "Wacht op goedkeuring" : "Wacht op goedkeuring (controle niet gelukt)", on: false, bad: s.health !== "ok" };
  if (s.changed) return { label: "Online, pagina veranderd", on: true, bad: true };
  return { label: "Online", on: true, bad: false };
}
