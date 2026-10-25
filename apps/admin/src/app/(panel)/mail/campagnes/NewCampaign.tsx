"use client";
import { useActionState } from "react";
import { createCampaign, type ActionResult } from "../actions";

const TOPIC: Record<string, string> = { "nieuwe-platen": "Nieuwe platen", feestdagen: "Feestdagen", nieuwsbrief: "Nieuwsbrief" };

/** Nieuwe campagne: naam, template, onderwerpen en eventueel markten. Versturen gebeurt daarna in de lijst. */
export function NewCampaign({ templates, topics, markets, counts }: { templates: { slug: string; name: string }[]; topics: string[]; markets: string[]; counts: Record<string, number> }) {
  const [state, action, pending] = useActionState<ActionResult, FormData>(createCampaign, { error: null });
  return (
    <form action={action} className="stack">
      {state.error && <div className="ui-callout" data-tone="danger" role="alert"><p>{state.error}</p></div>}
      <div className="grid-form">
        <label className="field"><span>Naam</span><input name="name" required minLength={2} maxLength={120} placeholder="Nieuwsbrief november" /></label>
        <label className="field"><span>Template</span><select name="template" required defaultValue="nieuwsbrief">{templates.map((t) => <option key={t.slug} value={t.slug}>{t.name}</option>)}</select></label>
      </div>
      <fieldset className="field"><legend>Aan abonnees van</legend><div className="checks">
        {topics.map((t) => <label key={t} className="check"><input type="checkbox" name="topics" value={t} defaultChecked={t === "nieuwsbrief"} /> {TOPIC[t] ?? t} ({counts[t] ?? 0})</label>)}
      </div><small>Wie meerdere aangevinkte onderwerpen koos, krijgt de mail één keer.</small></fieldset>
      {markets.length > 1 && <fieldset className="field"><legend>Markten (leeg = alle)</legend><div className="checks">
        {markets.map((m) => <label key={m} className="check"><input type="checkbox" name="markets" value={m} /> <code>{m}</code></label>)}
      </div></fieldset>}
      <div><button type="submit" className="ui-btn" data-variant="primary" disabled={pending}>{pending ? "Bezig…" : "Campagne aanmaken"}</button></div>
    </form>
  );
}
