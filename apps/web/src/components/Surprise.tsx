"use client";
import { useHref } from "./Base";
import { useRouter } from "next/navigation";

export function Surprise({ market, slugs, label }: { market: string; slugs: string[]; label: string }) {
  const href = useHref();
  const router = useRouter();
  return <button type="button" className="btn primary" onClick={() => router.push(href(`/platen/${slugs[Math.floor(Math.random() * slugs.length)]}`))}>{label}</button>;
}
