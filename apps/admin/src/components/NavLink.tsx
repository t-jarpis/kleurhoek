"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

/** Link in het zijmenu met een actieve stand (aria-current) voor de huidige sectie. */
export function NavLink({ href, children }: { href: string; children: React.ReactNode }) {
  const path = usePathname();
  const active = href === "/" ? path === "/" : path === href || path.startsWith(`${href}/`);
  return <Link href={href} aria-current={active ? "page" : undefined}>{children}</Link>;
}
