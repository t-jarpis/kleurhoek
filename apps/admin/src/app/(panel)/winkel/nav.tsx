import Link from "next/link";

export function ShopNav({ active }: { active: "overzicht" | "producten" | "koppelingen" }) {
  const items = [["overzicht", "/winkel", "Overzicht"], ["producten", "/winkel/producten", "Producten"], ["koppelingen", "/winkel/koppelingen", "Koppelingen"]] as const;
  return (
    <div className="tabs" role="tablist" aria-label="Winkel">
      {items.map(([key, href, label]) => <Link key={key} role="tab" aria-selected={active === key} href={href}>{label}</Link>)}
    </div>
  );
}
