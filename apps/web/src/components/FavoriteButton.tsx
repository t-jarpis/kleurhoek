"use client";
import { useHref } from "./Base";
import { Icon } from "@kleurhoek/theme";
import { useEffect, useState } from "react";
import { favorites, useFavorites } from "@/lib/local";
import { messages } from "@/i18n/nl";

/**
 * Plaat bewaren als favoriet (design system: FavoriteButton, ADR 0039). Werkt zonder account; met `accounts` en
 * zonder login verschijnt na bewaren eenmalig de hint dat inloggen ze op elk apparaat bewaart.
 */
export function FavoriteButton({ slug, market, language, accounts }: { slug: string; market: string; language: string; accounts: boolean }) {
  const href = useHref();
  const t = messages(language);
  const list = useFavorites();
  const on = list.includes(slug);
  const [linked, setLinked] = useState<boolean | null>(null);
  const [hint, setHint] = useState(false);
  useEffect(() => { void favorites.sync().then(setLinked); }, []);
  const toggle = () => { const now = favorites.toggle(slug); if (now && accounts && linked === false) setHint(true); };
  const back = typeof window === "undefined" ? href() : window.location.pathname;
  return (
    <>
      <button type="button" className="btn ui-fav" aria-pressed={on} onClick={toggle}><Icon name="heart" />{on ? t.favSaved : t.favSave}</button>
      {hint && on && (
        <p className="ui-fav-hint no-print" role="status"><a href={`/auth/login?returnTo=${encodeURIComponent(back)}`}>{t.favLoginLink}</a>{t.favLoginHint.startsWith(",") ? "" : " "}{t.favLoginHint}</p>
      )}
    </>
  );
}
