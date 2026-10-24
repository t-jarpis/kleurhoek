import Link from "next/link";
import { notFound } from "next/navigation";
import { adminApi, ApiError, describe } from "@/lib/api";
import { KIND_LABEL } from "../labels";
import { addManager, deleteOrganization, removeLogo, removeManager, saveGeneral, saveOffer } from "./actions";
import { LogoUpload } from "./LogoUpload";
import { BrandEditor } from "./BrandEditor";
import { CopyButton } from "@/components/CopyButton";

export const dynamic = "force-dynamic";

const TABS = [["algemeen", "Algemeen"], ["huisstijl", "Huisstijl"], ["aanbod", "Aanbod"], ["beheerders", "Beheerders"]] as const;
type Tab = (typeof TABS)[number][0];

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  return { title: `Organisatie ${(await params).slug}` };
}

export default async function OrganizationPage({ params, searchParams }: {
  params: Promise<{ slug: string }>; searchParams: Promise<{ tab?: string; melding?: string; fout?: string }>;
}) {
  const { slug } = await params;
  const { tab: rawTab, melding, fout } = await searchParams;
  const tab: Tab = TABS.some(([t]) => t === rawTab) ? (rawTab as Tab) : "algemeen";
  const [me, data] = await Promise.all([adminApi.me().catch(() => null), adminApi.organization(slug).catch((e: unknown) => e)]);
  if (data instanceof ApiError && data.status === 404) notFound();
  if (data instanceof Error) { const d = describe(data); return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>; }
  const org = data as Awaited<ReturnType<typeof adminApi.organization>>;
  const canManage = me?.permissions.includes("organizations.manage") ?? false;
  const logo = org.brand.logoVersion ? `/merk/${org.slug}/${org.brand.logoVersion}` : null;
  const all = <T,>(chosen: T[] | null, value: T) => chosen === null || chosen.includes(value);
  const managers = tab === "beheerders" && !org.isDefault ? await adminApi.orgManagers(org.slug).catch(() => []) : [];

  return (
    <>
      <div className="stack">
        <p className="lead"><Link href="/organisaties">Organisaties</Link></p>
        <div className="row-between">
          <h1>{org.name}</h1>
          <span className={`pill ${org.active ? "on" : "off"}`}>{org.active ? "Actief" : "Uit"}</span>
        </div>
        <p className="lead">{KIND_LABEL[org.kind]} · code <code>{org.slug}</code> · laatst gewijzigd door {org.updatedBy}</p>
        <nav className="tabs" aria-label="Onderdelen">
          {TABS.filter(([t]) => t !== "beheerders" || !org.isDefault).map(([t, label]) => <Link key={t} href={`/organisaties/${org.slug}?tab=${t}`} aria-current={tab === t ? "page" : undefined}>{label}</Link>)}
        </nav>
      </div>
      {melding && <p className="note" role="status">{melding}</p>}
      {fout && <div className="err" role="alert"><p>{fout}</p></div>}

      {tab === "algemeen" && (
        <section className="panel stack">
          <h2>Algemeen</h2>
          <form action={saveGeneral} className="stack">
            <input type="hidden" name="slug" value={org.slug} />
            <fieldset disabled={!canManage} className="stack" style={{ border: 0, padding: 0, margin: 0 }}>
              <label className="field"><span>Naam</span><input name="name" defaultValue={org.name} required minLength={2} maxLength={80} /><small>Staat in de titel van de site en in mails.</small></label>
              {!org.isDefault && (
                <>
                  <label className="field"><span>Soort</span>
                    <select name="kind" defaultValue={org.kind}>
                      {(["school", "opvang", "vereniging", "bedrijf", "overig"] as const).map((k) => <option key={k} value={k}>{KIND_LABEL[k]}</option>)}
                    </select>
                  </label>
                  <div className="field">
                    <span>Adres</span>
                    {org.subdomain ? <p className="lead">Altijd bereikbaar op{" "}<span className="ui-copy"><a href={`https://${org.subdomain}`} target="_blank" rel="noopener noreferrer"><code id="org-adres">{org.subdomain}</code></a><CopyButton value={`https://${org.subdomain}`} label="Kopieer adres" targetId="org-adres" /></span></p> : <p className="lead">Subdomeinen zijn in deze omgeving niet ingesteld (ORG_HOST_PATTERN).</p>}
                  </div>
                  <label className="field"><span>Eigen domeinen</span>
                    <textarea name="hosts" defaultValue={org.hosts.join("\n")} rows={3} className="mono" spellCheck={false} placeholder="kleuren.deregenboog.nl" />
                    <small>Eén per regel. Het domein moet ook in Cloudflare naar Kleurhoek wijzen (zie infra/README).</small>
                  </label>
                  <input type="hidden" name="active-field" value="1" />
                  <label className="check"><input type="checkbox" name="active" defaultChecked={org.active} /> Actief: de site van deze organisatie is bereikbaar</label>
                </>
              )}
              {org.isDefault && <p className="lead">Dit is Kleurhoek zelf: alle adressen die niet bij een andere organisatie horen. Staat altijd aan.</p>}
              <div><button type="submit">Opslaan</button></div>
            </fieldset>
          </form>
        </section>
      )}

      {tab === "algemeen" && canManage && !org.isDefault && (
        <section className="panel stack">
          <h2>Organisatie verwijderen</h2>
          <p className="lead">De site op {org.subdomain ?? "het subdomein"} verdwijnt meteen, met huisstijl, logo en aanbod. De code komt weer vrij. Bezoekcijfers blijven bewaard. Dit kan niet ongedaan worden gemaakt.</p>
          <form action={deleteOrganization} className="grid-form">
            <input type="hidden" name="slug" value={org.slug} />
            <label className="field"><span>Typ <code>{org.slug}</code> om te bevestigen</span><input name="confirm" required autoComplete="off" autoCapitalize="none" spellCheck={false} className="mono" /></label>
            <div><button type="submit" className="danger">Verwijderen</button></div>
          </form>
        </section>
      )}

      {tab === "huisstijl" && (
        <>
          <section className="panel stack">
            <h2>Huisstijl</h2>
            <BrandEditor org={org} themes={org.themes} fonts={org.fonts} logo={logo} canManage={canManage} />
          </section>
          <section className="panel stack">
            <h2>Logo</h2>
            <div className="ui-upload">
              <div className="ui-upload-preview">{logo ? <img src={logo} alt={`Logo van ${org.name}`} /> : "Geen logo, het woordmerk wordt gebruikt"}</div>
              <div className="ui-upload-body">
                <span className="ui-hint">PNG, WebP, JPEG of SVG, maximaal 256 kB. Liefst liggend, met transparante achtergrond, zodat het op licht en donker werkt.</span>
                {canManage && (
                  <div className="ui-brandpreview-row">
                    <LogoUpload slug={org.slug} />
                    {logo && <form action={removeLogo}><input type="hidden" name="slug" value={org.slug} /><button type="submit" className="ghost">Verwijder</button></form>}
                  </div>
                )}
              </div>
            </div>
          </section>
        </>
      )}

      {tab === "aanbod" && (
        <section className="panel stack">
          <h2>Aanbod</h2>
          <p className="lead">Wat deze organisatie laat zien. Alles aangevinkt betekent ook alles wat er later bij komt.</p>
          <form action={saveOffer} className="stack">
            <input type="hidden" name="slug" value={org.slug} />
            <fieldset disabled={!canManage} className="stack" style={{ border: 0, padding: 0, margin: 0 }}>
              <fieldset className="field"><legend>Onderwerpen</legend><div className="checks">
                {org.options.categories.map((c) => <label key={c.slug} className="check"><input type="checkbox" name="categories" value={c.slug} defaultChecked={all(org.offer.categories, c.slug)} /> {c.name}</label>)}
              </div></fieldset>
              <fieldset className="field"><legend>Leeftijden</legend><div className="checks">
                {org.options.ages.map((a) => <label key={a.slug} className="check"><input type="checkbox" name="ages" value={a.slug} defaultChecked={all(org.offer.ages, a.slug)} /> {a.name}</label>)}
              </div></fieldset>
              <fieldset className="field"><legend>Soort platen</legend><div className="checks">
                {org.options.kinds.map((k) => <label key={k.slug} className="check"><input type="checkbox" name="kinds" value={k.slug} defaultChecked={all(org.offer.kinds, k.slug)} /> {k.name}</label>)}
              </div></fieldset>
              <fieldset className="field"><legend>Leerdoelen</legend><div className="checks">
                {org.options.goals.map((g) => <label key={g.slug} className="check"><input type="checkbox" name="goals" value={g.slug} defaultChecked={all(org.offer.goals, g.slug)} /> {g.name}</label>)}
              </div><small>Alleen platen met minstens één aangevinkt leerdoel. De leerdoelen volgen uit soort, onderwerp en naam van de plaat.</small></fieldset>
              <fieldset className="field"><legend>Collecties</legend>
                {org.options.collections.length === 0 ? <p className="lead">Nog geen collecties. Maak ze bij <Link href="/collecties">Collecties</Link>.</p> : (
                  <div className="checks">
                    {org.options.collections.map((c) => <label key={c.slug} className="check"><input type="checkbox" name="collections" value={c.slug} defaultChecked={org.offer.collections?.includes(c.slug) ?? false} /> {c.name} ({c.plates} platen)</label>)}
                  </div>
                )}
                <small>Niets aangevinkt: alle platen. Wel iets aangevinkt: alleen platen uit die collecties.</small>
              </fieldset>
              <label className="field"><span>Uitgezette platen</span>
                <textarea name="excluded" defaultValue={org.offer.excluded.join("\n")} rows={3} className="mono" spellCheck={false} placeholder="code-van-een-plaat" />
                <small>Eén code per regel. Beheerders van de organisatie zetten platen ook zelf uit op hun site (pagina Beheer).</small>
              </label>
              <fieldset className="field"><legend>Markten</legend><div className="checks">
                {org.options.markets.map((m) => <label key={m} className="check"><input type="checkbox" name="markets" value={m} defaultChecked={all(org.offer.markets, m)} /> <code>{m}</code></label>)}
              </div></fieldset>
              <fieldset className="field"><legend>Functies</legend><div className="checks">
                <label className="check"><input type="checkbox" name="shop" defaultChecked={org.features.shop} /> Webshop en partnerlinks</label>
                <label className="check"><input type="checkbox" name="accounts" defaultChecked={org.features.accounts} /> Inloggen voor ouders</label>
                <label className="check"><input type="checkbox" name="learningFilters" defaultChecked={org.features.learningFilters} /> Filter Leerdoel op de site</label>
              </div><small>Zonder webshop verdwijnen materiaallinks en producten van de site van deze organisatie.</small></fieldset>
              <div><button type="submit">Aanbod opslaan</button></div>
            </fieldset>
          </form>
        </section>
      )}

      {tab === "beheerders" && !org.isDefault && (
        <section className="panel stack">
          <h2>Beheerders</h2>
          <p className="lead">Iemand van de organisatie (bijvoorbeeld een leerkracht of bibliothecaris) die op de eigen site leerdoelen, collecties en losse platen kiest, via Beheer onderaan de site. Dat is een gewoon account op de site, geen beheeraccount: de persoon logt eerst één keer in op {org.subdomain ?? "de site"} en jij voegt hem daarna hier toe.</p>
          {managers.length === 0 ? <p className="lead">Nog geen beheerders.</p> : (
            <table>
              <thead><tr><th>Naam</th><th>E-mailadres</th><th>Sinds</th><th><span className="visually-hidden">Actie</span></th></tr></thead>
              <tbody>{managers.map((m) => (
                <tr key={m.userId}><td>{m.displayName ?? "—"}</td><td>{m.email ?? "—"}</td><td>{new Date(m.since).toLocaleDateString("nl-NL", { dateStyle: "medium" })}</td>
                  <td>{canManage && <form action={removeManager}><input type="hidden" name="slug" value={org.slug} /><input type="hidden" name="userId" value={m.userId} /><button type="submit" className="ghost">Weghalen<span className="visually-hidden"> {m.displayName ?? m.email}</span></button></form>}</td></tr>
              ))}</tbody>
            </table>
          )}
          {canManage && (
            <form action={addManager} className="grid-form">
              <input type="hidden" name="slug" value={org.slug} />
              <label className="field"><span>E-mailadres</span><input name="email" type="email" required maxLength={254} autoComplete="off" /></label>
              <div><button type="submit">Beheerder toevoegen</button></div>
            </form>
          )}
        </section>
      )}
    </>
  );
}
