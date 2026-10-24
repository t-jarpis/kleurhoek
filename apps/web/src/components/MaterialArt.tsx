import art from "./material-art.json";

const DRAWINGS: Record<string, string> = art;

/**
 * Eigen tekening van een materiaal op een papieren tegel (design system: MaterialArt). Lijnen in
 * plaatinkt, vlakken in krijtkleuren; decoratief, de naam staat ernaast. Geen tekening, geen tegel.
 */
export function MaterialArt({ slug }: { slug: string }) {
  const inner = DRAWINGS[slug];
  if (!inner) return null;
  return (
    <span className="kh-material-art" aria-hidden="true">
      <svg viewBox="0 0 48 48" fill="none" stroke="var(--plate-ink)" strokeWidth={1.8} strokeLinejoin="round" strokeLinecap="round" dangerouslySetInnerHTML={{ __html: inner }} />
    </span>
  );
}
