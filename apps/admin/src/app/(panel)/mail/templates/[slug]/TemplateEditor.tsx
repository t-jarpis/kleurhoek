"use client";
import { useEffect, useMemo, useRef, useState, useTransition } from "react";
import type { I18nText, MailBlock, MailOptions, MailTemplateInput } from "@/lib/api";
import { previewTemplate, saveTemplate, testTemplate } from "../../actions";

const BLOCK_LABEL: Record<MailBlock["type"], string> = { heading: "Kop", text: "Tekst", button: "Knop", plates: "Platen", divider: "Lijn" };
const SOURCE_LABEL = { new: "Nieuw sinds de vorige mail", holiday: "Feestdag die eraan komt", collection: "Een collectie", selected: "Zelf gekozen" } as const;
const newId = () => Math.random().toString(36).slice(2, 10);

function blank(type: MailBlock["type"]): MailBlock {
  const id = newId();
  if (type === "heading" || type === "text") return { id, type, text: {} };
  if (type === "button") return { id, type, label: {}, url: "{{site}}" };
  if (type === "plates") return { id, type, source: "new", max: 6, columns: 3 };
  return { id, type: "divider" };
}

/** Teksten van een blok voor de taalcontrole. */
const textsOf = (b: MailBlock): I18nText[] => (b.type === "heading" || b.type === "text" ? [b.text] : b.type === "button" ? [b.label] : []);

/**
 * Template bewerken (design system: MailBlockEditor en MailPreview, ADR 0037). Links de blokken per taal, rechts
 * het voorbeeld zoals de API hem maakt.
 */
export function TemplateEditor({ slug: initialSlug, initial, options, canManage }: { slug: string | null; initial: MailTemplateInput; options: MailOptions; canManage: boolean }) {
  const [t, setT] = useState<MailTemplateInput>(initial);
  const [slug, setSlug] = useState(initialSlug ?? "");
  const [lang, setLang] = useState("nl");
  const [market, setMarket] = useState(options.markets[0] ?? "nl-nl");
  const [width, setWidth] = useState<"breed" | "mobiel">("breed");
  const [preview, setPreview] = useState<{ subject: string; html: string; text: string; empty: boolean } | { error: string } | null>(null);
  const [status, setStatus] = useState<{ tone: "danger" | "success"; text: string } | null>(null);
  const [pending, start] = useTransition();
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const system = t.kind === "system";
  const languages = options.languages.length ? options.languages : ["nl"];

  // Voorbeeld verversen na een korte pauze in het typen.
  useEffect(() => {
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(() => {
      void previewTemplate({ ...t, name: t.name || "Voorbeeld" }, market).then((r) => setPreview(r.ok ? r : { error: r.error }));
    }, 600);
    return () => { if (timer.current) clearTimeout(timer.current); };
  }, [t, market]);

  const incomplete = useMemo(() => new Set(languages.filter((l) => !t.subject[l] || t.blocks.some((b) => textsOf(b).some((x) => !x[l])))), [t, languages]);
  const setBlock = (i: number, b: MailBlock) => setT((x) => ({ ...x, blocks: x.blocks.map((y, j) => (j === i ? b : y)) }));
  const move = (i: number, d: -1 | 1) => setT((x) => { const b = [...x.blocks]; const j = i + d; if (j < 0 || j >= b.length) return x; [b[i], b[j]] = [b[j]!, b[i]!]; return { ...x, blocks: b }; });
  const remove = (i: number) => setT((x) => ({ ...x, blocks: x.blocks.filter((_, j) => j !== i) }));
  const i18n = (v: I18nText, s: string): I18nText => ({ ...v, [lang]: s });

  function save() {
    start(async () => {
      const r = await saveTemplate(slug, { ...t, name: t.name || slug }, !initialSlug);
      setStatus(r.error ? { tone: "danger", text: r.error } : { tone: "success", text: "Opgeslagen." });
    });
  }
  function test() {
    start(async () => {
      const r = await testTemplate({ ...t, name: t.name || "Test" }, market);
      setStatus(r.error ? { tone: "danger", text: r.error } : { tone: "success", text: `Testmail gestuurd naar ${r.to}.` });
    });
  }

  return (
    <div className="ui-mailedit">
      <fieldset disabled={!canManage || pending} className="stack" style={{ border: 0, padding: 0, margin: 0 }}>
        <section className="panel stack">
          {!initialSlug && <label className="field"><span>Code</span><input value={slug} onChange={(e) => setSlug(e.target.value.toLowerCase())} pattern="[a-z0-9][a-z0-9\-]{0,62}[a-z0-9]" className="mono" required placeholder="nieuwsbrief-herfst" /><small>Kleine letters, cijfers en streepjes.</small></label>}
          <label className="field"><span>Naam</span><input value={t.name} onChange={(e) => setT({ ...t, name: e.target.value })} maxLength={80} /></label>
          {system ? <p className="lead">Vaste template: de site gebruikt hem zelf (bevestigen of welkom). Je kunt de inhoud aanpassen, niet weghalen.</p> : (
            <label className="field"><span>Soort</span>
              <select value={t.kind} onChange={(e) => setT({ ...t, kind: e.target.value as MailTemplateInput["kind"] })}>
                <option value="campaign">Campagne (nieuwsbrief, los versturen)</option><option value="automation">Automatisch (voor workflows)</option>
              </select>
            </label>
          )}
          <div className="ui-langtabs" role="group" aria-label="Taal van de teksten">
            {languages.map((l) => (
              <button key={l} type="button" className="ui-btn" aria-pressed={lang === l} {...(incomplete.has(l) ? { "data-missing": "" } : {})} onClick={() => setLang(l)}>
                {l}{incomplete.has(l) ? " (onvolledig)" : ""}
              </button>
            ))}
          </div>
          <label className="field"><span>Onderwerp ({lang})</span><input value={t.subject[lang] ?? ""} onChange={(e) => setT({ ...t, subject: i18n(t.subject, e.target.value) })} maxLength={200} lang={lang} placeholder={lang !== "nl" ? t.subject.nl : ""} /></label>
          <label className="field"><span>Voorkoptekst ({lang})</span><input value={t.preheader[lang] ?? ""} onChange={(e) => setT({ ...t, preheader: i18n(t.preheader, e.target.value) })} maxLength={200} lang={lang} placeholder={lang !== "nl" ? t.preheader.nl : ""} /><small>Grijze regel die mailprogramma&apos;s naast het onderwerp tonen.</small></label>
        </section>

        <ol className="ui-blocks" aria-label="Blokken">
          {t.blocks.map((b, i) => (
            <li key={b.id} className="ui-block">
              <div className="ui-block-head">
                <strong>{i + 1}. {BLOCK_LABEL[b.type]}</strong>
                <button type="button" className="ui-btn" data-variant="quiet" onClick={() => move(i, -1)} disabled={i === 0}>Omhoog</button>
                <button type="button" className="ui-btn" data-variant="quiet" onClick={() => move(i, 1)} disabled={i === t.blocks.length - 1}>Omlaag</button>
                <button type="button" className="ui-btn" data-variant="danger" onClick={() => remove(i)}>Verwijderen</button>
              </div>
              {b.type === "heading" && <input aria-label={`Kop (${lang})`} value={b.text[lang] ?? ""} onChange={(e) => setBlock(i, { ...b, text: i18n(b.text, e.target.value) })} lang={lang} placeholder={lang !== "nl" ? b.text.nl : ""} maxLength={160} />}
              {b.type === "text" && <>
                <textarea aria-label={`Tekst (${lang})`} value={b.text[lang] ?? ""} onChange={(e) => setBlock(i, { ...b, text: i18n(b.text, e.target.value) })} lang={lang} placeholder={lang !== "nl" ? b.text.nl : ""} rows={5} maxLength={4000} />
                <small>Lege regel = nieuwe alinea. **vet**, [tekst](https://…). Variabelen: {"{{site}}"}, {"{{voorkeuren}}"}.</small>
              </>}
              {b.type === "button" && <div className="ui-step-row">
                <label className="field"><span>Tekst ({lang})</span><input value={b.label[lang] ?? ""} onChange={(e) => setBlock(i, { ...b, label: i18n(b.label, e.target.value) })} lang={lang} placeholder={lang !== "nl" ? b.label.nl : ""} maxLength={60} /></label>
                <label className="field"><span>Link</span><input value={b.url} onChange={(e) => setBlock(i, { ...b, url: e.target.value })} className="mono" maxLength={500} /></label>
              </div>}
              {b.type === "plates" && <div className="ui-step-row">
                <label className="field"><span>Bron</span>
                  <select value={b.source} onChange={(e) => setBlock(i, { ...b, source: e.target.value as typeof b.source })}>
                    {(Object.keys(SOURCE_LABEL) as (keyof typeof SOURCE_LABEL)[]).map((s) => <option key={s} value={s}>{SOURCE_LABEL[s]}</option>)}
                  </select>
                </label>
                {b.source === "collection" && <label className="field"><span>Collectie</span>
                  <select value={b.collection ?? ""} onChange={(e) => setBlock(i, { ...b, collection: e.target.value })}><option value="">Kies…</option>{options.collections.map((c) => <option key={c.slug} value={c.slug}>{c.name}</option>)}</select>
                </label>}
                {b.source === "selected" && <label className="field"><span>Codes van platen</span><input value={(b.slugs ?? []).join(" ")} onChange={(e) => setBlock(i, { ...b, slugs: e.target.value.split(/[\s,]+/).filter(Boolean).slice(0, 30) })} className="mono" placeholder="egel uil lampion-maken" /></label>}
                <label className="field"><span>Aantal</span><input type="number" min={1} max={12} value={b.max} onChange={(e) => setBlock(i, { ...b, max: Math.min(12, Math.max(1, Number(e.target.value) || 1)) })} /></label>
                <label className="field"><span>Kolommen</span><select value={b.columns} onChange={(e) => setBlock(i, { ...b, columns: Number(e.target.value) === 2 ? 2 : 3 })}><option value={2}>2</option><option value={3}>3</option></select></label>
              </div>}
              {b.type === "divider" && <small>Een dunne lijn tussen twee delen.</small>}
            </li>
          ))}
        </ol>
        <div className="toolbar" role="group" aria-label="Blok toevoegen">
          <span>Blok toevoegen:</span>
          {(Object.keys(BLOCK_LABEL) as MailBlock["type"][]).map((k) => <button key={k} type="button" className="ui-btn" onClick={() => setT((x) => ({ ...x, blocks: [...x.blocks, blank(k)] }))}>{BLOCK_LABEL[k]}</button>)}
        </div>
        {status && <div className="ui-callout" data-tone={status.tone} role={status.tone === "danger" ? "alert" : "status"}><p>{status.text}</p></div>}
        {canManage && <div className="toolbar">
          <button type="button" className="ui-btn" data-variant="primary" onClick={save} disabled={!slug}>{pending ? "Bezig…" : "Opslaan"}</button>
          <button type="button" className="ui-btn" onClick={test}>Testmail naar mij</button>
        </div>}
      </fieldset>

      <aside className="ui-mailpreview" data-width={width} aria-label="Voorbeeld">
        <div className="ui-step-row">
          <label className="field"><span>Markt</span><select value={market} onChange={(e) => setMarket(e.target.value)}>{options.markets.map((m) => <option key={m} value={m}>{m}</option>)}</select></label>
          <span className="ui-langtabs" role="group" aria-label="Breedte">
            <button type="button" className="ui-btn" aria-pressed={width === "breed"} onClick={() => setWidth("breed")}>Breed</button>
            <button type="button" className="ui-btn" aria-pressed={width === "mobiel"} onClick={() => setWidth("mobiel")}>Mobiel</button>
          </span>
        </div>
        {preview === null ? <p className="lead">Voorbeeld laden…</p> : "error" in preview ? <div className="ui-callout" data-tone="warning"><p>{preview.error}</p></div> : <>
          <p className="ui-mailpreview-subject">{preview.subject}</p>
          {preview.empty && <div className="ui-callout" data-tone="warning"><p>Deze mail gaat nu niet weg: er zijn geen platen voor de gekozen bron in deze markt.</p></div>}
          <iframe title="Voorbeeld van de mail" sandbox="" srcDoc={preview.html} />
          <details><summary>Tekstversie</summary><pre style={{ whiteSpace: "pre-wrap" }}>{preview.text}</pre></details>
        </>}
      </aside>
    </div>
  );
}
