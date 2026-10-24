import Link from "next/link";
import { adminApi, describe, type Product } from "@/lib/api";
import { ShopNav } from "../nav";

export const metadata = { title: "Per land · Winkel" };

/**
 * CoverageMatrix (DS, ADR 0031): per materiaal en markt het product dat bezoekers zien. Zelfde regel als de
 * website: aan, partner aan, in die markt, laagste voorkeur eerst. "Geen" laat zien waar nog iets ontbreekt.
 */
export default async function PerCountry() {
  let data;
  try { data = await adminApi.products(); } catch (e) { const d = describe(e); return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>; }
  const { products, materials, partners, markets, amazonStores } = data;
  const enabledPartners = new Set(partners.filter((p) => p.enabled).map((p) => p.slug));
  // Kolommen: markten die er zijn, plus markten waar producten of Amazon-winkels voor bestaan.
  const codes = [...new Set([...markets.map((m) => m.code), ...products.flatMap((p) => p.markets), ...amazonStores.flatMap((s) => s.markets)])]
    .sort((a, b) => (a === "nl-NL" ? -1 : b === "nl-NL" ? 1 : a.slice(3).localeCompare(b.slice(3)) || a.localeCompare(b)));
  const status = new Map(markets.map((m) => [m.code, m.status]));
  const winner = (material: string, market: string): Product | undefined => products
    .filter((p) => p.enabled && enabledPartners.has(p.partner) && p.markets.includes(market) && p.materials.includes(material))
    .sort((a, b) => a.rank - b.rank || a.slug.localeCompare(b.slug))[0];
  const partnerName = (slug: string) => partners.find((p) => p.slug === slug)?.name ?? slug;
  return (
    <>
      <div>
        <h1>Per land</h1>
        <p className="lead">Welk product bezoekers per materiaal zien, per markt (land en taal). Een product telt alleen als het aan staat, de partner aan staat en de markt erbij staat.</p>
      </div>
      <div className="toolbar"><ShopNav active="landen" /></div>
      <div className="ui-table-wrap" tabIndex={0} role="region" aria-labelledby="cm-title">
        <table className="ui-table ui-matrix">
          <caption id="cm-title">Aanbod per land</caption>
          <thead><tr><th>Materiaal</th>{codes.map((c) => (
            <th key={c}>{c.slice(3)} · {c.slice(0, 2)}{status.get(c) === "live" ? "" : status.has(c) ? " (concept)" : " (geen markt)"}</th>
          ))}</tr></thead>
          <tbody>{materials.map((m) => (
            <tr key={m.slug}><th scope="row">{m.name}</th>{codes.map((c) => {
              const p = winner(m.slug, c);
              return p
                ? <td key={c}><Link href={`/winkel/producten?bewerk=${p.slug}`}>{p.name ?? p.slug}</Link><small>{partnerName(p.partner)}</small></td>
                : <td key={c} data-empty="">Geen</td>;
            })}</tr>
          ))}</tbody>
        </table>
      </div>
    </>
  );
}
