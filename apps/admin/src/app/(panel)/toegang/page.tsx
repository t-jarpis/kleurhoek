import { adminApi, describe } from "@/lib/api";
import { addEntry, addMine, myIp, removeEntry, setEnabled, setLogin } from "./actions";

export const dynamic = "force-dynamic";
export const metadata = { title: "Toegang" };

export default async function Access({ searchParams }: { searchParams: Promise<{ melding?: string; fout?: string }> }) {
  const { melding, fout } = await searchParams;
  const [me, ip] = await Promise.all([adminApi.me().catch(() => null), myIp()]);
  let access;
  try { access = await adminApi.siteAccess(); } catch (e) { const d = describe(e); return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>; }
  const canManage = me?.permissions.includes("operations.access.manage") ?? false;
  return (
    <>
      <div>
        <h1>Toegang</h1>
        <p className="lead">Inloggen op de website aan- of uitzetten, en de website afschermen met een lijst IP-adressen (voor een testomgeving of vóór een lancering). Het admin panel valt hier niet onder; dat blijft achter Cloudflare Access. Wijzigingen werken binnen een minuut en komen in het auditlog.</p>
      </div>
      {melding && <p className="note" role="status">{melding}</p>}
      {fout && <div className="err" role="alert"><p>{fout}</p></div>}

      <section className="panel stack">
        <div className="row-between">
          <h2>Inloggen op de website</h2>
          {canManage
            ? <form action={setLogin}><input type="hidden" name="loginEnabled" value={String(!access.loginEnabled)} /><button type="submit" className="ui-switch" aria-pressed={access.loginEnabled}>{access.loginEnabled ? "Aan" : "Uit"}<span className="visually-hidden">: inloggen op de website</span></button></form>
            : <span className={`pill ${access.loginEnabled ? "on" : "off"}`}>{access.loginEnabled ? "Aan" : "Uit"}</span>}
        </div>
        <p className="lead">{access.loginEnabled
          ? "Ouders, leerkrachten en beheerders van scholen kunnen inloggen (als dat voor hun organisatie aanstaat)."
          : "Niemand kan op de website inloggen: de knop is weg, nieuwe logins worden geweigerd en accountfuncties zoals favorieten in je account zijn verborgen. Kleuren en printen werkt gewoon."} Het admin panel valt hier niet onder.</p>
      </section>

      <section className="panel stack">
        <div className="row-between">
          <h2>Website afschermen</h2>
          <span className={`pill ${access.enabled ? "on" : "off"}`}>{access.enabled ? "Aan" : "Uit"}</span>
        </div>
        <p className="lead">{access.enabled ? "Alleen adressen uit de lijst hieronder zien de website. Anderen krijgen een melding dat de omgeving is afgeschermd." : "De website is voor iedereen bereikbaar."} Laatst gewijzigd door {access.updatedBy}.</p>
        {canManage && (
          <form action={setEnabled}>
            <input type="hidden" name="enabled" value={String(!access.enabled)} />
            <button type="submit">{access.enabled ? "Afscherming uitzetten" : "Afscherming aanzetten"}</button>
            {!access.enabled && <span className="lead"> Je eigen adres wordt dan automatisch toegevoegd.</span>}
          </form>
        )}
      </section>

      <section className="panel stack">
        <div className="row-between">
          <h2>Toegestane adressen</h2>
          {ip && <span className="lead">Jouw adres nu: <code>{ip}</code></span>}
        </div>
        {access.entries.length === 0 ? <p className="lead">Nog geen adressen.</p> : (
          <table>
            <thead><tr><th>Adres of blok</th><th>Omschrijving</th><th>Toegevoegd</th><th /></tr></thead>
            <tbody>
              {access.entries.map((e) => (
                <tr key={e.cidr}>
                  <td><code>{e.cidr}</code></td>
                  <td>{e.label}</td>
                  <td className="lead">{new Date(e.addedAt).toLocaleDateString("nl-NL")} door {e.addedBy}</td>
                  <td>{canManage && <form action={removeEntry}><input type="hidden" name="cidr" value={e.cidr} /><button type="submit" className="ghost">Verwijderen</button></form>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        {canManage && (
          <>
            {ip && <form action={addMine}><button type="submit" className="ghost">Mijn adres toevoegen</button></form>}
            <form action={addEntry} className="grid-form">
              <label className="field"><span>IP-adres of blok</span><input name="cidr" required maxLength={64} className="mono" placeholder="203.0.113.7 of 2a02:a46:1:2::/64" /></label>
              <label className="field"><span>Omschrijving</span><input name="label" required maxLength={80} placeholder="Kantoor" /></label>
              <div><button type="submit">Toevoegen</button></div>
            </form>
            <p className="lead">Een thuisverbinding met IPv6 wisselt van adres binnen hetzelfde blok; &quot;Mijn adres toevoegen&quot; voegt daarom het hele /64-blok toe. Wisselt je IPv4-adres (na een herstart van de router), voeg het nieuwe dan opnieuw toe.</p>
          </>
        )}
      </section>
    </>
  );
}
