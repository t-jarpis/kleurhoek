import Link from "next/link";
import { adminApi, describe } from "@/lib/api";
import { CollectionEditor } from "./CollectionEditor";
import { deleteCollection } from "./actions";

export const metadata = { title: "Collecties" };
export const dynamic = "force-dynamic";

/**
 * Collecties (ADR 0036): samengestelde reeksen platen. Een school, bso of bibliotheek kan haar aanbod beperken tot
 * een of meer collecties (bij Organisaties, of zelf via Beheer op de eigen site).
 */
export default async function CollectionsPage({ searchParams }: { searchParams: Promise<{ melding?: string; bewerk?: string }> }) {
  const { melding, bewerk } = await searchParams;
  let data;
  try {
    const [list, me] = await Promise.all([adminApi.collections(), adminApi.me()]);
    data = { ...list, canManage: me.permissions.includes("catalog.manage") };
  } catch (e) { const d = describe(e); return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>; }
  const { collections, plates, goals, canManage } = data;
  const editing = bewerk === "nieuw" ? null : collections.find((c) => c.slug === bewerk) ?? undefined;
  return (
    <>
      <div>
        <h1>Collecties</h1>
        <p className="lead">Reeksen platen die bij elkaar horen, zoals &quot;Rekenen groep 3&quot; of &quot;Herfst op school&quot;. Een organisatie kan haar site beperken tot een of meer collecties.</p>
      </div>
      {melding && <p className="note" role="status">{melding}</p>}
      {bewerk !== undefined && editing !== undefined ? (
        <section className="panel stack">
          <div className="row-between"><h2>{editing ? editing.names.nl ?? editing.slug : "Nieuwe collectie"}</h2><Link href="/collecties">Terug naar de lijst</Link></div>
          <CollectionEditor collection={editing} plates={plates} goals={goals} canManage={canManage} />
        </section>
      ) : (
        <section className="panel stack">
          <div className="row-between"><h2>Alle collecties</h2>{canManage && <Link className="ui-btn" data-variant="primary" href="/collecties?bewerk=nieuw">Nieuwe collectie</Link>}</div>
          {collections.length === 0 ? <p className="lead">Nog geen collecties.</p> : (
            <table>
              <thead><tr><th>Naam</th><th>Code</th><th className="num">Platen</th><th>Talen</th><th><span className="visually-hidden">Acties</span></th></tr></thead>
              <tbody>{collections.map((c) => (
                <tr key={c.slug}>
                  <td><Link href={`/collecties?bewerk=${c.slug}`}>{c.names.nl ?? c.slug}</Link></td>
                  <td><code>{c.slug}</code></td>
                  <td className="num">{c.plates.length}</td>
                  <td>{Object.keys(c.names).join(", ")}</td>
                  <td>{canManage && <form action={deleteCollection}><input type="hidden" name="slug" value={c.slug} /><button type="submit" className="ghost">Verwijderen<span className="visually-hidden"> {c.names.nl}</span></button></form>}</td>
                </tr>
              ))}</tbody>
            </table>
          )}
        </section>
      )}
    </>
  );
}
