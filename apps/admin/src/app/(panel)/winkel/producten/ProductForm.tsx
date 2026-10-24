"use client";
import Link from "next/link";
import { useActionState, useState } from "react";
import type { Product } from "@/lib/api";
import { saveProductForm, type ProductFormState } from "../actions";

type PartnerOption = { slug: string; name: string; enabled: boolean; allowedHosts: string[] };
const AMAZON_SHORT = ["amzn.eu", "amzn.to", "a.co"];

/** Welke partner hoort bij deze link? Korte Amazon-links horen bij Amazon (de API volgt ze bij opslaan). */
export function partnerForUrl(url: string, partners: PartnerOption[]): string | null {
  let host: string;
  try { host = new URL(url.trim()).hostname.toLowerCase(); } catch { return null; }
  const bare = host.replace(/^www\./, "");
  const exact = partners.find((p) => p.allowedHosts.some((h) => h === host || h.replace(/^www\./, "") === bare));
  if (exact) return exact.slug;
  if (AMAZON_SHORT.includes(host)) return partners.find((p) => p.slug === "amazon-nl")?.slug ?? null;
  return partners.find((p) => p.allowedHosts.length === 0)?.slug ?? null; // winkel zonder partnerprogramma
}

/** Product toevoegen of bewerken. De link staat voorop; de partner volgt uit de link. */
export function ProductForm({ editing, partners, materials, marketOptions }: { editing?: Product; partners: PartnerOption[]; materials: { slug: string; name: string }[]; marketOptions: string[] }) {
  const [state, action, pending] = useActionState<ProductFormState, FormData>(saveProductForm, null);
  const v = state?.values;
  const val = (k: string, fallback: string) => (v ? String(v[k] ?? "") : fallback);
  const [partner, setPartner] = useState(val("partner", editing?.partner ?? ""));
  const chosen = partners.find((p) => p.slug === partner);
  const checkedMaterials = v ? (v.material as string[]) : editing?.materials ?? [];
  const checkedMarkets = v ? (v.market as string[]) : editing?.markets ?? ["nl-NL"];
  const allMarkets = [...new Set([...marketOptions, ...checkedMarkets])].sort();
  return (
    <form action={action} className="grid-form" key={state ? JSON.stringify(state) : editing?.slug ?? "nieuw"}>
      {state?.error && <div className="err wide" role="alert"><p>{state.error}</p></div>}
      <label className="field wide"><span>Link naar het product</span>
        <input name="url" type="url" required defaultValue={val("url", editing?.url ?? "")} placeholder="Plak de link uit de winkel of de app (ook amzn.eu/…)"
          onChange={(e) => { const p = partnerForUrl(e.target.value, partners); if (p) setPartner(p); }} />
        <small>Korte deellinks en links met extra's worden bij opslaan netjes gemaakt.</small>
      </label>
      <label className="field"><span>Partner</span>
        <select name="partner" required value={partner} onChange={(e) => setPartner(e.target.value)}>
          <option value="" disabled>Volgt uit de link</option>
          {partners.map((p) => <option key={p.slug} value={p.slug}>{p.name}{p.enabled ? "" : " (uit)"}</option>)}
        </select>
        {chosen && !chosen.enabled && <small className="bad">Deze partner staat uit: zet hem aan onder Koppelingen, anders blijft het product onzichtbaar.</small>}
      </label>
      <label className="field"><span>Naam</span><input name="name" required defaultValue={val("name", editing?.name ?? "")} placeholder="Kleurpotloden, 24 kleuren" /></label>
      <label className="field"><span>Code</span><input name="slug" required defaultValue={val("slug", editing?.slug ?? "")} readOnly={!!editing} placeholder="kleurpotloden-24" pattern="[a-z0-9\-]{2,64}" autoCapitalize="none" spellCheck={false} /><small>Kort en vast; komt in de link en in de cijfers.</small></label>
      <label className="field"><span>Prijsindicatie</span><input name="priceHint" defaultValue={val("priceHint", editing?.priceHint ?? "")} placeholder="ca. € 8" /></label>
      <label className="field"><span>EAN</span><input name="ean" defaultValue={val("ean", editing?.ean ?? "")} inputMode="numeric" pattern="\d{8,14}" /></label>
      <label className="field wide"><span>Toelichting</span><input name="note" defaultValue={val("note", editing?.note ?? "")} placeholder="Zacht en goed te slijpen" /></label>
      <fieldset className="field wide"><legend>Bij materialen</legend>
        <div className="checks">{materials.map((m) => <label key={m.slug} className="check"><input type="checkbox" name="material" value={m.slug} defaultChecked={checkedMaterials.includes(m.slug)} /> {m.name}</label>)}</div>
      </fieldset>
      <fieldset className="field wide"><legend>Landen (markt: land en taal)</legend>
        <div className="checks">{allMarkets.map((m) => <label key={m} className="check"><input type="checkbox" name="market" value={m} defaultChecked={checkedMarkets.includes(m)} /> {m.slice(3)} · {m.slice(0, 2)}</label>)}</div>
        <small>Het product verschijnt alleen in de aangevinkte markten (ADR 0031).</small>
      </fieldset>
      <label className="field"><span>Voorkeur</span><input name="rank" type="number" min={0} max={99} defaultValue={val("rank", String(editing?.rank ?? 0))} /><small>Meer producten bij hetzelfde materiaal? Laagste getal wint.</small></label>
      <label className="check"><input type="checkbox" name="enabled" defaultChecked={v ? v.enabled === "on" : editing?.enabled ?? true} /> Tonen op de site</label>
      <div className="wide"><button type="submit" disabled={pending}>{pending ? "Opslaan…" : "Opslaan"}</button> {editing && <Link href="/winkel/producten" className="lead">Annuleren</Link>}</div>
    </form>
  );
}
