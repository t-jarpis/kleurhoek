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
  const unread = can("contact.read") ? await adminApi.unread().catch(() => 0) : 0;
  return (
    <div className="shell">
      <nav className="side" aria-label="Beheer">
        <div className="brand"><Logo suffix="beheer" size={20} /></div>
        {/* Groepen (design system: AdminNav): een groep verschijnt alleen als je er iets in mag zien. */}
        {can("analytics.read") && <>
          <span className="ui-sidenav-group">Overzicht</span>
          <NavLink href="/" icon="dashboard">Dashboard</NavLink>
          <NavLink href="/analytics" icon="analytics">Analytics</NavLink>
          <NavLink href="/doelen" icon="goals">Doelen</NavLink>
        </>}
        {(can("catalog.manage") || can("sources.read") || can("seo.read")) && <span className="ui-sidenav-group">Inhoud</span>}
        {can("catalog.manage") && <NavLink href="/collecties" icon="collections">Collecties</NavLink>}
        {can("sources.read") && <NavLink href="/bronnen" icon="sources">Bronnengids</NavLink>}
        {can("seo.read") && <NavLink href="/seo" icon="seo">Vindbaarheid</NavLink>}
        {(can("shop.read") || can("contact.read") || can("organizations.read") || can("mail.read")) && <span className="ui-sidenav-group">Klanten en partners</span>}
        {can("mail.read") && <NavLink href="/mail" icon="mail">Mail</NavLink>}
        {can("shop.read") && <NavLink href="/winkel" icon="shop">Winkel</NavLink>}
        {can("contact.read") && <NavLink href="/contact" icon="contact">Contact{unread > 0 && <span className="ui-count" aria-label={`${unread} nieuw`}>{unread}</span>}</NavLink>}
        {can("organizations.read") && <NavLink href="/organisaties" icon="organizations">Organisaties</NavLink>}
        {(can("identity.users.read") || can("operations.access.read") || can("operations.ratelimit.read") || can("releases.read")) && <span className="ui-sidenav-group">Systeem</span>}
        {can("identity.users.read") && <NavLink href="/gebruikers" icon="users">Gebruikers</NavLink>}
        {can("operations.access.read") && <NavLink href="/toegang" icon="access">Toegang</NavLink>}
        {can("operations.ratelimit.read") && <NavLink href="/rate-limits" icon="limits">Rate limits</NavLink>}
        {can("releases.read") && <NavLink href="/releases" icon="releases">Releases</NavLink>}
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
