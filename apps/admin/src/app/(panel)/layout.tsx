import { Logo } from "@kleurhoek/theme";
import { NavLink } from "@/components/NavLink";
import { LogoutButton } from "@/components/LogoutButton";
import { adminApi } from "@/lib/api";
import { viewer } from "@/lib/session";

export const dynamic = "force-dynamic";

/** Menu op basis van de rechten die de API teruggeeft: je ziet alleen wat je mag. */
export default async function PanelLayout({ children }: { children: React.ReactNode }) {
  const [who, me] = await Promise.all([viewer(), adminApi.me().catch(() => null)]);
  const can = (p: string) => me?.permissions.includes(p) ?? false;
  return (
    <div className="shell">
      <nav className="side" aria-label="Beheer">
        <div className="brand"><Logo suffix="beheer" size={20} /></div>
        {can("analytics.read") && <NavLink href="/">Dashboard</NavLink>}
        {can("analytics.read") && <NavLink href="/doelen">Doelen</NavLink>}
        {can("shop.read") && <NavLink href="/winkel">Winkel</NavLink>}
        {can("identity.users.read") && <NavLink href="/gebruikers">Gebruikers</NavLink>}
        {can("operations.ratelimit.read") && <NavLink href="/rate-limits">Rate limits</NavLink>}
        {can("organizations.read") && <NavLink href="/organisaties">Organisaties</NavLink>}
        {can("operations.access.read") && <NavLink href="/toegang">Toegang</NavLink>}
        <div className="who">
          <span>{who.name ?? who.email ?? "Beheerder"}</span>
          {who.dev ? <span className="pill off">lokaal</span> : <LogoutButton />}
        </div>
      </nav>
      <main>
        {me && me.permissions.length === 0 ? (
          <div className="err"><h1>Nog geen rol</h1><p>Je bent ingelogd, maar hebt nog geen rol. Vraag een platformbeheerder om je er een te geven.</p></div>
        ) : children}
      </main>
    </div>
  );
}
