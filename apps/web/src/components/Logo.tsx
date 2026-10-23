import { Logo as BrandLogo } from "@kleurhoek/theme";
import Link from "next/link";
import { type Org, logoSrc } from "@/lib/org";

/** Logo van de organisatie: eigen afbeelding, eigen woordmerk of het merk van Kleurhoek. */
export function Logo({ market, org }: { market: string; org: Org }) {
  return (
    <Link href={`/${market}`} className="logo" aria-label={org.isDefault ? "Kleurhoek" : org.name}>
      <BrandLogo image={logoSrc(org)} wordmark={org.isDefault ? null : (org.brand.wordmark ?? org.name)} />
    </Link>
  );
}
