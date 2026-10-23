"use client";
import { checkAccent, checkPrimary, ratio, type ColorCheck } from "@kleurhoek/theme";
import { useId } from "react";

const HEX = /^#[0-9a-f]{6}$/i;

/** Uitkomst van de contrastcontrole: goed, alleen licht (donker valt terug op het thema) of afgekeurd. */
export function judge(kind: "primary" | "accent", value: string): { ok: boolean | "warn"; text: string } | null {
  if (!value) return null;
  if (!HEX.test(value)) return { ok: false, text: "Gebruik #rrggbb, bijvoorbeeld uit de huisstijlgids." };
  const c: ColorCheck = kind === "primary" ? checkPrimary(value) : checkAccent(value);
  if (!c.ok) return { ok: false, text: `✕ ${c.message}` };
  const min = kind === "primary" ? 3 : 4.5;
  if (c.dark < min) return { ok: "warn", text: `Leesbaar in licht (${ratio(c.light)}:1). In donker te donker (${ratio(c.dark)}:1): daar blijft de themakleur.` };
  return { ok: true, text: `✓ Leesbaar: ${ratio(c.light)}:1 licht, ${ratio(c.dark)}:1 donker.` };
}

/** ColorField uit het design system: kleurvak, hexcode en direct het contrastoordeel. */
export function ColorField({ name, label, hint, kind, value, onChange }: {
  name: string; label: string; hint: string; kind: "primary" | "accent"; value: string; onChange: (v: string) => void;
}) {
  const id = useId();
  const verdict = judge(kind, value);
  return (
    <div className="ui-field ui-colorfield">
      <label htmlFor={id}>{label}</label>
      <div className="ui-colorfield-row">
        <input type="color" className="ui-colorfield-swatch" aria-label={`Kies ${label.toLowerCase()}`} value={HEX.test(value) ? value.toLowerCase() : ""} onChange={(e) => onChange(e.target.value)} />
        <input id={id} name={name} className="ui-input" value={value} maxLength={7} spellCheck={false} autoComplete="off"
          aria-invalid={verdict?.ok === false ? true : undefined} aria-describedby={`${id}-h ${id}-c`} onChange={(e) => onChange(e.target.value.trim())} />
      </div>
      <span id={`${id}-h`} className="ui-hint">{hint}</span>
      <span id={`${id}-c`} className="ui-colorfield-check" data-ok={verdict ? String(verdict.ok) : undefined} aria-live="polite">{verdict?.text ?? "Leeg: de kleur van het thema."}</span>
    </div>
  );
}
