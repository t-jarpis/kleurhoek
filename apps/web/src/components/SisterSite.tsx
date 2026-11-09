import { SISTER_LINK, type SisterSite as Site } from "@/lib/sister-sites";

/**
 * SisterSite uit het design system (ADR 0098): één rustige tegel naar een eigen zustersite (nu Denkhoek), met het
 * beeldmerk van die site. `site` komt uit denkhoekFor(market); null = niets tonen.
 */
export function SisterSite({ site }: { site: Site | null }) {
  if (!site) return null;
  return (
    <aside className="kh-sister no-print" aria-labelledby="kh-sister-title">
      <span className="kh-logo-mark" aria-hidden="true">
        {site.blocks.map((token) => <i key={token} style={{ background: `var(--${token})` }} />)}
      </span>
      <div className="kh-sister-text">
        <h2 id="kh-sister-title">{site.title}</h2>
        <p>{site.text}</p>
      </div>
      <a className="ui-btn" href={site.url} {...SISTER_LINK}>{site.cta}</a>
    </aside>
  );
}

/** Eén regel in de voettekst: "Ook van ons: Denkhoek – gratis puzzels". */
export function SisterFooterLink({ site }: { site: Site | null }) {
  if (!site) return null;
  return <p><a href={site.url} {...SISTER_LINK}>{site.footer}</a></p>;
}
