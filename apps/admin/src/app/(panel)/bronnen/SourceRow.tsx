import type { Source } from "@/lib/api";
import { sourceAction, updateSource } from "./actions";
import { sourceState, when } from "./labels";

/**
 * Eén link naar de maker met de laatste controle en de knoppen. De paginatitel bij de maker tonen we hier
 * alleen als hulp; op de site staat altijd onze eigen titel.
 */
export function SourceRow({ s, canManage, from }: { s: Source; canManage: boolean; from?: "nakijken" }) {
  const state = sourceState(s);
  const act = (action: "check" | "approve" | "reject" | "delete", label: string, cls = "ghost") => (
    <form action={sourceAction}>
      <input type="hidden" name="id" value={s.id} /><input type="hidden" name="theme" value={s.themeSlug} /><input type="hidden" name="action" value={action} />
      {from && <input type="hidden" name="from" value={from} />}
      <button type="submit" className={cls}>{label}</button>
    </form>
  );
  return (
    <section className="panel stack">
      <div className="row-between">
        <div>
          <h2>{s.title ?? "(nog geen titel)"}</h2>
          <a href={s.url} target="_blank" rel="noopener noreferrer">{s.url}</a>
        </div>
        <span className={`pill ${state.on ? "on" : "off"}`}>{state.label}</span>
      </div>
      <p className={state.bad ? "bad" : "lead"}>
        Laatste controle: {when(s.lastCheckedAt)}{s.httpStatus ? ` · HTTP ${s.httpStatus}` : ""}
        {s.robotsAllowed === false ? " · robots.txt staat het niet toe" : ""}{s.checkNote ? ` · ${s.checkNote}` : ""}
        {s.finalUrl && s.finalUrl !== s.url ? ` · doorverwezen naar ${s.finalUrl}` : ""}
      </p>
      {s.pageTitle && <p className="lead">Titel bij de maker: <i>{s.pageTitle}</i></p>}
      <p className="lead">
        Basis: {s.basis === "license" ? `licentie van de maker${s.licenseDate ? ` (${s.licenseDate})` : ""}: ${s.licenseNote ?? ""}` : "alleen een link (geen beeld van de maker)"}
        {s.approvedBy ? ` · goedgekeurd door ${s.approvedBy}` : ""}
      </p>
      {canManage && (
        <>
          <div className="checks">
            {act("check", "Nu controleren")}
            {s.status !== "approved" && s.health === "ok" && act("approve", "Goedkeuren", "")}
            {s.status === "approved" && s.changed && s.health === "ok" && act("approve", "Ziet er goed uit", "")}
            {s.status !== "rejected" && act("reject", "Afwijzen")}
            {act("delete", "Verwijderen", "danger")}
          </div>
          {!from && (
            <details>
              <summary>Titel, beschrijving en basis aanpassen</summary>
              <form action={updateSource} className="grid-form">
                <input type="hidden" name="id" value={s.id} /><input type="hidden" name="theme" value={s.themeSlug} />
                <label className="field"><span>Eigen titel</span><input name="title" required minLength={2} maxLength={120} defaultValue={s.title ?? ""} /></label>
                <label className="field"><span>Basis</span>
                  <select name="basis" defaultValue={s.basis}><option value="link">Alleen een link</option><option value="license">Licentie van de maker</option></select>
                </label>
                <label className="field"><span>Datum toestemming</span><input name="licenseDate" type="date" defaultValue={s.licenseDate ?? ""} /></label>
                <label className="field wide"><span>Beschrijving (eigen tekst)</span><textarea name="description" maxLength={400} rows={2} defaultValue={s.description ?? ""} /></label>
                <label className="field wide"><span>Licentie: wat mag, en waar staat de toestemming</span><textarea name="licenseNote" maxLength={1000} rows={2} defaultValue={s.licenseNote ?? ""} /></label>
                <div><button type="submit">Opslaan</button></div>
              </form>
            </details>
          )}
        </>
      )}
    </section>
  );
}
