import Link from "next/link";
import { adminApi, describe } from "@/lib/api";
import { ShopNav } from "./nav";

export const metadata = { title: "Winkel" };

const iso = (d: Date) => d.toISOString().slice(0, 10);
const pct = (n: number) => `${(n * 100).toLocaleString("nl-NL", { maximumFractionDigits: 1 })}%`;
const PERIODS = [7, 30, 90] as const;

export default async function Shop({ searchParams }: { searchParams: Promise<{ dagen?: string }> }) {
  const requested = Number((await searchParams).dagen);
  const days = (PERIODS as readonly number[]).includes(requested) ? requested : 30;
  const to = new Date(), from = new Date(Date.now() - (days - 1) * 86_400_000);
  let data;
  try {
    const [summary, catalog] = await Promise.all([adminApi.shopSummary(iso(from), iso(to)), adminApi.products()]);
    data = { summary, catalog };
  } catch (e) {
    const d = describe(e);
    return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>;
  }
  const { summary, catalog } = data;
  const name = (slug: string) => catalog.products.find((p) => p.slug === slug)?.name ?? slug;
  const partnerOf = (slug: string) => {
    const partner = catalog.products.find((p) => p.slug === slug)?.partner;
    return catalog.partners.find((p) => p.slug === partner)?.name ?? partner ?? "—";
  };
  const byPartner = [...summary.products.reduce((m, p) => {
    const k = partnerOf(p.product); const v = m.get(k) ?? { clicks: 0, visitors: 0 };
    return m.set(k, { clicks: v.clicks + p.clicks, visitors: v.visitors + p.visitors });
  }, new Map<string, { clicks: number; visitors: number }>())].sort((a, b) => b[1].clicks - a[1].clicks);
  const growth = (g: number | null) => (g === null ? "nieuw" : `${g >= 0 ? "+" : ""}${pct(g)}`);
  const live = catalog.partners.filter((p) => p.enabled && p.slug !== "direct").length;

  return (
    <>
      <div>
        <h1>Winkel</h1>
        <p className="lead">Doorkliks naar producten bij partners, zonder cookies of persoonsgegevens. Gebruik dit om te zien wat ouders echt willen hebben, voordat je zelf gaat inkopen. De cijfers worden elke 10 minuten bijgewerkt.</p>
      </div>
      <div className="toolbar">
        <ShopNav active="overzicht" />
        <div className="tabs" aria-label="Periode">
          {PERIODS.map((d) => <Link key={d} href={`/winkel?dagen=${d}`} aria-selected={d === days}>{d} dagen</Link>)}
        </div>
      </div>
      {live === 0 && <p className="note">Nog geen partner gekoppeld. Vul je site-ID in bij <Link href="/winkel/koppelingen">Koppelingen</Link>, dan verschijnen producten bij de platen.</p>}
      <div className="cards">
        <div className="stat"><span>Lijst "Wat heb je nodig" bekeken</span><b>{summary.totals.materialsViews.toLocaleString("nl-NL")}</b></div>
        <div className="stat"><span>Doorkliks naar producten</span><b>{summary.totals.productClicks.toLocaleString("nl-NL")}</b></div>
        <div className="stat"><span>Klikratio</span><b>{pct(summary.totals.clickRate)}</b></div>
        <div className="stat"><span>Producten in de winkel</span><b>{catalog.products.filter((p) => p.enabled).length}</b></div>
      </div>
      <section className="panel">
        <h2>Kandidaten om zelf te leveren</h2>
        <p className="lead">Minstens 20 bezoekers die doorklikten in deze periode, en niet dalend ten opzichte van de periode ervoor ({summary.previous.from} t/m {summary.previous.to}). Kijk daarna in je partneraccount hoeveel er echt verkocht is.</p>
        {summary.candidates.length === 0 ? <p className="lead">Nog geen kandidaten. Dat komt vanzelf als er meer bezoekers zijn.</p> : (
          <table><thead><tr><th>Product</th><th className="num">Bezoekers</th><th className="num">Groei</th><th>Vooral vanaf</th></tr></thead>
            <tbody>{summary.candidates.map((p) => <tr key={p.product}><td><b>{name(p.product)}</b></td><td className="num">{p.visitors}</td><td className="num">{growth(p.growth)}</td><td>{p.topPlates.join(", ")}</td></tr>)}</tbody></table>
        )}
      </section>
      <section className="panel">
        <h2>Alle producten</h2>
        {summary.products.length === 0 ? <p className="lead">Nog geen doorkliks in deze periode.</p> : (
          <table><thead><tr><th>Product</th><th>Partner</th><th className="num">Doorkliks</th><th className="num">Bezoekers</th><th className="num">Vorige periode</th><th className="num">Groei</th><th>Vooral vanaf</th></tr></thead>
            <tbody>{summary.products.map((p) => <tr key={p.product}><td>{name(p.product)}</td><td>{partnerOf(p.product)}</td><td className="num">{p.clicks}</td><td className="num">{p.visitors}</td><td className="num">{p.previousVisitors}</td><td className="num">{growth(p.growth)}</td><td>{p.topPlates.join(", ")}</td></tr>)}</tbody></table>
        )}
      </section>
      <section className="panel">
        <h2>Per partner</h2>
        <p className="lead">Hoeveel verkeer je naar elke winkel stuurt. Dit is je onderhandelingspositie: met deze cijfers kun je een winkel vragen om een hogere vergoeding, een eigen kortingscode of een gezamenlijk pakket.</p>
        {byPartner.length === 0 ? <p className="lead">Nog geen doorkliks in deze periode.</p> : (
          <table><thead><tr><th>Partner</th><th className="num">Doorkliks</th><th className="num">Bezoekers</th></tr></thead>
            <tbody>{byPartner.map(([partner, v]) => <tr key={partner}><td>{partner}</td><td className="num">{v.clicks}</td><td className="num">{v.visitors}</td></tr>)}</tbody></table>
        )}
      </section>
      <section className="panel">
        <h2>Per plaat</h2>
        {summary.plates.length === 0 ? <p className="lead">Nog geen gegevens in deze periode.</p> : (
          <table><thead><tr><th>Plaat</th><th className="num">Lijst bekeken</th><th className="num">Doorkliks</th><th className="num">Klikratio</th></tr></thead>
            <tbody>{summary.plates.map((p) => <tr key={p.plate}><td>{p.plate}</td><td className="num">{p.materialsViews}</td><td className="num">{p.productClicks}</td><td className="num">{pct(p.clickRate)}</td></tr>)}</tbody></table>
        )}
        <p className="lead">Bezoekers zijn per dag uniek geteld (het zout wisselt dagelijks), dus over meerdere dagen zijn het bezoeken, geen personen.</p>
      </section>
    </>
  );
}
