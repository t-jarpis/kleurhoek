import Link from "next/link";
import { adminApi, describe, type SocialOverview, type SocialPost, type SocialStatus } from "@/lib/api";
import { channel, connect, decide, generate, markShared, saveSettings, saveText } from "./actions";
import { ShareButtons } from "./ShareButtons";

export const metadata = { title: "Social" };
export const dynamic = "force-dynamic";

/**
 * Social (ADR 0063). Het systeem maakt elke dag voorstellen voor Pinterest, Facebook en Instagram, en teksten om zelf
 * te delen in groepen en WhatsApp. Niets wordt geplaatst zonder goedkeuring. Elke ochtend komt er een mail.
 */
const TABS = [["voorstellen", "Ter goedkeuring"], ["gepland", "Gepland"], ["delen", "Om te delen"], ["geplaatst", "Geplaatst"], ["kanalen", "Kanalen"], ["instellingen", "Instellingen"]] as const;
type Tab = (typeof TABS)[number][0];
const CHANNEL: Record<string, string> = { pinterest: "Pinterest", facebook: "Facebook", instagram: "Instagram", delen: "Om te delen" };
const SOURCE: Record<string, string> = { plaat: "Plaat", feestdag: "Feestdag", aftelkalender: "Aftelkalender", lespakket: "Lespakket", knutselen: "Knutselen" };
const DAYS = [[1, "ma"], [2, "di"], [3, "wo"], [4, "do"], [5, "vr"], [6, "za"], [7, "zo"]] as const;
const when = (iso: string) => new Intl.DateTimeFormat("nl-NL", { weekday: "short", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit", timeZone: "Europe/Amsterdam" }).format(new Date(iso));
const STATUS_FOR: Record<Tab, SocialStatus[]> = { voorstellen: ["voorstel"], gepland: ["goedgekeurd", "mislukt"], delen: ["voorstel", "goedgekeurd"], geplaatst: ["geplaatst"], kanalen: [], instellingen: [] };

function Post({ p, tab, canManage }: { p: SocialPost; tab: Tab; canManage: boolean }) {
  return (
    <li className="ui-post" data-channel={p.channel}>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={p.image} alt="" loading="lazy" />
      <div>
        <div className="ui-post-head">
          <span className="ui-badge" data-tone={p.status === "mislukt" ? "danger" : p.status === "geplaatst" ? "success" : undefined}>{CHANNEL[p.channel]}</span>
          <span>{p.status === "geplaatst" && p.publishedAt ? `geplaatst ${when(p.publishedAt)}` : when(p.scheduledAt)}</span>
          <span>· {SOURCE[p.source] ?? p.source}{p.board ? ` · ${p.board}` : ""}</span>
        </div>
        <h3>{p.title}</h3>
        <p>{p.body.length > 220 && tab !== "delen" ? `${p.body.slice(0, 220)}…` : p.body}</p>
        {p.error && <p className="ui-post-error">Mislukt ({p.attempts}×): {p.error}</p>}
        {canManage && p.status !== "geplaatst" && (
          <details>
            <summary>Tekst aanpassen</summary>
            <form action={saveText}>
              <input type="hidden" name="id" value={p.id} /><input type="hidden" name="tab" value={tab} />
              <textarea className="ui-textarea" name="body" defaultValue={p.body} rows={6} maxLength={p.channel === "pinterest" ? 500 : 2200} aria-label="Tekst" />
              <button className="ui-btn">Opslaan</button>
            </form>
          </details>
        )}
      </div>
      <div className="ui-post-actions">
        {canManage && p.status !== "geplaatst" && p.channel !== "delen" && (
          <form action={decide}>
            <input type="hidden" name="id" value={p.id} /><input type="hidden" name="tab" value={tab} />
            {p.status !== "goedgekeurd" && <button className="ui-btn" data-variant="primary" name="approve" value="1">{p.status === "mislukt" ? "Opnieuw proberen" : "Goedkeuren"}</button>}
            <button className="ui-btn" data-variant="quiet" name="approve" value="0">{p.status === "goedgekeurd" ? "Toch niet" : "Afwijzen"}</button>
          </form>
        )}
        {p.channel === "delen" && p.status !== "geplaatst" && (
          <>
            <ShareButtons text={p.body} title={p.title} />
            {canManage && <form action={markShared}><input type="hidden" name="id" value={p.id} /><button className="ui-btn" data-variant="primary">Gedeeld</button></form>}
            {canManage && <form action={decide}><input type="hidden" name="id" value={p.id} /><input type="hidden" name="tab" value={tab} /><button className="ui-btn" data-variant="quiet" name="approve" value="0">Overslaan</button></form>}
          </>
        )}
        {p.externalUrl && <a className="ui-btn" href={p.externalUrl} target="_blank" rel="noopener noreferrer">Bekijken</a>}
        <a className="ui-btn" data-variant="quiet" href={p.link} target="_blank" rel="noopener noreferrer">Pagina</a>
      </div>
    </li>
  );
}

function Channels({ o, canManage }: { o: SocialOverview; canManage: boolean }) {
  const ch = (k: string) => o.channels.find((c) => c.kind === k)!;
  const metaReady = ch("facebook").available;
  const card = (k: "pinterest" | "facebook" | "instagram") => {
    const c = ch(k);
    return (
      <div className="ui-channel" key={k}>
        <h3>{CHANNEL[k]} <span className="ui-badge" data-tone={!c.available ? "warning" : c.connected ? "success" : undefined}>{!c.available ? "Niet ingesteld" : c.connected ? (c.enabled ? "Gekoppeld" : "Gekoppeld, uit") : "Niet gekoppeld"}</span></h3>
        <p>{c.connected ? `${c.account ?? ""}${c.connectedAt ? ` · sinds ${new Intl.DateTimeFormat("nl-NL", { day: "numeric", month: "short" }).format(new Date(c.connectedAt))}` : ""}` : !c.available ? "De app-sleutels ontbreken nog (zie hieronder)." : k === "instagram" ? "Koppelt mee met Facebook, als het Instagram-account aan de pagina hangt." : "Nog niet gekoppeld."}</p>
        {canManage && c.available && (
          <div className="ui-post-actions">
            {k !== "instagram" && (
              <form action={connect}><input type="hidden" name="kind" value={k === "pinterest" ? "pinterest" : "meta"} /><input type="hidden" name="redirectBase" value={o.redirectBase} /><button className="ui-btn" data-variant="primary">{c.connected ? "Opnieuw koppelen" : "Koppelen"}</button></form>
            )}
            {c.connected && <form action={channel}><input type="hidden" name="kind" value={k} /><button className="ui-btn" name="action" value={c.enabled ? "uit" : "aan"}>{c.enabled ? "Uitzetten" : "Aanzetten"}</button></form>}
            {c.connected && <form action={channel}><input type="hidden" name="kind" value={k} /><button className="ui-btn" data-variant="quiet" name="action" value="ontkoppelen">Ontkoppelen</button></form>}
          </div>
        )}
      </div>
    );
  };
  return (
    <>
      <div className="ui-channels">{card("pinterest")}{card("facebook")}{card("instagram")}</div>
      {(!ch("pinterest").available || !metaReady) && (
        <section className="panel stack">
          <h2>Zo stel je de kanalen in</h2>
          <p>Koppelen gaat via de officiële inlogpagina van Pinterest en Meta; Kleurhoek krijgt nooit je wachtwoord. Eenmalig maak je per platform een app aan:</p>
          <ol>
            {!ch("pinterest").available && <li><strong>Pinterest:</strong> maak een zakelijk account voor Kleurhoek, en op developers.pinterest.com een app. Zet als terugkeeradres <code>{o.redirectBase}/pinterest</code>. Vraag daarna „Standard access” aan; tot die tijd zijn pins alleen voor jezelf zichtbaar.</li>}
            {!metaReady && <li><strong>Facebook en Instagram:</strong> maak een Facebook-pagina voor Kleurhoek en koppel een zakelijk Instagram-account aan die pagina. Maak op developers.facebook.com een app (type Business) met Facebook Login, en zet als terugkeeradres <code>{o.redirectBase}/meta</code>. Zet de app op Live; omdat je zelf beheerder van de app bent, is geen keuring door Meta nodig voor je eigen pagina.</li>}
            <li>Zet de app-ID’s en -geheimen in <code>infra/envs/prod/terraform.tfvars</code> (blok <code>social</code>) en draai <code>scripts/infra.sh up prod</code>. Daarna verschijnt hier de knop Koppelen.</li>
          </ol>
        </section>
      )}
    </>
  );
}

function Settings({ o, canManage }: { o: SocialOverview; canManage: boolean }) {
  const s = o.settings;
  return (
    <form className="panel stack" action={saveSettings}>
      <label className="ui-field"><span>Mail met voorstellen naar</span><input className="ui-input" type="email" name="notifyEmail" defaultValue={s.notifyEmail ?? ""} placeholder="jij@voorbeeld.nl" disabled={!canManage} /><span className="ui-hint">Elke ochtend om 7 uur, alleen als er iets goed te keuren is.</span></label>
      <label className="ui-field"><span>Nieuwe pins per dag</span><input className="ui-input" type="number" name="pinsPerDay" min={0} max={10} defaultValue={s.pinsPerDay} disabled={!canManage} /></label>
      <fieldset className="ui-field"><legend>Dagen met een post op Facebook en Instagram</legend>
        <div className="ui-post-actions">{DAYS.map(([n, l]) => <label key={n} className="ui-check"><input type="checkbox" name="feedDays" value={n} defaultChecked={s.feedDays.includes(n)} disabled={!canManage} /> {l}</label>)}</div>
      </fieldset>
      <label className="ui-field"><span>Tijdstip van die post</span><input className="ui-input" type="time" name="feedTime" defaultValue={s.feedTime} disabled={!canManage} /></label>
      {canManage && <div><button className="ui-btn" data-variant="primary">Opslaan</button></div>}
    </form>
  );
}

export default async function SocialPage({ searchParams }: { searchParams: Promise<{ tab?: string; melding?: string }> }) {
  const sp = await searchParams;
  const tab: Tab = (TABS.find(([k]) => k === sp.tab)?.[0]) ?? "voorstellen";
  let data;
  try {
    const [o, me] = await Promise.all([adminApi.social(), adminApi.me()]);
    const list = STATUS_FOR[tab].length ? await adminApi.socialPosts(STATUS_FOR[tab], tab === "delen" ? "delen" : undefined) : [];
    data = { o, canManage: me.permissions.includes("social.manage"), list: tab === "delen" ? list : list.filter((p) => p.channel !== "delen") };
  } catch (e) { const d = describe(e); return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>; }
  const { o, canManage, list } = data;
  const count = (status: SocialStatus, channel?: string) => o.counts.filter((c) => c.status === status && (channel ? c.channel === channel : c.channel !== "delen")).reduce((n, c) => n + c.n, 0);
  const label = (k: Tab, l: string) => {
    const n = k === "voorstellen" ? count("voorstel") : k === "delen" ? count("voorstel", "delen") + count("goedgekeurd", "delen") : k === "gepland" ? count("mislukt") : 0;
    return n ? `${l} (${n})` : l;
  };
  const none = !o.channels.some((c) => c.connected);
  return (
    <>
      <div>
        <h1>Social</h1>
        <p className="lead">Elke dag maakt Kleurhoek voorstellen voor Pinterest, Facebook en Instagram, en een tekst om zelf te delen in groepen en WhatsApp. Niets wordt geplaatst zonder jouw akkoord; goedgekeurde posts gaan op het geplande moment vanzelf online.</p>
      </div>
      <nav className="tabs" aria-label="Social">
        {TABS.map(([k, l]) => <Link key={k} aria-current={tab === k ? "page" : undefined} href={`/social?tab=${k}`}>{label(k, l)}</Link>)}
      </nav>
      {sp.melding && <p className="note" role="status">{sp.melding}</p>}
      {none && tab !== "kanalen" && <div className="ui-callout"><p>Nog geen kanaal gekoppeld. Tot die tijd komen er alleen teksten om zelf te delen. <Link href="/social?tab=kanalen">Kanalen koppelen</Link></p></div>}
      {tab === "kanalen" ? <Channels o={o} canManage={canManage} /> : tab === "instellingen" ? <Settings o={o} canManage={canManage} /> : (
        <>
          {canManage && (tab === "voorstellen" || tab === "delen") && (
            <div className="toolbar">
              {tab === "voorstellen" && list.length > 1 && (
                <form action={decide}>{list.map((p) => <input key={p.id} type="hidden" name="id" value={p.id} />)}<input type="hidden" name="tab" value={tab} /><button className="ui-btn" data-variant="primary" name="approve" value="1">Alles goedkeuren ({list.length})</button></form>
              )}
              <form action={generate}><button className="ui-btn">Nu voorstellen maken</button></form>
            </div>
          )}
          {list.length === 0 ? <div className="ui-empty"><p>{tab === "voorstellen" ? "Niets om goed te keuren. Elke ochtend komen er nieuwe voorstellen." : tab === "delen" ? "Geen teksten om te delen." : tab === "gepland" ? "Niets gepland." : "Nog niets geplaatst."}</p></div>
            : <ul className="ui-posts">{list.map((p) => <Post key={p.id} p={p} tab={tab} canManage={canManage} />)}</ul>}
        </>
      )}
    </>
  );
}
