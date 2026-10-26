import Link from "next/link";
import type { ContactTopic, ConversationStatus } from "@/lib/api";

export const TOPIC_LABEL: Record<ContactTopic, string> = {
  question: "Vraag", idea: "Idee voor een plaat", bug: "Iets werkt niet", partnership: "Samenwerken", copyright: "Auteursrecht", privacy: "Privacy", organization: "Aanvraag eigen omgeving",
};
export const STATUS_LABEL: Record<ConversationStatus, string> = { new: "Nieuw", open: "Open", answered: "Beantwoord", closed: "Gesloten", spam: "Spam" };
export const CHANNEL_LABEL = { web: "Website", whatsapp: "WhatsApp" } as const;

export const back = (path: string, kind: "melding" | "fout", text: string) => `${path}${path.includes("?") ? "&" : "?"}${kind}=${encodeURIComponent(text)}`;

export const when = (iso: string) => new Date(iso).toLocaleString("nl-NL", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit", timeZone: "Europe/Amsterdam" });

export function ContactNav({ active, unread }: { active: "inbox" | "kanalen"; unread?: number }) {
  return (
    <nav className="tabs" aria-label="Contact">
      <Link href="/contact" aria-current={active === "inbox" ? "page" : undefined}>Inbox{unread ? ` (${unread})` : ""}</Link>
      <Link href="/contact/kanalen" aria-current={active === "kanalen" ? "page" : undefined}>Kanalen</Link>
    </nav>
  );
}
