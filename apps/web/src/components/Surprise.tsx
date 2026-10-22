"use client";
import { useRouter } from "next/navigation";

export function Surprise({ market, slugs, label }: { market: string; slugs: string[]; label: string }) {
  const router = useRouter();
  return <button type="button" className="btn primary" onClick={() => router.push(`/${market}/platen/${slugs[Math.floor(Math.random() * slugs.length)]}`)}>{label}</button>;
}
