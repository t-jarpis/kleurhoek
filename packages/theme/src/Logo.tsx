import { activeTheme } from "../generated/theme";

/** Beeldmerk van het thema: blokjes in de krijtkleuren uit het thema. */
export function LogoMark({ size = 30 }: { size?: number }) {
  return (
    <span className="kh-logo-mark" aria-hidden="true" style={{ width: size, height: size }}>
      {activeTheme.logo.blocks.map((token) => <i key={token} style={{ background: `var(--${token})` }} />)}
    </span>
  );
}

/**
 * Logo. Standaard het beeldmerk van het thema plus het woordmerk. Een organisatie kan een eigen
 * woordmerk (naam) of een eigen logo-afbeelding hebben (ADR 0017); die komt dan in de plaats.
 * De link en de toegankelijke naam geeft de app zelf.
 */
export function Logo({ suffix, size = 30, wordmark, image }: { suffix?: string; size?: number; wordmark?: string | null; image?: string | null }) {
  return (
    <span className="kh-logo">
      {image
        ? <img className="kh-logo-img" src={image} alt="" style={{ height: size * 1.4 }} />
        : <><LogoMark size={size} /><span className="kh-logo-word" style={{ fontSize: size }}>{wordmark ?? activeTheme.logo.word}</span></>}
      {suffix && <span className="kh-logo-suffix">{suffix}</span>}
    </span>
  );
}
