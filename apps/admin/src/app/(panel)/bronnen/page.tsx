import Link from "next/link";
import { adminApi, describe } from "@/lib/api";
import { createTheme } from "./actions";
import { SourcesNav } from "./labels";

export const dynamic = "force-dynamic";
export const metadata = { title: "Bronnengids" };

/**
 * Bronnengids (ADR 0025): thema's waar mensen naar zoeken, met links naar de kleurplaten bij de maker zelf.
 * We tonen nooit beeld van de maker; alleen eigen tekst en een link.
 */
export default async function Themes({ searchParams }: { searchParams: Promise<{ melding?: string; fout?: string }> }) {
  const q = await searchParams;
  let themes, review, me;
  try { [themes, review, me] = await Promise.all([adminApi.themes(), adminApi.sourceReview(), adminApi.me()]); } catch (e) { const d = describe(e); return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>; }
  const canManage = me.permissions.includes("sources.manage");
  return (
    <>
      <div className="row-between">
        <div><h1>Bronnengids</h1><p className="lead">Links naar gratis kleurplaten bij de makers zelf. Alleen officiële bronnen; eerst controleren en goedkeuren, daarna houdt de dagelijkse controle ze in de gaten.</p></div>
        <SourcesNav active="themas" attention={review.length} />
      </div>
      {q.melding && <p className="note" role="status">{q.melding}</p>}
      {q.fout && <div className="err" role="alert"><p>{q.fout}</p></div>}
      <section className="panel">
        {themes.length === 0 ? <p className="lead">Nog geen thema&apos;s. Maak er hieronder een.</p> : (
          <table>
            <thead><tr><th>Thema</th><th>Maker</th><th className="num">Links online</th><th className="num">Nakijken</th><th>Status</th></tr></thead>
            <tbody>
              {themes.map((t) => (
                <tr key={t.slug}>
                  <td><Link href={`/bronnen/${t.slug}`}><b>{t.name ?? t.slug}</b></Link></td>
                  <td>{t.makerName}</td>
                  <td className="num">{t.counts.live} van {t.counts.total}</td>
                  <td className={`num ${t.counts.attention ? "bad" : ""}`}>{t.counts.attention}</td>
                  <td><span className={`pill ${t.status === "published" ? "on" : "off"}`}>{t.status === "published" ? "Online" : "Concept"}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
      {canManage && (
        <section className="panel stack">
          <h2>Nieuw thema</h2>
          <form action={createTheme} className="grid-form">
            <label className="field"><span>Naam</span><input name="name" required minLength={2} maxLength={80} placeholder="Het pretpark" /></label>
            <label className="field"><span>Code (in het adres)</span><input name="slug" required maxLength={64} className="mono" pattern="[a-z0-9-]+" placeholder="pretpark" /></label>
            <label className="field"><span>Maker</span><input name="makerName" required minLength={2} maxLength={80} placeholder="Naam van de rechthebbende" /></label>
            <label className="field wide"><span>Website van de maker</span><input name="makerUrl" type="url" required placeholder="https://www.maker.nl/" /></label>
            <label className="field wide"><span>Beschrijving (eigen tekst, geen tekst van de maker overnemen)</span><textarea name="description" required minLength={10} maxLength={600} rows={3} /></label>
            <div><button type="submit">Thema aanmaken</button></div>
          </form>
        </section>
      )}
    </>
  );
}
