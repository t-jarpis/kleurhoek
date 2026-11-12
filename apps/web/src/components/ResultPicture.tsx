import { useId } from "react";

/**
 * ResultPicture uit het design system (ADR 0100): "Zo wordt het", het werkstuk zoals het wordt, naast de stappen
 * van een bouwplaat. `svg` komt uit lib/result.ts (met role="img" en alt-tekst).
 */
export function ResultPicture({ svg, title }: { svg: string; title: string }) {
  const id = `result-${useId().replace(/[^a-zA-Z0-9]/g, "")}`;
  return (
    <figure className="kh-result-block" aria-labelledby={id}>
      <h3 id={id}>{title}</h3>
      <div className="kh-result-paper" dangerouslySetInnerHTML={{ __html: svg }} />
    </figure>
  );
}
