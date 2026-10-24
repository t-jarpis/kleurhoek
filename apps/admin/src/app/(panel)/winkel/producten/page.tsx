import Link from "next/link";
import { adminApi, describe } from "@/lib/api";
import { ProductForm } from "./ProductForm";
import { importSuggestions, toggleProduct } from "../actions";
import { AmazonQuickAdd } from "./AmazonQuickAdd";
import { ShopNav } from "../nav";

export const metadata = { title: "Producten · Winkel" };

export default async function Products({ searchParams }: { searchParams: Promise<{ melding?: string; bewerk?: string; land?: string; status?: string }> }) {
  const { melding, bewerk, land, status } = await searchParams;
  let data;
  try { data = await adminApi.products(); } catch (e) { const d = describe(e); return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>; }
  const { products, materials, partners, suggestions, amazonStores } = data;
  // Landen in de lijst: uit de markten van de producten (ADR 0031).
  const countries = [...new Set(products.flatMap((p) => p.markets.map((m) => m.slice(3))))].sort();
  const country = land && countries.includes(land.toUpperCase()) ? land.toUpperCase() : null;
  const shown = products.filter((p) => (!country || p.markets.some((m) => m.endsWith(`-${country}`))) && (status !== "uit" || !p.enabled));
  const query = (next: { land?: string | null; status?: string | null }) => {
    const q = new URLSearchParams();
    const l = next.land === undefined ? country : next.land, st = next.status === undefined ? status : next.status;
    if (l) q.set("land", l.toLowerCase());
    if (st) q.set("status", st);
    const str = q.toString();
    return `/winkel/producten${str ? `?${str}` : ""}`;
  };
  const back = query({});
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
        <ProductForm editing={editing} partners={partners} materials={materials} marketOptions={[...new Set([...data.markets.map((m) => m.code), ...amazonStores.flatMap((s) => s.markets)])]} />
      </section>
      <section className="panel" aria-labelledby="amazon-title">
        <h2 id="amazon-title">Snel toevoegen via Amazon</h2>
        <p className="lead">Plak een link of ASIN en kies de winkels: per winkel komt er een product met de juiste link en landen.</p>
        <AmazonQuickAdd stores={amazonStores} materials={materials} />
      </section>
      <section className="panel" aria-labelledby="all-title">
        <h2 id="all-title">Alle producten</h2>
        <div className="checks" role="group" aria-label="Filter">
          <Link className="ui-chip" aria-current={!country && status !== "uit" ? "true" : undefined} href={query({ land: null, status: null })}>Alles <span className="ui-chip-count">{products.length}</span></Link>
          {countries.map((c) => (
            <Link key={c} className="ui-chip" aria-current={country === c ? "true" : undefined} href={query({ land: c })}>{c} <span className="ui-chip-count">{products.filter((p) => p.markets.some((m) => m.endsWith(`-${c}`))).length}</span></Link>
          ))}
          <Link className="ui-chip" aria-current={status === "uit" ? "true" : undefined} href={query({ status: status === "uit" ? null : "uit" })}>Alleen verborgen</Link>
        </div>
        {shown.length === 0 ? <p className="lead">Geen producten{country ? ` voor ${country}` : ""}.</p> : (
          <div className="ui-table-wrap" tabIndex={0} role="region" aria-labelledby="all-title">
            <table className="ui-table ui-suggest-table"><thead><tr><th>Product</th><th>Partner</th><th>Landen</th><th>Bij materialen</th><th>Zichtbaar</th><th aria-label="Actie" /></tr></thead>
              <tbody>{shown.map((p) => (
                <tr key={p.slug}>
                  <td className="ui-suggest-item"><b>{p.name ?? p.slug}</b><span>{[p.priceHint, p.note].filter(Boolean).join(" · ")}</span></td>
                  <td data-label="Partner">{partners.find((x) => x.slug === p.partner)?.name ?? p.partner}{partners.find((x) => x.slug === p.partner)?.enabled === false && <span className="ui-hint"> (partner uit)</span>}</td>
                  <td data-label="Landen">{[...new Set(p.markets.map((m) => m.slice(3)))].map((c) => <span key={c} className="ui-badge">{c}</span>)}</td>
                  <td data-label="Bij materialen">{p.materials.map(materialName).join(", ") || "—"}{p.rank ? ` (voorkeur ${p.rank})` : ""}</td>
                  <td><form action={toggleProduct}>
                    <input type="hidden" name="slug" value={p.slug} /><input type="hidden" name="enabled" value={String(!p.enabled)} /><input type="hidden" name="back" value={back} />
                    <button className="ui-switch" type="submit" aria-pressed={p.enabled}>{p.enabled ? "Zichtbaar" : "Verborgen"}<span className="visually-hidden">: {p.name ?? p.slug}</span></button>
                  </form></td>
                  <td><Link href={`/winkel/producten?bewerk=${p.slug}`}>Bewerken</Link></td>
                </tr>
              ))}</tbody></table>
          </div>
        )}
      </section>
    </>
  );
}
