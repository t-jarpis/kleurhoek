import { adminApi, describe } from "@/lib/api";
import { ShopNav } from "../nav";
import { SalesImport } from "./SalesImport";

export const metadata = { title: "Verkopen · Winkel" };
export const dynamic = "force-dynamic";

/** Rapporten van partners inlezen (ADR 0033): de basis voor opbrengst per klik op Overzicht. */
export default async function Sales() {
  const iso = (d: Date) => d.toISOString().slice(0, 10);
  let data;
  try {
    const [catalog, report] = await Promise.all([adminApi.products(), adminApi.salesReport(iso(new Date(Date.now() - 365 * 86_400_000)), iso(new Date()))]);
    data = { catalog, report };
  } catch (e) { const d = describe(e); return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>; }
  const { catalog, report } = data;
  const name = (slug: string) => catalog.partners.find((p) => p.slug === slug)?.name ?? slug;
  const partners = catalog.partners.filter((p) => p.slug !== "direct").map((p) => ({ slug: p.slug, name: p.name }));
  return (
    <>
      <div>
        <h1>Verkopen</h1>
        <p className="lead">Lees het rapport uit je partneraccount in (bol, Amazon of een netwerk), zodat je per partner ziet wat een doorklik oplevert. Exporteer daar een CSV met per verkoop de datum, het kenmerk of de tracking-ID, het product en de commissie.</p>
      </div>
      <div className="toolbar"><ShopNav active="verkopen" /></div>
      <section className="panel"><h2>Rapport inlezen</h2><SalesImport partners={partners} /></section>
      <section className="panel">
        <h2>Ingelezen rapporten</h2>
        {report.imports.length === 0 ? <p className="lead">Nog geen rapporten.</p> : (
          <table><thead><tr><th>Partner</th><th>Bestand</th><th>Periode</th><th className="num">Rijen</th><th>Ingelezen</th></tr></thead>
            <tbody>{report.imports.map((i) => <tr key={i.id}><td>{name(i.partner)}</td><td>{i.fileName}</td><td>{i.from} t/m {i.to}</td><td className="num">{i.rows}</td><td>{new Date(i.at).toLocaleString("nl-NL", { dateStyle: "medium", timeStyle: "short" })}</td></tr>)}</tbody></table>
        )}
      </section>
    </>
  );
}
