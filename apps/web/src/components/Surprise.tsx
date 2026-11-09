"use client";
import { useBase } from "./Base";
import { useRouter } from "next/navigation";
import { link } from "@/lib/sites";
import { loadPlates } from "@/lib/plate-index";

/** Een willekeurige plaat. De lijst komt van `platen.json` (ADR 0099); meestal heeft het raster hem al geladen. */
export function Surprise({ label }: { label: string }) {
  const base = useBase();
  const router = useRouter();
  const go = () => loadPlates(base).then((plates) => {
    const p = plates[Math.floor(Math.random() * plates.length)];
    if (p) router.push(link(base, `/platen/${p.slug}`));
  }, () => { /* lijst niet te laden: de knop doet dan even niets */ });
  return <button type="button" className="btn primary" onClick={() => void go()}>{label}</button>;
}
