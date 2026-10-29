import Link from "next/link";
import { link } from "@/lib/sites";

/** Breadcrumb uit het design system (ADR 0055). Het laatste item is de huidige pagina, zonder link. */
export function Crumbs({ items, base, label }: { items: { name: string; path?: string }[]; base: string; label: string }) {
  return (
    <nav className="ui-crumbs no-print" aria-label={label}>
      <ol>
        {items.map((c, i) => (
          <li key={i} aria-current={i === items.length - 1 ? "page" : undefined}>
            {c.path !== undefined && i < items.length - 1 ? <Link href={link(base, c.path)}>{c.name}</Link> : c.name}
          </li>
        ))}
      </ol>
    </nav>
  );
}
