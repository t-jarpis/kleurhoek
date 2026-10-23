import { Logo as BrandLogo } from "@kleurhoek/theme";
import Link from "next/link";

export function Logo({ market }: { market: string }) {
  return (
    <Link href={`/${market}`} className="logo" aria-label="Kleurhoek">
      <BrandLogo />
    </Link>
  );
}
