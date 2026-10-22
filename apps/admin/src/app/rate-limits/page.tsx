import { adminApi } from "@/lib/api";
import { saveRule, toggleRule } from "./actions";

export const dynamic = "force-dynamic";
export const metadata = { title: "Rate limits" };

const KEY = { ip: "per bezoeker (IP, gehasht)", user: "per beheerder", client: "per client" } as const;

export default async function RateLimits() {
  let rules;
  try { rules = await adminApi.rateLimits(); } catch (e) { return <div className="err"><h1>Geen verbinding met de API</h1><p>{(e as Error).message}</p></div>; }
  const today = new Date().toISOString().slice(0, 10);
  return (
    <>
      <div><h1>Rate limits</h1><p className="lead">Een wijziging werkt binnen 30 seconden en komt in het auditlog. Limieten aan de rand (Cloudflare) staan in Terraform.</p></div>
      <section className="panel">
        <table>
          <thead><tr><th>Regel</th><th>Limiet</th><th className="num">Vandaag</th><th className="num">Geblokkeerd, 7 dagen</th><th>Status</th></tr></thead>
          <tbody>
            {rules.map((r) => {
              const t = r.days.find((d) => d.day === today);
              const week = r.days.reduce((s, d) => s + d.blocked, 0);
              return (
                <tr key={r.slug}>
                  <td className="rule"><b>{r.slug}</b><span className="lead">{r.description}</span><span className="lead">{KEY[r.keyBy]}</span></td>
                  <td>
                    <form action={saveRule} className="inline">
                      <input type="hidden" name="slug" value={r.slug} />
                      <input type="number" name="limit" defaultValue={r.limit} min={1} aria-label={`Limiet ${r.slug}`} />
                      <span>per</span>
                      <input type="number" name="windowSeconds" defaultValue={r.windowSeconds} min={1} aria-label={`Venster ${r.slug} in seconden`} />
                      <span>s</span>
                      <button type="submit">Opslaan</button>
                    </form>
                  </td>
                  <td className="num">{(t?.allowed ?? 0).toLocaleString("nl-NL")} door<br /><span className={t?.blocked ? "bad" : "lead"}>{(t?.blocked ?? 0).toLocaleString("nl-NL")} geblokkeerd</span></td>
                  <td className={`num ${week ? "bad" : ""}`}>{week.toLocaleString("nl-NL")}</td>
                  <td className="status">
                    <form action={toggleRule} className="inline">
                      <input type="hidden" name="slug" value={r.slug} />
                      <input type="hidden" name="enabled" value={String(!r.enabled)} />
                      <span className={`pill ${r.enabled ? "on" : "off"}`}>{r.enabled ? "Aan" : "Uit"}</span>
                      <button type="submit" className="ghost">{r.enabled ? "Uitzetten" : "Aanzetten"}</button>
                    </form>
                    <span className="lead">Gewijzigd door {r.updatedBy}</span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </section>
    </>
  );
}
