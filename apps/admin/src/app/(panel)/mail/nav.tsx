import Link from "next/link";

export function MailNav({ active }: { active: "overzicht" | "templates" | "workflows" | "campagnes" | "bezorging" }) {
  const items = [["overzicht", "/mail", "Overzicht"], ["campagnes", "/mail/campagnes", "Campagnes"], ["workflows", "/mail/workflows", "Workflows"], ["templates", "/mail/templates", "Templates"], ["bezorging", "/mail/bezorging", "Bezorging"]] as const;
  return (
    <nav className="tabs" aria-label="Mail">
      {items.map(([key, href, label]) => <Link key={key} aria-current={active === key ? "page" : undefined} href={href}>{label}</Link>)}
    </nav>
  );
}

export const TOPIC_LABEL: Record<string, string> = { "nieuwe-platen": "Nieuwe platen", feestdagen: "Feestdagen", nieuwsbrief: "Nieuwsbrief" };
export const KIND_LABEL: Record<string, string> = { system: "Vast", automation: "Automatisch", campaign: "Campagne" };
