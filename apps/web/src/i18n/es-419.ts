import type { Messages } from "./nl";

/**
 * Spaans voor Latijns-Amerika en de VS (es-MX, es-AR, es-CO, es-US; ADR 0050). Zelfde teksten als es.ts, maar
 * met "ustedes" in plaats van "vosotros", Latijns-Amerikaanse woorden en papier op Letter-formaat waar de markt
 * dat gebruikt. Alleen de teksten die verschillen staan hier.
 */
export function latamSpanish(es: Messages, letter: boolean): Messages {
  const words = (s: string) => s
    .replace(/\bel móvil\b/g, "el celular").replace(/\bel ordenador\b/g, "la computadora")
    .replace(/\brellene\b/g, "llene").replace(/\bRellenas\b/g, "Llenas")
    .replace(/\bA4\b/g, letter ? "tamaño carta" : "A4");
  const fix = <T,>(v: T): T => (typeof v === "string" ? words(v) as T
    : typeof v === "function" ? ((...a: unknown[]) => fix((v as (...a: unknown[]) => unknown)(...a))) as T
    : Array.isArray(v) ? v.map(fix) as T
    : v && typeof v === "object" ? Object.fromEntries(Object.entries(v).map(([k, x]) => [k, fix(x)])) as T : v);
  return {
    ...fix(es),
    ownLede: "Una versión propia de Kleurhoek, con su nombre, sus colores y justo los dibujos que encajan con el uso que les van a dar. Los dibujos y el mantenimiento corren por nuestra cuenta.",
    ownForWhoText: "Escuelas de preescolar y primaria, guarderías y centros de actividades extraescolares, asociaciones, bibliotecas y empresas con un rincón infantil, como una sala de espera o un evento.",
    ownBenefits: [
      ["Una dirección propia", "Su espacio tiene su propia dirección, como elarcoiris.kleurhoek.nl. También puede ser un dominio propio."],
      ["Su imagen", "Su nombre o logotipo y sus colores. Nos aseguramos de que todo se lea bien."],
      ["Sin nuestro nombre en los dibujos", "En nuestro sitio aparece kleurhoek.nl en pequeño bajo cada dibujo, también en papel. En su espacio, no."],
      ["La oferta que les queda", "Elijan los temas, las edades, los objetivos de aprendizaje y los tipos de actividades, o armen su propia colección."],
      ["Solo los dibujos", "Si quieren, sin enlaces a tiendas ni de afiliados, para que solo queden los dibujos."],
      ["Ustedes lo ajustan", "Desde «Gestión» en su propio sitio activan o desactivan objetivos, colecciones y dibujos sueltos."],
      ["Solo para quien tenga la dirección", "Su espacio no aparece en los buscadores. Quien tenga la dirección puede empezar enseguida."],
    ] as [string, string][],
    ownSteps: [
      "Llenas el formulario de abajo.",
      "Nos ponemos en contacto contigo en unos pocos días hábiles y hablamos de lo que necesitan y de lo que cuesta.",
      "Preparamos su espacio y te damos la dirección. Desde ese momento pueden empezar.",
    ],
    orgKinds: { ...es.orgKinds, school: "Escuela" },
    orgMessage: "¿Qué les gustaría?",
    orgMessagePlaceholder: "Por ejemplo: para preescolar y 1.º de primaria, con nuestro logotipo, sin manualidades.",
  };
}
