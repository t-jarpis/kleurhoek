"use client";
import { useState } from "react";
import { createOrganization } from "./actions";
import { KIND_LABEL } from "./labels";
import { codeProblem, slugify } from "./slug";

/** Nieuwe organisatie: de code volgt de naam tot je hem zelf aanpast; de hint toont het echte adres. */
/** `initial`: vooraf ingevuld, bijvoorbeeld vanuit een aanvraag voor een eigen omgeving (ADR 0028). */
export function NewOrgForm({ hostPattern, reserved, taken, initial }: { hostPattern: string | null; reserved: string[]; taken: string[]; initial?: { name: string; code: string; kind: string } }) {
  const [name, setName] = useState(initial?.name.slice(0, 80) ?? "");
  const [code, setCode] = useState(initial?.code ?? "");
  const [touched, setTouched] = useState(Boolean(initial?.code));
  const shown = touched ? code : slugify(name);
  const problem = codeProblem(shown, reserved, taken);
  const host = hostPattern ? hostPattern.replace("{slug}", shown || "code") : null;
  return (
    <form action={createOrganization} className="grid-form">
      <label className="field"><span>Naam</span>
        <input name="name" required minLength={2} maxLength={80} placeholder="Basisschool De Regenboog" value={name} onChange={(e) => setName(e.target.value)} />
      </label>
      <label className="field"><span>Code</span>
        <input name="slug" required maxLength={32} className="mono" placeholder="de-regenboog" value={shown} spellCheck={false} autoCapitalize="none" autoCorrect="off"
          aria-invalid={problem ? true : undefined} aria-describedby="code-hint"
          onChange={(e) => { setTouched(true); setCode(e.target.value.toLowerCase()); }} />
      </label>
      <label className="field"><span>Soort</span>
        <select name="kind" defaultValue={["school", "opvang", "vereniging", "bedrijf", "overig"].includes(initial?.kind ?? "") ? initial!.kind : "school"}>
          {(["school", "opvang", "vereniging", "bedrijf", "overig"] as const).map((k) => <option key={k} value={k}>{KIND_LABEL[k]}</option>)}
        </select>
      </label>
      <small id="code-hint" className="lead wide" aria-live="polite">
        {problem ? <span className="bad">{problem}</span> : host ? <>Adres: <code>{host}</code>. </> : null}
        {!problem && "De code is later niet te wijzigen. Een nieuwe organisatie toont eerst alle platen, zonder webshop."}
      </small>
      <div><button type="submit" disabled={!!problem || !shown}>Aanmaken</button></div>
    </form>
  );
}
