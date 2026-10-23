import Link from "next/link";
import { adminApi, describe } from "@/lib/api";
import { createOrganization } from "./actions";
import { KIND_LABEL } from "./labels";

export const dynamic = "force-dynamic";
export const metadata = { title: "Organisaties" };

export default async function Organizations({ searchParams }: { searchParams: Promise<{ melding?: string; fout?: string }> }) {
  const { melding, fout } = await searchParams;
  const [me, data] = await Promise.all([adminApi.me().catch(() => null), adminApi.organizations().catch((e: unknown) => e)]);
  if (data instanceof Error) { const d = describe(data); return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>; }
  const { organizations } = data as Awaited<ReturnType<typeof adminApi.organizations>>;
  const canManage = me?.permissions.includes("organizations.manage") ?? false;
  return (
    <>
      <div>
        <h1>Organisaties</h1>
        <p className="lead">Kleurhoek zelf en organisaties met een eigen versie van de site, zoals scholen en kinderopvang: eigen naam, logo en kleuren, eigen (sub)domein en eigen aanbod. De platen blijven van Kleurhoek.</p>
      </div>
      {melding && <p className="note" role="status">{melding}</p>}
      {fout && <div className="err" role="alert"><p>{fout}</p></div>}

      <section className="panel">
        <table>
          <thead><tr><th>Naam</th><th>Soort</th><th>Adres</th><th>Webshop</th><th>Status</th></tr></thead>
          <tbody>
            {organizations.map((o) => (
              <tr key={o.slug}>
                <td><Link href={`/organisaties/${o.slug}`}><b>{o.name}</b></Link><div className="lead"><code>{o.slug}</code></div></td>
                <td>{KIND_LABEL[o.kind]}</td>
                <td className="lead">{o.isDefault ? "Standaard (alle andere adressen)" : [o.subdomain, ...o.hosts].filter(Boolean).join(", ") || "—"}</td>
                <td>{o.features.shop ? "Aan" : "Uit"}</td>
                <td><span className={`pill ${o.active ? "on" : "off"}`}>{o.active ? "Actief" : "Uit"}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {canManage && (
        <section className="panel stack">
          <h2>Nieuwe organisatie</h2>
          <form action={createOrganization} className="grid-form">
            <label className="field"><span>Naam</span><input name="name" required minLength={2} maxLength={80} placeholder="Basisschool De Regenboog" /></label>
            <label className="field"><span>Code</span><input name="slug" required maxLength={32} pattern="[a-z0-9][a-z0-9\-]{0,30}[a-z0-9]" className="mono" placeholder="de-regenboog" aria-describedby="code-hint" /></label>
            <label className="field"><span>Soort</span>
              <select name="kind" defaultValue="school">
                {(["school", "opvang", "vereniging", "bedrijf", "overig"] as const).map((k) => <option key={k} value={k}>{KIND_LABEL[k]}</option>)}
              </select>
            </label>
            <small id="code-hint" className="lead wide">De code wordt het subdomein (bijvoorbeeld <code>de-regenboog.kleurhoek.nl</code>) en is later niet te wijzigen. Een nieuwe organisatie toont eerst alle platen, zonder webshop.</small>
            <div><button type="submit">Aanmaken</button></div>
          </form>
        </section>
      )}
    </>
  );
}
