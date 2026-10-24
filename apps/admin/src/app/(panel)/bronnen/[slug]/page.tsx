import Link from "next/link";
import { adminApi, describe } from "@/lib/api";
import { addSource, publishTheme, updateTheme } from "../actions";
import { SourcesNav } from "../labels";
import { SourceRow } from "../SourceRow";

export const dynamic = "force-dynamic";
export const metadata = { title: "Thema" };

export default async function ThemePage({ params, searchParams }: { params: Promise<{ slug: string }>; searchParams: Promise<{ melding?: string; fout?: string }> }) {
  const [{ slug }, q] = await Promise.all([params, searchParams]);
  let theme, me, shop;
  try { [theme, me] = await Promise.all([adminApi.theme(slug), adminApi.me()]); } catch (e) { const d = describe(e); return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>; }
  if (me.permissions.includes("shop.read")) shop = await adminApi.products().catch(() => null);
  const canManage = me.permissions.includes("sources.manage");
  const published = theme.status === "published";
  return (
    <>
      <div className="row-between">
        <div>
          <p className="lead"><Link href="/bronnen">← Bronnengids</Link></p>
          <h1>{theme.name ?? theme.slug}</h1>
          <p className="lead">{theme.makerName} · <a href={theme.makerUrl} target="_blank" rel="noopener noreferrer">{theme.makerUrl}</a> · {theme.counts.live} van {theme.counts.total} links online</p>
        </div>
        <SourcesNav active="themas" />
      </div>
      {q.melding && <p className="note" role="status">{q.melding}</p>}
      {q.fout && <div className="err" role="alert"><p>{q.fout}</p></div>}

      <section className="panel stack">
        <div className="row-between">
          <h2>Op de website</h2>
          <span className={`pill ${published ? "on" : "off"}`}>{published ? "Online" : "Concept"}</span>
        </div>
        <p className="lead">Online betekent: zichtbaar onder Thema&apos;s bij de maker, met alleen de goedgekeurde links die werken. Zonder werkende link verdwijnt het thema vanzelf.</p>
        {canManage && (
          <form action={publishTheme} className="inline">
            <input type="hidden" name="slug" value={theme.slug} />
            <input type="hidden" name="status" value={published ? "draft" : "published"} />
            <button type="submit" className={published ? "ghost" : ""}>{published ? "Offline halen" : "Online zetten"}</button>
          </form>
        )}
      </section>

      <h2>Links naar de maker</h2>
      {theme.sources.length === 0 && <p className="lead">Nog geen links.</p>}
      {theme.sources.map((s) => <SourceRow key={s.id} s={s} canManage={canManage} />)}

      {canManage && (
        <section className="panel stack">
          <h2>Link toevoegen</h2>
          <p className="lead">Alleen pagina&apos;s van de maker of rechthebbende zelf (bijvoorbeeld de downloadpagina van het pretpark), nooit sites die tekeningen van anderen overnemen. We controleren de link meteen en volgen robots.txt.</p>
          <form action={addSource} className="grid-form">
            <input type="hidden" name="theme" value={theme.slug} />
            <label className="field wide"><span>Adres (https)</span><input name="url" type="url" required placeholder="https://www.maker.nl/kleurplaten" /></label>
            <label className="field"><span>Eigen titel</span><input name="title" required minLength={2} maxLength={120} placeholder="Kleurplaten van het pretpark" /></label>
            <label className="field"><span>Basis</span>
              <select name="basis" defaultValue="link"><option value="link">Alleen een link</option><option value="license">Licentie van de maker</option></select>
            </label>
            <label className="field"><span>Datum toestemming (bij licentie)</span><input name="licenseDate" type="date" /></label>
            <label className="field wide"><span>Beschrijving (eigen tekst, mag leeg)</span><textarea name="description" maxLength={400} rows={2} /></label>
            <label className="field wide"><span>Licentie: wat mag, en waar staat de toestemming (bij licentie verplicht)</span><textarea name="licenseNote" maxLength={1000} rows={2} /></label>
            <div><button type="submit">Toevoegen en controleren</button></div>
          </form>
        </section>
      )}

      {canManage && (
        <section className="panel stack">
          <h2>Thema bewerken</h2>
          <form action={updateTheme} className="grid-form">
            <input type="hidden" name="slug" value={theme.slug} />
            <label className="field"><span>Naam</span><input name="name" required minLength={2} maxLength={80} defaultValue={theme.name ?? ""} /></label>
            <label className="field"><span>Maker</span><input name="makerName" required minLength={2} maxLength={80} defaultValue={theme.makerName} /></label>
            <label className="field"><span>Website van de maker</span><input name="makerUrl" type="url" required defaultValue={theme.makerUrl} /></label>
            <label className="field wide"><span>Beschrijving (eigen tekst)</span><textarea name="description" required minLength={10} maxLength={600} rows={3} defaultValue={theme.description ?? ""} /></label>
            {shop && (
              <fieldset className="field wide">
                <legend>Producten bij dit thema (partnerlinks, hooguit 12)</legend>
                {shop.products.length === 0 ? <small>Nog geen producten in de winkel.</small> : (
                  <div className="checks">
                    {shop.products.map((p) => (
                      <label key={p.slug} className="check"><input type="checkbox" name="products" value={p.slug} defaultChecked={theme.productSlugs.includes(p.slug)} /> {p.name ?? p.slug}{p.enabled ? "" : " (uit)"}</label>
                    ))}
                  </div>
                )}
                <small>Echte producten van het thema (een knuffel, puzzel of kleurboek) mogen; geen logo&apos;s of beeld van de maker op onze pagina.</small>
              </fieldset>
            )}
            <div><button type="submit">Opslaan</button></div>
          </form>
        </section>
      )}
    </>
  );
}
