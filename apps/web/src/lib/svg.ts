/** De binnenkant van een plaat-SVG, zonder eigen stijlblok: de CSS van de site stijlt hem. */
export function svgInner(svg: string): string {
  return svg.replace(/^\s*<svg[^>]*>/, "").replace(/<\/svg>\s*$/, "").replace(/<style>[\s\S]*?<\/style>/g, "");
}

/** Hoogte uit de viewBox ("0 0 200 270" → 270); 200 als die ontbreekt. */
export function svgHeight(svg: string): number {
  const m = /viewBox="0 0 200 (\d+(?:\.\d+)?)"/.exec(svg);
  return m ? Number(m[1]) : 200;
}
