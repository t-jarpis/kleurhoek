"use client";
import { brandCss, Logo } from "@kleurhoek/theme";
import { useState } from "react";
import { ColorField, judge } from "@/components/ColorField";
import type { Organization, OrgChoices } from "@/lib/api";
import { saveBrand } from "./actions";

/** Huisstijl kiezen met een live voorbeeld (BrandPreview): dezelfde brandCss als de website. */
export function BrandEditor({ org, themes, fonts, logo, canManage }: {
  org: Organization; themes: OrgChoices["themes"]; fonts: OrgChoices["fonts"]; logo: string | null; canManage: boolean;
}) {
  const [theme, setTheme] = useState(org.brand.theme ?? "");
  const [font, setFont] = useState(org.brand.font ?? "");
  const [primary, setPrimary] = useState(org.brand.colors.primary ?? "");
  const [accent, setAccent] = useState(org.brand.colors.accent ?? "");
  const [wordmark, setWordmark] = useState(org.brand.wordmark ?? "");
  const blocked = judge("primary", primary)?.ok === false || judge("accent", accent)?.ok === false;
  const themeFont = themes.find((t) => t.id === (theme || themes[0]?.id))?.font;
  const shownFont = font || themeFont;
  return (
    <div className="brand-editor">
      <form action={saveBrand} className="stack">
        <input type="hidden" name="slug" value={org.slug} />
        <fieldset disabled={!canManage} className="stack" style={{ border: 0, padding: 0, margin: 0 }}>
          <label className="field"><span>Thema</span>
            <select name="theme" value={theme} onChange={(e) => setTheme(e.target.value)}>
              <option value="">Standaard</option>
              {themes.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
            </select>
            <small>Vormen, randen en knoppen. Een nieuw thema komt als map in packages/theme/themes.</small>
          </label>
          <label className="field"><span>Lettertype</span>
            <select name="font" value={font} onChange={(e) => setFont(e.target.value)}>
              <option value="">Van het thema ({fonts.find((f) => f.id === themeFont)?.family ?? "standaard"})</option>
              {fonts.map((f) => <option key={f.id} value={f.id}>{f.family}</option>)}
            </select>
          </label>
          <ColorField name="primary" label="Hoofdkleur" kind="primary" value={primary} onChange={setPrimary} hint="Knoppen en gekozen filters." />
          <ColorField name="accent" label="Accentkleur" kind="accent" value={accent} onChange={setAccent} hint="Links en de focusring." />
          <label className="field"><span>Naam in het logo</span>
            <input name="wordmark" value={wordmark} maxLength={30} onChange={(e) => setWordmark(e.target.value)} placeholder="kleurhoek" />
            <small>Kleine letters staan het best. Een geüpload logo gaat voor.</small>
          </label>
          <div><button type="submit" disabled={blocked}>Huisstijl opslaan</button>{blocked && <span className="lead"> Pas eerst de afgekeurde kleur aan.</span>}</div>
        </fieldset>
      </form>

      <div className="stack">
        <style>{brandCss({ primary: judge("primary", primary)?.ok === false ? null : primary || null, accent: judge("accent", accent)?.ok === false ? null : accent || null }, "#voorbeeld")}</style>
        <div id="voorbeeld" className="ui-brandpreview" data-kh-scope data-mode="ouder" {...(shownFont ? { "data-kh-font": shownFont } : {})} inert>
          <span className="ui-brandpreview-label">Voorbeeld</span>
          <div className="ui-brandpreview-bar">
            <Logo size={26} wordmark={wordmark || null} image={logo} />
            <span className="ui-brandpreview-row">
              <span className="ui-btn">Maak een boekje</span>
              <span className="ui-btn" data-variant="primary">Verras me</span>
            </span>
          </div>
          <div className="ui-brandpreview-row">
            <span className="ui-chip" aria-pressed="true">Alles</span>
            <span className="ui-chip" aria-pressed="false">Dieren</span>
            <a href="#voorbeeld" tabIndex={-1}>Voor ouders</a>
          </div>
        </div>
        <p className="lead">Thema&apos;s gelden voor de hele site en zijn hier pas na opslaan te zien. Wissel licht en donker via je systeem om beide te controleren.</p>
      </div>
    </div>
  );
}
