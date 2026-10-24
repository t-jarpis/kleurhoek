import Link from "next/link";
import { adminApi, describe } from "@/lib/api";
import { ProductForm } from "./ProductForm";
import { importSuggestions } from "../actions";
import { ShopNav } from "../nav";

export const metadata = { title: "Producten · Winkel" };

export default async function Products({ searchParams }: { searchParams: Promise<{ melding?: string; bewerk?: string }> }) {
  const { melding, bewerk } = await searchParams;
  let data;
  try { data = await adminApi.products(); } catch (e) { const d = describe(e); return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>; }
  const { products, materials, partners, suggestions } = data;
  const editing = products.find((p) => p.slug === bewerk);
  const materialName = (s: string) => materials.find((m) => m.slug === s)?.name ?? s;
  const covered = new Set(products.filter((p) => p.enabled).flatMap((p) => p.materials));

  return (
    <>
      <div>
        <h1>Producten</h1>
        <p className="lead">Een product hoort bij een of meer materialen. Bij elke plaat die dat materiaal nodig heeft, verschijnt het in "Wat heb je nodig" (alleen voor ouders, gemarkeerd als partnerlink).</p>
      </div>
      <div className="toolbar"><ShopNav active="producten" /></div>
      {melding && <p className="note" role="status">{melding}</p>}
      <section className="panel">
        <h2>Materialen zonder product</h2>
        {materials.every((m) => covered.has(m.slug)) ? <p className="lead">Elk materiaal heeft een product.</p> : (
          <p>{materials.filter((m) => !covered.has(m.slug)).map((m) => m.name).join(" · ")}</p>
        )}
      </section>
      {suggestions.length > 0 && (
        <section className="panel" aria-labelledby="suggest-title">
          <h2 id="suggest-title">Voorgestelde producten</h2>
          <div className="ui-suggest-head">
            <p>Producten die bij je materialen passen. Ze komen meteen online; controleer na het toevoegen de prijs en of de partner aan staat.</p>
            <form action={importSuggestions}>
              {suggestions.map((s) => <input key={s.slug} type="hidden" name="slug" value={s.slug} />)}
              <button className="ui-btn" data-variant="primary" type="submit">Alles toevoegen ({suggestions.length})</button>
            </form>
          </div>
          <table className="ui-suggest-table"><thead><tr><th>Product</th><th>Bij materiaal</th><th>Partner</th><th aria-label="Actie" /></tr></thead>
            <tbody>{suggestions.map((s) => (
              <tr key={s.slug}>
                <td className="ui-suggest-item"><b>{s.name}</b><span>{s.note}</span></td>
                <td data-label="Bij materiaal">{s.materials.map(materialName).join(", ")}</td>
                <td data-label="Partner"><a href={s.url} target="_blank" rel="noopener noreferrer">{partners.find((x) => x.slug === s.partner)?.name ?? s.partner}<span className="visually-hidden"> (opent in nieuw tabblad)</span></a></td>
                <td className="ui-suggest-action"><form action={importSuggestions}><input type="hidden" name="slug" value={s.slug} /><button className="ui-btn" data-variant="secondary" type="submit">Toevoegen</button></form></td>
              </tr>
            ))}</tbody></table>
        </section>
      )}
      <section className="panel">
        <h2>{editing ? `Bewerken: ${editing.name ?? editing.slug}` : "Product toevoegen"}</h2>
        <ProductForm editing={editing} partners={partners} materials={materials} />
      </section>
      <section className="panel">
        <h2>Alle producten</h2>
        {products.length === 0 ? <p className="lead">Nog geen producten.</p> : (
          <table><thead><tr><th>Product</th><th>Partner</th><th>Markten</th><th>Bij materialen</th><th>Status</th><th /></tr></thead>
            <tbody>{products.map((p) => (
              <tr key={p.slug}>
                <td className="rule"><b>{p.name ?? p.slug}</b><span className="lead">{p.priceHint ?? ""} {p.note ?? ""}</span></td>
                <td>{partners.find((x) => x.slug === p.partner)?.name ?? p.partner}</td>
                <td>{p.markets.join(", ")}</td>
                <td>{p.materials.map(materialName).join(", ") || "—"}{p.rank ? ` (voorkeur ${p.rank})` : ""}</td>
                <td><span className={`pill ${p.enabled ? "on" : "off"}`}>{p.enabled ? "Zichtbaar" : "Verborgen"}</span></td>
                <td><Link href={`/winkel/producten?bewerk=${p.slug}`}>Bewerken</Link></td>
              </tr>
            ))}</tbody></table>
        )}
      </section>
    </>
  );
}
