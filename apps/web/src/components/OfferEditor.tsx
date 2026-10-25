"use client";
import { useHref } from "./Base";
import { useEffect, useMemo, useState } from "react";
import { messages } from "@/i18n/nl";

interface Data {
  name: string;
  offer: { collections: string[] | null; goals: string[] | null; excluded: string[] };
  goals: { slug: string; name: string }[];
  collections: { slug: string; name: string; description: string | null; plates: string[] }[];
  plates: { slug: string; name: string; category: string; kind: string; goals: string[] }[];
}

const norm = (s: string) => s.toLocaleLowerCase().normalize("NFD").replace(/\p{Diacritic}/gu, "");

/**
 * Aanbod van de eigen organisatie (design system: OfferEditor, ADR 0036): leerdoelen, collecties en losse platen.
 * Alles via de eigen /auth-routes; het token komt nooit in de browser.
 */
export function OfferEditor({ org, market, language }: { org: string; market: string; language: string }) {
  const href = useHref();
  const t = messages(language);
  const [data, setData] = useState<Data | "anon" | "none" | "error" | null>(null);
  const [goals, setGoals] = useState<string[]>([]);
  const [collections, setCollections] = useState<string[]>([]);
  const [excluded, setExcluded] = useState<Set<string>>(new Set());
  const [q, setQ] = useState("");
  const [status, setStatus] = useState<{ busy: boolean; text: string | null }>({ busy: false, text: null });

  useEffect(() => {
    fetch(`/auth/beheer/${org}?language=${language}`).then(async (r) => {
      if (r.status === 401) return setData("anon");
      if (r.status === 404) return setData("none");
      if (!r.ok) return setData("error");
      const d = (await r.json()) as Data;
      setGoals(d.offer.goals ?? []); setCollections(d.offer.collections ?? []); setExcluded(new Set(d.offer.excluded));
      setData(d);
    }).catch(() => setData("error"));
  }, [org, language]);

  const allowed = useMemo(() => {
    if (typeof data !== "object" || !data) return null;
    return collections.length ? new Set(data.collections.filter((c) => collections.includes(c.slug)).flatMap((c) => c.plates)) : null;
  }, [data, collections]);

  if (data === null) return <p className="muted">{t.loading}</p>;
  if (data === "error") return <p className="muted">{t.accountError}</p>;
  if (data === "anon") return <p><a className="btn primary" href={`/auth/login?returnTo=${encodeURIComponent(href("/beheer"))}`}>{t.login}</a></p>;
  if (data === "none") return <p className="panel">{t.mgNotManager}</p>;

  const inScope = (p: Data["plates"][number]) => (!allowed || allowed.has(p.slug)) && (!goals.length || p.goals.some((g) => goals.includes(g)));
  const scoped = data.plates.filter(inScope);
  const visible = scoped.filter((p) => !excluded.has(p.slug)).length;
  const query = norm(q.trim());
  const listed = query ? scoped.filter((p) => norm(p.name).includes(query) || p.slug.includes(query)) : scoped;
  const toggle = (list: string[], set: (v: string[]) => void, slug: string) => set(list.includes(slug) ? list.filter((x) => x !== slug) : [...list, slug]);

  async function save() {
    setStatus({ busy: true, text: t.mgSaving });
    const res = await fetch(`/auth/beheer/${org}`, {
      method: "PUT", headers: { "content-type": "application/json" },
      body: JSON.stringify({ collections: collections.length ? collections : null, goals: goals.length ? goals : null, excluded: [...excluded] }),
    }).catch(() => null);
    setStatus({ busy: false, text: res?.ok ? t.mgSaved : t.mgError });
  }

  return (
    <div className="ui-offer">
      <fieldset>
        <legend>{t.mgGoals}</legend>
        <p className="ui-offer-hint">{t.mgGoalsHint}</p>
        <div className="ui-offer-choices">
          {data.goals.map((g) => <label key={g.slug} className="chk"><input type="checkbox" checked={goals.includes(g.slug)} onChange={() => toggle(goals, setGoals, g.slug)} /> {g.name}</label>)}
        </div>
      </fieldset>
      {data.collections.length > 0 && (
        <fieldset>
          <legend>{t.mgCollections}</legend>
          <p className="ui-offer-hint">{t.mgCollectionsHint}</p>
          <div className="ui-offer-choices">
            {data.collections.map((c) => (
              <label key={c.slug} className="chk"><input type="checkbox" checked={collections.includes(c.slug)} onChange={() => toggle(collections, setCollections, c.slug)} />
                <span>{c.name} <span className="muted">({c.plates.length} {t.mgPlatesIn})</span>{c.description && <small className="muted" style={{ display: "block" }}>{c.description}</small>}</span>
              </label>
            ))}
          </div>
        </fieldset>
      )}
      <fieldset>
        <legend>{t.mgPlates}</legend>
        <p className="ui-offer-hint">{t.mgPlatesHint}</p>
        <label className="visually-hidden" htmlFor="kh-offer-search">{t.mgSearch}</label>
        <input id="kh-offer-search" className="ui-offer-search" type="search" value={q} onChange={(e) => setQ(e.target.value)} placeholder={t.mgSearch} autoComplete="off" />
        {listed.length === 0 ? <p className="muted">{t.mgNoMatch}</p> : (
          <ul className="ui-offer-list">
            {listed.map((p) => {
              const off = excluded.has(p.slug);
              return (
                <li key={p.slug} className="ui-offer-row" {...(off ? { "data-off": "" } : {})}>
                  <span>{p.name}<small>{t.kindNames[p.kind] ?? p.kind}</small></span>
                  <button type="button" className="ui-switch" aria-pressed={!off} onClick={() => setExcluded((s) => { const n = new Set(s); if (off) n.delete(p.slug); else n.add(p.slug); return n; })}>
                    {off ? t.mgHidden : t.mgShown}<span className="visually-hidden">: {p.name}</span>
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </fieldset>
      <div className="ui-offer-bar">
        <button type="button" className="ui-btn" data-variant="primary" disabled={status.busy} onClick={() => void save()}>{status.busy ? t.mgSaving : t.mgSave}</button>
        <span role="status">{status.text && !status.busy ? `${status.text} ` : ""}{t.mgCount(visible, scoped.length)}</span>
      </div>
    </div>
  );
}
