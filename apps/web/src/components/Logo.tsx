import Link from "next/link";

export function Logo({ market }: { market: string }) {
  return (
    <Link href={`/${market}`} className="logo" aria-label="Kleurhoek">
      {"Kleurhoek".split("").map((ch, i) => <span key={i} aria-hidden="true">{ch}</span>)}
    </Link>
  );
}
