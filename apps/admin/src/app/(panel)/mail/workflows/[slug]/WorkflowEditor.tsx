"use client";
import { useState, useTransition } from "react";
import type { MailOptions, MailStep, MailTopic, MailTrigger, MailWorkflow } from "@/lib/api";
import { saveWorkflow } from "../../actions";
import { DAYS } from "../labels";

type Body = Pick<MailWorkflow, "name" | "enabled" | "trigger" | "steps">;
const TOPIC: Record<MailTopic, string> = { "nieuwe-platen": "Nieuwe platen", feestdagen: "Feestdagen", nieuwsbrief: "Nieuwsbrief" };
const STEP_LABEL: Record<MailStep["type"], string> = { filter: "Filter", require_plates: "Alleen als er nieuwe platen zijn", wait: "Wachten", send: "Mail sturen" };
const TRIGGERS: Record<MailTrigger["type"], { label: string; make: () => MailTrigger }> = {
  subscribed: { label: "Na aanmelden", make: () => ({ type: "subscribed" }) },
  schedule: { label: "Vaste dag en tijd", make: () => ({ type: "schedule", weekday: 1, hour: 8 }) },
  plates_published: { label: "Nieuwe platen gepubliceerd", make: () => ({ type: "plates_published", min: 5 }) },
  holiday_soon: { label: "Feestdag komt eraan", make: () => ({ type: "holiday_soon", days: 14 }) },
};
const num = (v: string, min: number, max: number) => Math.min(max, Math.max(min, Number(v) || min));

/** Workflow bewerken (design system: WorkflowSteps, ADR 0037): aanleiding en stappen onder elkaar. */
export function WorkflowEditor({ slug: initialSlug, initial, options, canManage }: { slug: string | null; initial: Body; options: MailOptions; canManage: boolean }) {
  const [w, setW] = useState<Body>(initial);
  const [slug, setSlug] = useState(initialSlug ?? "");
  const [error, setError] = useState<string | null>(null);
  const [pending, start] = useTransition();
  // De bevestigingsmail hoort bij aanmelden zelf, niet in een workflow.
  const templates = options.templates.filter((tp) => tp.slug !== "bevestigen");
  const setStep = (i: number, s: MailStep) => setW((x) => ({ ...x, steps: x.steps.map((y, j) => (j === i ? s : y)) }));
  const move = (i: number, d: -1 | 1) => setW((x) => { const s = [...x.steps]; const j = i + d; if (j < 0 || j >= s.length) return x; [s[i], s[j]] = [s[j]!, s[i]!]; return { ...x, steps: s }; });
  const add = (type: MailStep["type"]) => setW((x) => ({ ...x, steps: [...x.steps, type === "filter" ? { type, topics: ["nieuwe-platen"] } : type === "require_plates" ? { type, min: 3 } : type === "wait" ? { type, hours: 24 } : { type, template: templates[0]?.slug ?? "" }] }));
  const t = w.trigger;

  return (
    <fieldset disabled={!canManage || pending} className="stack" style={{ border: 0, padding: 0, margin: 0 }}>
      <section className="panel stack">
        {!initialSlug && <label className="field"><span>Code</span><input value={slug} onChange={(e) => setSlug(e.target.value.toLowerCase())} className="mono" required placeholder="herfst-reeks" /></label>}
        <label className="field"><span>Naam</span><input value={w.name} onChange={(e) => setW({ ...w, name: e.target.value })} maxLength={80} required /></label>
        <form onSubmit={(e) => e.preventDefault()}><button type="button" className="ui-switch" aria-pressed={w.enabled} onClick={() => setW({ ...w, enabled: !w.enabled })}>{w.enabled ? "Actief" : "Uit"}<span className="visually-hidden">: {w.name}</span></button></form>
      </section>
      <ol className="ui-steps" aria-label="Aanleiding en stappen">
        <li className="ui-step" data-kind="trigger">
          <strong>Aanleiding</strong>
          <div className="ui-step-row">
            <label className="field"><span>Wanneer</span>
              <select value={t.type} onChange={(e) => setW({ ...w, trigger: TRIGGERS[e.target.value as MailTrigger["type"]].make() })}>
                {(Object.keys(TRIGGERS) as MailTrigger["type"][]).map((k) => <option key={k} value={k}>{TRIGGERS[k].label}</option>)}
              </select>
            </label>
            {t.type === "schedule" && <>
              <label className="field"><span>Dag</span><select value={t.weekday} onChange={(e) => setW({ ...w, trigger: { ...t, weekday: Number(e.target.value) } })}>{DAYS.map((d, i) => <option key={d} value={i}>{d}</option>)}</select></label>
              <label className="field"><span>Uur (Nederlandse tijd)</span><input type="number" min={0} max={23} value={t.hour} onChange={(e) => setW({ ...w, trigger: { ...t, hour: num(e.target.value, 0, 23) } })} /></label>
            </>}
            {t.type === "plates_published" && <label className="field"><span>Minstens zoveel nieuwe platen</span><input type="number" min={1} max={100} value={t.min} onChange={(e) => setW({ ...w, trigger: { ...t, min: num(e.target.value, 1, 100) } })} /></label>}
            {t.type === "holiday_soon" && <label className="field"><span>Dagen van tevoren</span><input type="number" min={1} max={60} value={t.days} onChange={(e) => setW({ ...w, trigger: { ...t, days: num(e.target.value, 1, 60) } })} /></label>}
          </div>
          {t.type === "schedule" && <small>Met een stap &quot;Alleen als er nieuwe platen zijn&quot; gaat de mail alleen weg als er sinds de vorige keer genoeg nieuws is.</small>}
        </li>
        {w.steps.map((s, i) => (
          <li key={i} className="ui-step">
            <div className="ui-block-head">
              <strong>{STEP_LABEL[s.type]}</strong>
              <button type="button" className="ui-btn" data-variant="quiet" onClick={() => move(i, -1)} disabled={i === 0}>Omhoog</button>
              <button type="button" className="ui-btn" data-variant="quiet" onClick={() => move(i, 1)} disabled={i === w.steps.length - 1}>Omlaag</button>
              <button type="button" className="ui-btn" data-variant="danger" onClick={() => setW((x) => ({ ...x, steps: x.steps.filter((_, j) => j !== i) }))}>Verwijderen</button>
            </div>
            {s.type === "filter" && <div className="ui-step-row">
              <fieldset className="field"><legend>Onderwerpen (minstens één)</legend><div className="checks">
                {options.topics.map((tp) => <label key={tp} className="check"><input type="checkbox" checked={s.topics?.includes(tp) ?? false} onChange={() => setStep(i, { ...s, topics: s.topics?.includes(tp) ? s.topics.filter((x) => x !== tp) : [...(s.topics ?? []), tp] })} /> {TOPIC[tp]}</label>)}
              </div></fieldset>
              {options.markets.length > 1 && <fieldset className="field"><legend>Markten (leeg = alle)</legend><div className="checks">
                {options.markets.map((m) => <label key={m} className="check"><input type="checkbox" checked={s.markets?.includes(m) ?? false} onChange={() => setStep(i, { ...s, markets: s.markets?.includes(m) ? s.markets.filter((x) => x !== m) : [...(s.markets ?? []), m] })} /> <code>{m}</code></label>)}
              </div></fieldset>}
            </div>}
            {s.type === "require_plates" && <label className="field"><span>Minstens zoveel nieuwe platen sinds de vorige keer</span><input type="number" min={1} max={100} value={s.min} onChange={(e) => setStep(i, { ...s, min: num(e.target.value, 1, 100) })} /></label>}
            {s.type === "wait" && <label className="field"><span>Uren wachten</span><input type="number" min={1} max={1440} value={s.hours} onChange={(e) => setStep(i, { ...s, hours: num(e.target.value, 1, 1440) })} /></label>}
            {s.type === "send" && <label className="field"><span>Template</span><select value={s.template} onChange={(e) => setStep(i, { ...s, template: e.target.value })}>{templates.map((tp) => <option key={tp.slug} value={tp.slug}>{tp.name}</option>)}</select></label>}
          </li>
        ))}
      </ol>
      <div className="toolbar" role="group" aria-label="Stap toevoegen">
        <span>Stap toevoegen:</span>
        {(Object.keys(STEP_LABEL) as MailStep["type"][]).map((k) => <button key={k} type="button" className="ui-btn" onClick={() => add(k)}>{STEP_LABEL[k]}</button>)}
      </div>
      {error && <div className="ui-callout" data-tone="danger" role="alert"><p>{error}</p></div>}
      {canManage && <div><button type="button" className="ui-btn" data-variant="primary" disabled={!slug || !w.name} onClick={() => start(async () => { const r = await saveWorkflow(slug, w, !initialSlug); if (r?.error) setError(r.error); })}>{pending ? "Bezig…" : "Opslaan"}</button></div>}
    </fieldset>
  );
}
