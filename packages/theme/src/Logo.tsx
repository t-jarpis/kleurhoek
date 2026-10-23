import { activeTheme } from "../generated/theme";

/** Beeldmerk van het actieve thema: blokjes in de krijtkleuren uit het thema. */
export function LogoMark({ size = 30 }: { size?: number }) {
  return (
    <span className="kh-logo-mark" aria-hidden="true" style={{ width: size, height: size }}>
      {activeTheme.logo.blocks.map((token) => <i key={token} style={{ background: `var(--${token})` }} />)}
    </span>
  );
}

/** Logo: beeldmerk plus woordmerk. Toegankelijke naam "Kleurhoek"; de link geeft de app zelf. */
export function Logo({ suffix, size = 30 }: { suffix?: string; size?: number }) {
  return (
    <span className="kh-logo">
      <LogoMark size={size} />
      <span className="kh-logo-word" style={{ fontSize: size }}>{activeTheme.logo.word}</span>
      {suffix && <span className="kh-logo-suffix">{suffix}</span>}
    </span>
  );
}
