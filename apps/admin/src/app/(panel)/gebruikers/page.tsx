import Link from "next/link";
import { adminApi, describe, type AdminUser, type Role } from "@/lib/api";
import { saveRoles, setStatus } from "./actions";

export const metadata = { title: "Gebruikers" };

type Search = { soort?: string; q?: string; pagina?: string; melding?: string };

const fmt = (iso: string | null) => (iso ? new Intl.DateTimeFormat("nl-NL", { dateStyle: "medium", timeStyle: "short" }).format(new Date(iso)) : "—");

export default async function Users({ searchParams }: { searchParams: Promise<Search> }) {
  const s = await searchParams;
  const kind = s.soort === "member" ? "member" : "admin";
  const page = Math.max(1, Number(s.pagina) || 1);
  const q = s.q?.trim().slice(0, 100) || undefined;
  let data, roles: Role[], me;
  try {
    [data, { roles }, me] = await Promise.all([adminApi.users({ kind, ...(q ? { q } : {}), page }), adminApi.roles(), adminApi.me()]);
  } catch (e) {
    const d = describe(e);
    return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>;
  }
  const canAssign = me.permissions.includes("identity.roles.assign");
  const canBlock = me.permissions.includes("identity.users.block");
  const self = (u: AdminUser) => u.id === me.userId;
  const params = new URLSearchParams({ soort: kind, ...(q ? { q } : {}), ...(page > 1 ? { pagina: String(page) } : {}) });
  const backTo = `/gebruikers?${params}`;
  const pages = Math.max(1, Math.ceil(data.total / data.pageSize));
  const link = (over: Record<string, string>) => `/gebruikers?${new URLSearchParams({ soort: kind, ...(q ? { q } : {}), ...over })}`;

  return (
    <>
      <div>
        <h1>Gebruikers</h1>
        <p className="lead">Inloggen en accounts zelf staan in Zitadel. Hier beheer je rollen en blokkades voor Kleurhoek; elke wijziging komt in het auditlog.</p>
      </div>
      {s.melding && <p className="note" role="status">{s.melding}</p>}
      <div className="toolbar">
        <div className="tabs" role="tablist">
          <Link role="tab" aria-selected={kind === "admin"} href="/gebruikers?soort=admin">Beheerders</Link>
          <Link role="tab" aria-selected={kind === "member"} href="/gebruikers?soort=member">Websitegebruikers</Link>
        </div>
        <form className="inline" action="/gebruikers">
          <input type="hidden" name="soort" value={kind} />
          <input type="search" name="q" defaultValue={q} placeholder="Naam of e-mail" aria-label="Zoeken" />
          <button type="submit">Zoeken</button>
        </form>
      </div>
      <section className="panel">
        {data.users.length === 0 ? <p className="lead">Geen gebruikers gevonden.</p> : (
          <table>
            <thead><tr><th>Gebruiker</th>{kind === "admin" && <th>Rollen</th>}<th>Land</th><th>Laatst actief</th><th>Status</th></tr></thead>
            <tbody>
              {data.users.map((u) => (
                <tr key={u.id}>
                  <td className="rule"><b>{u.displayName ?? "Naamloos"}</b><span className="lead">{u.email ?? "geen e-mail"}</span><span className="lead">Sinds {fmt(u.createdAt)}</span></td>
                  {kind === "admin" && (
                    <td>
                      {canAssign && !self(u) ? (
                        <form action={saveRoles} className="roles">
                          <input type="hidden" name="id" value={u.id} />
                          <input type="hidden" name="back" value={backTo} />
                          {roles.map((r) => (
                            <label key={r.slug} title={r.permissions.join(", ")}>
                              <input type="checkbox" name="role" value={r.slug} defaultChecked={u.roles.includes(r.slug)} /> {r.name}
                            </label>
                          ))}
                          <button type="submit" className="ghost">Opslaan</button>
                        </form>
                      ) : (u.roles.length ? u.roles.join(", ") : <span className="lead">geen</span>)}
                    </td>
                  )}
                  <td>{u.country ?? "—"}</td>
                  <td>{fmt(u.lastLoginAt)}</td>
                  <td className="status">
                    <span className={`pill ${u.status === "active" ? "on" : "off"}`}>{u.status === "active" ? "Actief" : "Geblokkeerd"}</span>
                    {self(u) && <span className="lead">Dit ben jij</span>}
                    {canBlock && !self(u) && (
                      <form action={setStatus} className="inline">
                        <input type="hidden" name="id" value={u.id} />
                        <input type="hidden" name="back" value={backTo} />
                        <input type="hidden" name="status" value={u.status === "active" ? "blocked" : "active"} />
                        <button type="submit" className="ghost">{u.status === "active" ? "Blokkeren" : "Deblokkeren"}</button>
                      </form>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        {pages > 1 && (
          <nav className="pager" aria-label="Pagina's">
            {page > 1 && <Link href={link({ pagina: String(page - 1) })}>← Vorige</Link>}
            <span>Pagina {page} van {pages} · {data.total} gebruikers</span>
            {page < pages && <Link href={link({ pagina: String(page + 1) })}>Volgende →</Link>}
          </nav>
        )}
      </section>
    </>
  );
}
