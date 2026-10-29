import { notFound, redirect } from "next/navigation";
import { baseFor } from "@/lib/base";
import { getOrg } from "@/lib/org";
import { link } from "@/lib/sites";

const API_URL = process.env.API_URL ?? "http://localhost:3001";
export const dynamic = "force-dynamic";

/** Een link om mee te doen (ADR 0060): naar de plaat van de kamer, met de code erbij. */
export default async function JoinPage({ params }: { params: Promise<{ org: string; market: string; code: string }> }) {
  const { org, market, code } = await params;
  const o = await getOrg(org);
  if (!o) notFound();
  const base = baseFor(o, market);
  const c = code.toUpperCase();
  if (!/^[A-HJ-NP-Z]{4}$/.test(c)) redirect(link(base, "/samen?fout=code"));
  const res = await fetch(`${API_URL}/v1/together/rooms/${c}`, { cache: "no-store" }).catch(() => null);
  if (!res?.ok) redirect(link(base, "/samen?fout=code"));
  const room = await res.json() as { slug: string };
  redirect(link(base, `/platen/${room.slug}?samen=${c}`));
}
