/**
 * Teksten voor de voorstellen (ADR 0063), in het Nederlands voor kleurhoek.nl. Vaste sjablonen met wat variatie,
 * geen AI-tekstgenerator: Thijs keurt alles goed en kan elke tekst aanpassen. Nooit "zelf getekend" of "met de hand".
 */
export interface PlateInfo { slug: string; name: string; category: string; categoryName: string; age: string; ageName: string; holiday: string | null; kind: string }

export const KIND: Record<string, string> = {
  kleurplaat: "kleurplaat", werkblad: "werkblad", knipplaat: "knipplaat", bouwplaat: "bouwplaat", kaart: "kaart om te maken",
  tekenles: "tekenles", spel: "spel om te printen", vouwblad: "vouwblad", sjabloon: "sjabloon",
};
const CRAFT = new Set(["knipplaat", "bouwplaat", "vouwblad", "kaart", "sjabloon"]);
const LEARN = new Set(["werkblad", "spel"]);

/** Seizoensplaten voor de borden Winter en Herfst (zelfde keuze als het CSV-bestand en de aftelkalender). */
export const WINTER = new Set(["sneeuwpop", "ijsbeer", "muts-en-wanten", "pinguins", "sleetje-trekken", "sneeuwvlok-knippen", "schaatser", "poolvos", "sneeuwballen-gooien", "iglo", "tekenles-sneeuwpop", "noorderlicht", "winterjas", "sneeuwuil", "skier", "pinguin-koker", "tekenles-pinguin", "doolhof-pinguin-ijsschots", "pixelkunst-pinguin", "hert", "volgorde-sneeuwpop-smelt", "woord-raden-sneeuwpop"]);
export const HERFST = new Set(["egel", "paddenstoel", "boom", "eekhoorn", "vos", "uil", "appelboom", "doolhof-eekhoorn-eikel", "tekenles-vos", "masker-vos", "masker-uil", "vosmasker"]);

/** Op welk Pinterest-bord een plaat komt. */
export function boardOf(p: PlateInfo): string {
  if (p.holiday === "sinterklaas") return "Sinterklaas kleurplaten en knutsels";
  if (p.holiday === "kerst" || p.holiday === "chanoeka") return "Kerst kleurplaten en knutsels";
  if (p.holiday === "oudnieuw") return "Oud en nieuw met kinderen";
  if (p.holiday === "sintmaarten") return "Sint-Maarten lampionnen en kleurplaten";
  if (p.holiday === "pasen") return "Pasen kleurplaten en knutsels";
  if (p.holiday) return "Feestdagen met kinderen";
  if (WINTER.has(p.slug)) return "Winter kleurplaten";
  if (HERFST.has(p.slug)) return "Herfst kleurplaten";
  if (LEARN.has(p.kind)) return "Werkbladen voor kleuters en groep 3";
  if (CRAFT.has(p.kind)) return "Knutselen met kinderen";
  if (p.kind === "tekenles") return "Leren tekenen voor kinderen";
  return `Kleurplaten ${p.categoryName.toLowerCase()}`;
}

export function pinText(p: PlateInfo): { title: string; description: string; alt: string } {
  const k = KIND[p.kind] ?? "kleurplaat";
  const description = ({
    kleurplaat: `Gratis kleurplaat '${p.name}' voor kinderen van ${p.ageName}. Print hem op A4 of kleur hem online in, zonder account.`,
    werkblad: `Gratis werkblad '${p.name}' voor ${p.ageName}, voor thuis of in de klas. Print op A4, met antwoordblad waar dat nodig is.`,
    spel: `Gratis spel om te printen: '${p.name}', voor ${p.ageName}. Thuis of in de klas, print op A4.`,
    tekenles: `Leer stap voor stap tekenen: '${p.name}', voor ${p.ageName}. Gratis om te printen op A4.`,
  } as Record<string, string>)[p.kind] ?? `Gratis ${k}: '${p.name}', voor ${p.ageName}. Print op A4, met uitleg en wat je nodig hebt.`;
  return { title: `${p.name} – gratis ${k}`.slice(0, 100), description: `${description} Elke plaat is een eigen ontwerp van Kleurhoek.`, alt: `${k[0]!.toUpperCase()}${k.slice(1)}: ${p.name}` };
}

const pick = <T,>(list: T[], seed: number) => list[Math.abs(seed) % list.length]!;
const hash = (s: string) => [...s].reduce((h, c) => (h * 31 + c.charCodeAt(0)) | 0, 7);

export type FeedKind = "feestdag" | "aftelkalender" | "lespakket" | "knutselen" | "plaat";
export interface FeedText { facebook: string; instagram: string; share: string; title: string }

/** Tekst voor Facebook (met link), Instagram (link in bio, hashtags) en om te delen in groepen en WhatsApp. */
export function feedText(kind: FeedKind, ctx: { day: string; link: string; plate: PlateInfo; holidayName?: string | undefined; days?: number | undefined; door?: number | undefined }): FeedText {
  const seed = hash(ctx.day + kind);
  const p = ctx.plate;
  const short = ctx.link.replace(/^https?:\/\/(www\.)?/, "");
  let lead: string; let title: string; let tags: string[];
  switch (kind) {
    case "feestdag": {
      const when = ctx.days === 1 ? "morgen" : `over ${ctx.days} dagen`;
      title = `${ctx.holidayName}: kleurplaten en knutsels`;
      lead = pick([
        `Het is ${when} ${ctx.holidayName}! 🎉 Zoek je nog iets om samen te doen? Op Kleurhoek staan gratis kleurplaten en knutselplaten voor ${ctx.holidayName}, bijvoorbeeld '${p.name}'. Online kleuren of printen op A4, zonder account.`,
        `Nog ${ctx.days === 1 ? "één nachtje" : `${ctx.days} nachtjes`} tot ${ctx.holidayName} ✨ Wij hebben gratis platen klaargezet om in te kleuren en te knutselen, zoals '${p.name}'. Print ze op A4 of kleur online.`,
      ], seed);
      tags = ["kleurplaat", "kleurplaten", ctx.holidayName!.toLowerCase().replace(/[^a-z0-9]/g, ""), "knutselen", "metkinderen"];
      break;
    }
    case "aftelkalender":
      title = `Aftelkalender: deurtje ${ctx.door}`;
      lead = pick([
        `Deurtje ${ctx.door} van de aftelkalender is open! 🎄 Elke dag in december een nieuwe gratis plaat om te kleuren of te knutselen.`,
        `Vandaag gaat deurtje ${ctx.door} open 🎁 Kijk wat erachter zit in de gratis aftelkalender van Kleurhoek: elke dag een nieuwe plaat.`,
      ], seed);
      tags = ["aftelkalender", "adventskalender", "kleurplaat", "december", "kerst"];
      break;
    case "lespakket":
      title = `Lespakket ${p.categoryName.toLowerCase()}, ${p.ageName}`;
      lead = pick([
        `Voor juffen en meesters 🍎 Een gratis lespakket ${p.categoryName.toLowerCase()} voor ${p.ageName}: kleurplaten, werkbladen en een knutselplaat, met de leerdoelen erbij. In één keer te printen als boekje.`,
        `Lesidee voor deze week: ${p.categoryName.toLowerCase()} ✏️ Een kant-en-klaar pakket voor ${p.ageName} met kleurplaten, werkbladen en iets om te knutselen. Gratis, print alles in één keer.`,
      ], seed);
      tags = ["lespakket", "onderwijs", "kleuterklas", "groep3", "werkblad", "juf"];
      break;
    case "knutselen":
      title = `Knutselen: ${p.name}`;
      lead = pick([
        `Weekendplan? ✂️ Knutsel '${p.name}', gratis te printen op A4. Op de pagina staat precies wat je nodig hebt.`,
        `Iets om samen te maken dit weekend: '${p.name}' 🧩 Print, knip en plak. Gratis, met uitleg erbij.`,
      ], seed);
      tags = ["knutselen", "knutselenmetkinderen", "printable", "kinderactiviteit"];
      break;
    default:
      title = p.name;
      lead = pick([
        `Plaat van de week: '${p.name}' 🖍️ Gratis om te printen op A4 of online in te kleuren. Voor kinderen van ${p.ageName}.`,
        `Zin om te kleuren? '${p.name}' staat klaar 🎨 Online kleuren kan ook, met penselen die binnen de lijnen blijven.`,
        `Nieuw om in te kleuren: '${p.name}' ✨ Gratis te printen, geen account nodig.`,
      ], seed);
      tags = ["kleurplaat", "kleurplaten", p.categoryName.toLowerCase().replace(/[^a-z0-9]/g, ""), "kleuren", "metkinderen"];
  }
  const hashtags = tags.map((t) => `#${t}`).join(" ");
  return {
    title,
    facebook: `${lead}\n\n👉 ${ctx.link}`,
    instagram: `${lead}\n\nLink in bio · ${short}\n\n${hashtags}`,
    share: `${lead}\n${ctx.link}`,
  };
}
