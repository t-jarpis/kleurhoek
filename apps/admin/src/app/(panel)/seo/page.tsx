import { adminApi, describe } from "@/lib/api";
import { saveSeo } from "./actions";
import { SnippetFields } from "./SnippetFields";

export const metadata = { title: "Vindbaarheid" };
export const dynamic = "force-dynamic";

/**
 * Vindbaarheid (ADR 0035). Zoekmachines zien alleen www.kleurhoek.nl; dev, lokaal en de sites van organisaties
 * krijgen noindex en een robots.txt die alles afschermt. Hier staan de stand per markt en de instellingen.
 */
export default async function SeoPage({ searchParams }: { searchParams: Promise<{ melding?: string }> }) {
  const { melding } = await searchParams;
  let data;
  try {
    const [seo, me] = await Promise.all([adminApi.seo(), adminApi.me()]);
    data = { seo, canManage: me.permissions.includes("seo.manage") };
  } catch (e) { const d = describe(e); return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>; }
  const { seo, canManage } = data;
  const site = `https://${seo.indexableHost}`;
  return (
    <>
      <div>
        <h1>Vindbaarheid</h1>
        <p className="lead">Hoe Kleurhoek in zoekmachines staat: wat er in de sitemap komt, de titel en omschrijving van de voorpagina per markt, en de codes waarmee je de site bij Google en Bing aanmeldt.</p>
      </div>
      {melding && <p className="note" role="status">{melding}</p>}
      <section className="panel">
        <h2>Wie wordt er gevonden</h2>
        <div className="ui-callout">
          <p><strong>Alleen {seo.indexableHost}.</strong> De dev-omgeving, lokaal draaien en de sites van organisaties (scholen, bibliotheken, eigen domeinen) krijgen <code>noindex</code> en een robots.txt die alles afschermt. Zo komen er geen dubbele pagina&apos;s in zoekmachines en blijven sites van organisaties van hen.</p>
        </div>
        <p>Op het productieadres: <a href={`${site}/robots.txt`}>robots.txt</a> en <a href={`${site}/sitemap.xml`}>sitemap.xml</a>. Elke plaat heeft een eigen titel, omschrijving in de taal van de markt, een vaste (canonieke) URL, taalversies en gestructureerde gegevens.</p>
        <table>
          <caption className="visually-hidden">In de sitemap per markt</caption>
          <thead><tr><th>Markt</th><th>Taal</th><th className="num">Platen</th><th className="num">Thema&apos;s</th><th className="num">Adressen in de sitemap</th></tr></thead>
          <tbody>{seo.markets.map((m) => <tr key={m.market}><td>{m.market}</td><td>{m.language}</td><td className="num">{m.plates}</td><td className="num">{m.themes}</td><td className="num">{5 + m.plates + m.themes}</td></tr>)}</tbody>
        </table>
      </section>
      <form action={saveSeo} className="stack">
        <fieldset disabled={!canManage} className="stack" style={{ border: 0, padding: 0, margin: 0 }}>
          <section className="panel stack">
            <h2>Aanmelden bij zoekmachines</h2>
            <p className="lead">Plak alleen de code uit de meta-tag (wat tussen <code>content=&quot;…&quot;</code> staat). Hij komt alleen op {seo.indexableHost}.</p>
            <label className="field"><span>Google Search Console</span><input name="googleVerification" defaultValue={seo.settings.googleVerification ?? ""} maxLength={100} pattern="[A-Za-z0-9_\-]{10,100}" autoComplete="off" spellCheck={false} className="mono" /><small>Eigenschap toevoegen › HTML-tag.</small></label>
            <label className="field"><span>Bing Webmaster Tools</span><input name="bingVerification" defaultValue={seo.settings.bingVerification ?? ""} maxLength={100} pattern="[A-Za-z0-9_\-]{10,100}" autoComplete="off" spellCheck={false} className="mono" /><small>Site toevoegen › HTML-metatag (msvalidate.01).</small></label>
          </section>
          {seo.markets.map((m) => (
            <section key={m.market} className="panel stack">
              <h2>Voorpagina {m.market}</h2>
              <SnippetFields market={m.market} host={seo.indexableHost} title={seo.settings.home[m.market]?.title ?? null} description={seo.settings.home[m.market]?.description ?? null} />
            </section>
          ))}
          {canManage && <div><button className="ui-btn" data-variant="primary" type="submit">Opslaan</button></div>}
        </fieldset>
      </form>
    </>
  );
}
