import { adminApi, describe } from "@/lib/api";
import { createPartner, savePartner } from "../actions";
import { ShopNav } from "../nav";

export const metadata = { title: "Koppelingen · Winkel" };

const HELP: Record<string, { label: string; text: string }> = {
  siteId: { label: "Site-ID", text: "Staat in je bol-partneraccount, bij Instellingen of in een link uit de Linkbuilder (de waarde achter s=)." },
  tag: { label: "Tracking-ID", text: "Je tracking-ID uit het partnerprogramma van deze Amazon-winkel. Elk land heeft een eigen programma en ID." },
};

/** Welke instellingen een sjabloon nodig heeft: alles tussen {} behalve url en subId. */
const placeholders = (template: string) => [...new Set([...template.matchAll(/\{([a-zA-Z]+)\}/g)].map((m) => m[1]!).filter((k) => k !== "url" && k !== "subId"))];

export default async function Partners({ searchParams }: { searchParams: Promise<{ melding?: string }> }) {
  const { melding } = await searchParams;
  let partners;
  try { partners = await adminApi.partners(); } catch (e) { const d = describe(e); return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>; }
  return (
    <>
      <div>
        <h1>Koppelingen</h1>
        <p className="lead">Hier koppel je jouw partneraccount. Zolang een partner uit staat, tonen we geen producten van die partner. Elke wijziging komt in het auditlog.</p>
      </div>
      <div className="toolbar"><ShopNav active="koppelingen" /></div>
      {melding && <p className="note" role="status">{melding}</p>}
      {partners.map((p) => {
        const keys = placeholders(p.linkTemplate);
        return (
          <section className="panel" key={p.slug}>
            <form action={savePartner} className="stack">
              <input type="hidden" name="slug" value={p.slug} />
              <div className="row-between">
                <h2>{p.name}</h2>
                <span className={`pill ${p.enabled ? "on" : "off"}`}>{p.enabled ? "Aan" : "Uit"}</span>
              </div>
              {keys.map((k) => (
                <label key={k} className="field">
                  <span>{HELP[k]?.label ?? k}</span>
                  <input name={`setting:${k}`} defaultValue={p.settings[k] ?? ""} autoComplete="off" pattern="[A-Za-z0-9_.\-]{0,64}" />
                  {HELP[k] && <small>{HELP[k].text}</small>}
                </label>
              ))}
              <label className="field">
                <span>Sjabloon voor de link</span>
                <input name="linkTemplate" defaultValue={p.linkTemplate} className="mono" />
                <small>{"{url}"} is de productpagina, {"{subId}"} de plaat waar de klik vandaan kwam (zo zie je in je partneraccount welke plaat verkoopt){keys.length ? `, ${keys.map((k) => `{${k}}`).join(", ")} komt uit de velden hierboven` : ""}.</small>
              </label>
              {p.allowedHosts.length > 0 && <p className="lead">Productpagina's alleen op: {p.allowedHosts.join(", ")}</p>}
              <label className="check"><input type="checkbox" name="enabled" defaultChecked={p.enabled} /> Producten van {p.name} tonen</label>
              <div><button type="submit">Opslaan</button> <span className="lead">Laatst gewijzigd door {p.updatedBy}</span></div>
            </form>
          </section>
        );
      })}
      <section className="panel">
        <h2>Partner toevoegen</h2>
        <p className="lead">Voor winkels met een partnerprogramma via een netwerk (bijvoorbeeld Pipoos via Daisycon, of winkels op Awin of TradeTracker). Maak in je netwerk een deeplink naar een willekeurig product, plak die hieronder en vervang de productpagina in die link door {"{url}"}. Waarden van jouw kant (zoals je site- of publisher-ID) zet je als {"{siteId}"} in het sjabloon; dan krijg je er straks een veld voor. Gebruik {"{subId}"} waar het netwerk een sub-ID of clickref verwacht, dan zie je per plaat wat er verkocht wordt.</p>
        <form action={createPartner} className="grid-form">
          <label className="field"><span>Code</span><input name="slug" required pattern="[a-z0-9\-]{2,32}" placeholder="pipoos" /></label>
          <label className="field"><span>Naam</span><input name="name" required placeholder="Pipoos" /></label>
          <label className="field"><span>Domeinen van de winkel</span><input name="allowedHosts" required placeholder="www.pipoos.com" /><small>Alleen productpagina's op deze domeinen worden geaccepteerd.</small></label>
          <label className="field wide"><span>Sjabloon voor de link</span><input name="linkTemplate" required className="mono" placeholder="https://netwerk.example/c/?id={siteId}&sub={subId}&url={url}" /></label>
          <div className="wide"><button type="submit">Toevoegen</button></div>
        </form>
      </section>
    </>
  );
}
