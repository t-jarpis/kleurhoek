"use client";
import { useHref } from "./Base";
import Link from "next/link";
import { useEffect } from "react";
import { favorites, useFavorites } from "@/lib/local";
import { messages } from "@/i18n/nl";

/** Wat een account je geeft (design system: AccountBenefits, ADR 0039), met een link naar je favorieten. */
export function AccountBenefits({ market, language }: { market: string; language: string }) {
  const href = useHref();
  const t = messages(language);
  const favs = useFavorites();
  useEffect(() => { void favorites.sync(); }, []);
  return (
    <section className="kh-pitch">
      <h2>{t.accBenefitsTitle}</h2>
      <ul className="kh-benefits">
        {t.accBenefits.map(([title, text]) => <li key={title}><b>{title}</b><span>{text}</span></li>)}
      </ul>
      {favs.length > 0 && <p><Link className="btn" href={href("?onderwerp=favorieten#platen")}>{t.accFavorites} ({favs.length})</Link></p>}
    </section>
  );
}
