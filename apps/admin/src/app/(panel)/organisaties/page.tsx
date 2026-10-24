import Link from "next/link";
import { adminApi, describe } from "@/lib/api";
import { KIND_LABEL } from "./labels";
import { NewOrgForm } from "./NewOrgForm";

export const dynamic = "force-dynamic";
export const metadata = { title: "Organisaties" };

export default async function Organizations({ searchParams }: { searchParams: Promise<{ melding?: string; fout?: string; naam?: string; code?: string; soort?: string }> }) {
  const { melding, fout, naam, code, soort } = await searchParams;
  const [me, data] = await Promise.all([adminApi.me().catch(() => null), adminApi.organizations().catch((e: unknown) => e)]);
  if (data instanceof Error) { const d = describe(data); return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>; }
  const data2 = data as Awaited<ReturnType<typeof adminApi.organizations>>;
  const { organizations } = data2;
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
        <section className="panel stack" id="nieuw">
          <h2>Nieuwe organisatie</h2>
          <NewOrgForm hostPattern={data2.hostPattern} reserved={data2.reserved} taken={organizations.map((o) => o.slug)} initial={{ name: naam ?? "", code: code ?? "", kind: soort ?? "school" }} />
        </section>
      )}
    </>
  );
}
