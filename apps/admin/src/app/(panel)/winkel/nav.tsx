import Link from "next/link";

export function ShopNav({ active }: { active: "overzicht" | "producten" | "koppelingen" }) {
  const items = [["overzicht", "/winkel", "Overzicht"], ["producten", "/winkel/producten", "Producten"], ["koppelingen", "/winkel/koppelingen", "Koppelingen"]] as const;
  return (
    <nav className="tabs" aria-label="Winkel">
      {items.map(([key, href, label]) => <Link key={key} aria-current={active === key ? "page" : undefined} href={href}>{label}</Link>)}
    </nav>
  );
}
