"use client";
import { useEffect, useState } from "react";
import { logout } from "@/lib/account";
import type { Messages } from "@/i18n/nl";

type State = { enabled: boolean; user: { name: string | null } | null } | null;

/**
 * Inlogknop. Vraagt de sessie los op, zodat de pagina zelf voor iedereen gelijk en dus cachebaar blijft.
 * Kinderen hoeven niet in te loggen; het account is voor ouders en leerkrachten.
 */
export function AccountButton({ market, t }: { market: string; t: Pick<Messages, "login" | "account" | "logout"> }) {
  const [state, setState] = useState<State>(null);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    let live = true;
    fetch("/auth/session").then((r) => (r.ok ? r.json() : null)).then((s: State) => { if (live) setState(s); }).catch(() => undefined);
    return () => { live = false; };
  }, []);

  if (!state?.enabled) return null;
  if (!state.user) {
    const back = typeof window === "undefined" ? `/${market}` : window.location.pathname + window.location.search;
    return <a className="btn" href={`/auth/login?returnTo=${encodeURIComponent(back)}`}>{t.login}</a>;
  }
  return (
    <div className="acct">
      <button type="button" className="btn" aria-expanded={open} onClick={() => setOpen(!open)}>{state.user.name ?? t.account}</button>
      {open && (
        <div className="acct-menu">
          <a href={`/${market}/account`}>{t.account}</a>
          <button type="button" onClick={() => void logout()}>{t.logout}</button>
        </div>
      )}
    </div>
  );
}
