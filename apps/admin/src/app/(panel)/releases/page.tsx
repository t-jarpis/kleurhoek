import { adminApi, describe, type Release } from "@/lib/api";

export const dynamic = "force-dynamic";
export const metadata = { title: "Releases" };

const REPO = "https://github.com/t-jarpis/kleurhoek/commit/";
const when = (iso: string) => new Intl.DateTimeFormat("nl-NL", { dateStyle: "long", timeStyle: "short", timeZone: "Europe/Amsterdam" }).format(new Date(iso));

/** ReleaseNotes uit het design system (ADR 0023): per uitrol wat er veranderde, nieuwste bovenaan. */
export default async function Releases() {
  let data;
  try { data = await adminApi.releases(); } catch (e) { const d = describe(e); return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>; }
  const { releases } = data;

  return (
    <>
      <div>
        <h1>Releases</h1>
        <p className="lead">Wat er per uitrol veranderde in deze omgeving, nieuwste bovenaan. Een release wordt vastgelegd zodra de nieuwe versie start.</p>
      </div>
      <section className="panel">
        {releases.length === 0 ? (
          <p className="lead">Nog geen releases. Ze verschijnen hier na de eerste uitrol via GitHub; lokaal worden ze niet vastgelegd.</p>
        ) : (
          <ol className="ui-releases">{releases.map((r, i) => <Item key={`${r.sha}-${r.startedAt}`} r={r} current={i === 0} all={releases} />)}</ol>
        )}
      </section>
    </>
  );
}

function Item({ r, current, all }: { r: Release; current: boolean; all: Release[] }) {
  const plain = r.notes.filter((n) => !n.technical), technical = r.notes.filter((n) => n.technical);
  // Bij terugdraaien: de eerste keer dat deze versie draaide.
  const first = r.kind === "rollback" ? all.filter((x) => x.sha === r.sha && x.kind !== "rollback").at(-1) : undefined;
  return (
    <li className="ui-release">
      <div className="ui-release-head">
        <h3>{when(r.startedAt)}</h3>
        {current && <span className="ui-badge" data-tone="success">Huidige versie</span>}
        {r.kind === "rollback" && <span className="ui-badge" data-tone="warning">Teruggedraaid</span>}
        {r.kind === "first" && <span className="ui-badge">Eerste release</span>}
        <a href={`${REPO}${r.sha}`} target="_blank" rel="noopener noreferrer"><code>{r.sha.slice(0, 7)}</code><span className="visually-hidden"> (opent GitHub in nieuw tabblad)</span></a>
      </div>
      {r.kind === "rollback" ? (
        <p className="lead">Terug naar {first ? `de versie van ${when(first.startedAt)}` : "een eerdere versie"}.</p>
      ) : (
        <>
          {plain.length > 0 && <ul>{plain.map((n) => <li key={n.sha}>{n.text}</li>)}</ul>}
          {technical.length > 0 && (
            <details>
              <summary>Technische wijzigingen ({technical.length})</summary>
              <ul>{technical.map((n) => <li key={n.sha}>{n.text}</li>)}</ul>
            </details>
          )}
          {r.notes.length === 0 && <p className="lead">Geen wijzigingen gevonden.</p>}
        </>
      )}
    </li>
  );
}
