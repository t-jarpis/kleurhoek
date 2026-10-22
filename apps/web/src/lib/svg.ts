/** De binnenkant van een plaat-SVG, zonder eigen stijlblok: de CSS van de site stijlt hem. */
export function svgInner(svg: string): string {
  return svg.replace(/^\s*<svg[^>]*>/, "").replace(/<\/svg>\s*$/, "").replace(/<style>[\s\S]*?<\/style>/g, "");
}
