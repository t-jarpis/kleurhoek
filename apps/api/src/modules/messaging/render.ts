import { createRequire } from "node:module";
import type { Block, I18nText, Topic } from "./messaging.types";

/**
 * Van template naar mail (ADR 0037, design system: Mailtemplate). Tabellen en inline stijlen, want mailprogramma's
 * kennen geen moderne CSS; kleuren en maten uit packages/theme (generated/email.json). Geen trackingpixels en geen
 * externe lettertypen. Pure functie: alle gegevens (platen, links) komen van buiten.
 */
const tokens = createRequire(__filename)("@kleurhoek/theme/email.json") as {
  font: string; color: Record<string, string>; radius: { control: string; card: string }; logo: { word: string; blocks: string[] };
};
const C = tokens.color;

export interface RenderPlate { name: string; url: string; image: string }
export interface RenderInput {
  subject: I18nText; preheader: I18nText; blocks: Block[]; language: string;
  /** Platen per platenblok (id), al opgezocht en in de taal van de mail. */
  plates: Record<string, RenderPlate[]>;
  links: { site: string; preferences: string; unsubscribe: string; confirm?: string | undefined };
  topics: Topic[];
  /** Geen voettekst met afmelden (bevestigingsmail: er is nog geen abonnement). */
  transactional?: boolean | undefined;
}
export interface RenderedMail { subject: string; html: string; text: string }

const FOOTER: Record<string, { why: (topics: string) => string; confirmWhy: string; prefs: string; unsubscribe: string; topics: Record<Topic, string> }> = {
  nl: { why: (t) => `Je krijgt deze mail omdat je je hebt aangemeld voor ${t} bij Kleurhoek.`, confirmWhy: "Je krijgt deze mail omdat iemand dit adres heeft opgegeven bij Kleurhoek. Was jij dat niet? Dan hoef je niets te doen.", prefs: "Voorkeuren", unsubscribe: "Afmelden", topics: { "nieuwe-platen": "nieuwe platen", feestdagen: "feestdagen", nieuwsbrief: "de nieuwsbrief" } },
  de: { why: (t) => `Du bekommst diese Mail, weil du dich bei Kleurhoek für ${t} angemeldet hast.`, confirmWhy: "Du bekommst diese Mail, weil jemand diese Adresse bei Kleurhoek angegeben hat. Warst du das nicht? Dann musst du nichts tun.", prefs: "Einstellungen", unsubscribe: "Abmelden", topics: { "nieuwe-platen": "neue Vorlagen", feestdagen: "Feiertage", nieuwsbrief: "den Newsletter" } },
  en: { why: (t) => `You're getting this email because you signed up for ${t} at Kleurhoek.`, confirmWhy: "You're getting this email because someone entered this address at Kleurhoek. If that wasn't you, there's nothing you need to do.", prefs: "Preferences", unsubscribe: "Unsubscribe", topics: { "nieuwe-platen": "new pages", feestdagen: "holidays", nieuwsbrief: "the newsletter" } },
  fr: { why: (t) => `Vous recevez cet e-mail car vous vous êtes inscrit à ${t} sur Kleurhoek.`, confirmWhy: "Vous recevez cet e-mail car quelqu'un a saisi cette adresse sur Kleurhoek. Si ce n'était pas vous, vous n'avez rien à faire.", prefs: "Préférences", unsubscribe: "Se désinscrire", topics: { "nieuwe-platen": "nouveaux coloriages", feestdagen: "fêtes", nieuwsbrief: "la newsletter" } },
  es: { why: (t) => `Recibes este correo porque te has suscrito a ${t} en Kleurhoek.`, confirmWhy: "Recibes este correo porque alguien ha introducido esta dirección en Kleurhoek. Si no has sido tú, no tienes que hacer nada.", prefs: "Preferencias", unsubscribe: "Darse de baja", topics: { "nieuwe-platen": "nuevos dibujos", feestdagen: "fiestas", nieuwsbrief: "el boletín" } },
  it: { why: (t) => `Ricevi questa email perché ti sei iscritto a ${t} su Kleurhoek.`, confirmWhy: "Ricevi questa email perché qualcuno ha inserito questo indirizzo su Kleurhoek. Se non sei stato tu, non devi fare nulla.", prefs: "Preferenze", unsubscribe: "Annulla iscrizione", topics: { "nieuwe-platen": "nuovi disegni", feestdagen: "feste", nieuwsbrief: "la newsletter" } },
  pl: { why: (t) => `Otrzymujesz tę wiadomość, ponieważ zapisałeś się na ${t} w Kleurhoek.`, confirmWhy: "Otrzymujesz tę wiadomość, ponieważ ktoś podał ten adres w Kleurhoek. Jeśli to nie ty, nie musisz nic robić.", prefs: "Ustawienia", unsubscribe: "Wypisz się", topics: { "nieuwe-platen": "nowe plansze", feestdagen: "święta", nieuwsbrief: "newsletter" } },
};
const AND: Record<string, string> = { nl: "en", de: "und", en: "and", fr: "et", es: "y", it: "e", pl: "i" };

/** Tekst in de taal van de mail, anders Nederlands, anders de eerste. */
export const pick = (t: I18nText | undefined, lang: string) => (t ? t[lang] || t.nl || Object.values(t)[0] || "" : "");

const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

/** Alleen http(s), mailto en de vaste variabelen; de rest wordt de site. */
function safeUrl(url: string, links: RenderInput["links"]): string {
  const u = fill(url.trim(), links);
  return /^(https?:\/\/|mailto:)/i.test(u) ? u : links.site;
}
const fill = (s: string, links: RenderInput["links"]) => s
  .replace(/\{\{\s*site\s*\}\}/g, links.site).replace(/\{\{\s*voorkeuren\s*\}\}/g, links.preferences)
  .replace(/\{\{\s*afmelden\s*\}\}/g, links.unsubscribe).replace(/\{\{\s*bevestigen\s*\}\}/g, links.confirm ?? links.site);

/** Eenvoudige opmaak: lege regel = alinea, **vet**, [tekst](link). Al het andere is platte tekst. */
function inline(src: string, links: RenderInput["links"]): string {
  return esc(src)
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (_m, label: string, url: string) => `<a href="${esc(safeUrl(url.replace(/&amp;/g, "&"), links))}" style="color:${C["color-accent"]};text-decoration:underline">${label}</a>`)
    .replace(/\n/g, "<br>");
}
const plain = (src: string, links: RenderInput["links"]) => src.replace(/\*\*(.+?)\*\*/g, "$1").replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (_m, label: string, url: string) => `${label} (${safeUrl(url, links)})`);

const font = `font-family:${tokens.font.replace(/"/g, "'")}`;

function blockHtml(b: Block, input: RenderInput): string {
  const { language: lang, links } = input;
  switch (b.type) {
    case "heading":
      return `<tr><td style="padding:24px 32px 4px;${font};font-size:24px;line-height:1.2;font-weight:800;color:${C["color-text"]}">${esc(pick(b.text, lang))}</td></tr>`;
    case "text":
      return pick(b.text, lang).split(/\n{2,}/).filter((p) => p.trim()).map((p) =>
        `<tr><td style="padding:8px 32px;${font};font-size:16px;line-height:1.6;color:${C["color-text"]}">${inline(p.trim(), links)}</td></tr>`).join("");
    case "button":
      return `<tr><td style="padding:16px 32px"><table role="presentation" cellspacing="0" cellpadding="0" border="0"><tr><td style="border-radius:${tokens.radius.control};background:${C["color-primary"]}">`
        + `<a href="${esc(safeUrl(b.url, links))}" style="display:inline-block;padding:12px 20px;${font};font-size:16px;font-weight:700;color:${C["color-text-on-primary"]};text-decoration:none;border-radius:${tokens.radius.control}">${esc(pick(b.label, lang))}</a>`
        + `</td></tr></table></td></tr>`;
    case "divider":
      return `<tr><td style="padding:16px 32px"><div style="border-top:1px solid ${C["color-border"]};height:1px;line-height:1px;font-size:1px">&nbsp;</div></td></tr>`;
    case "plates": {
      const list = (input.plates[b.id] ?? []).slice(0, b.max);
      if (!list.length) return "";
      const cols = b.columns, width = Math.floor(536 / cols) - 12;
      const rows: string[] = [];
      for (let i = 0; i < list.length; i += cols) {
        const cells = list.slice(i, i + cols).map((p) => `<td width="${Math.floor(100 / cols)}%" valign="top" style="padding:6px">`
          + `<a href="${esc(p.url)}" style="text-decoration:none;color:${C["color-text"]}"><img src="${esc(p.image)}" width="${width}" alt="${esc(p.name)}" style="display:block;width:100%;max-width:${width}px;height:auto;border:1px solid ${C["color-border"]};border-radius:${tokens.radius.card};background:${C["color-paper"]}">`
          + `<span style="display:block;padding-top:6px;${font};font-size:15px;line-height:1.3;font-weight:700;color:${C["color-text"]}">${esc(p.name)}</span></a></td>`);
        while (cells.length < cols) cells.push(`<td width="${Math.floor(100 / cols)}%"></td>`);
        rows.push(`<tr>${cells.join("")}</tr>`);
      }
      return `<tr><td style="padding:8px 26px"><table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">${rows.join("")}</table></td></tr>`;
    }
  }
}

function blockText(b: Block, input: RenderInput): string {
  const { language: lang, links } = input;
  switch (b.type) {
    case "heading": return pick(b.text, lang).toUpperCase();
    case "text": return plain(pick(b.text, lang), links);
    case "button": return `${pick(b.label, lang)}: ${safeUrl(b.url, links)}`;
    case "divider": return "----";
    case "plates": return (input.plates[b.id] ?? []).slice(0, b.max).map((p) => `- ${p.name}: ${p.url}`).join("\n");
  }
}

const logo = () => `<table role="presentation" cellspacing="0" cellpadding="0" border="0"><tr>`
  + `<td style="padding-right:8px"><table role="presentation" cellspacing="2" cellpadding="0" border="0"><tr>${tokens.logo.blocks.slice(0, 2).map((b) => `<td width="10" height="10" style="background:${C[b]};border-radius:2px;font-size:1px;line-height:1px">&nbsp;</td>`).join("")}</tr>`
  + `<tr>${tokens.logo.blocks.slice(2, 4).map((b) => `<td width="10" height="10" style="background:${C[b]};border-radius:2px;font-size:1px;line-height:1px">&nbsp;</td>`).join("")}</tr></table></td>`
  + `<td style="${font};font-size:24px;font-weight:800;letter-spacing:-0.03em;color:${C["color-text"]}">${esc(tokens.logo.word)}</td></tr></table>`;

export function renderMail(input: RenderInput): RenderedMail {
  const lang = FOOTER[input.language] ? input.language : "nl";
  const f = FOOTER[lang]!;
  const subject = fill(pick(input.subject, lang), input.links).slice(0, 200);
  const preheader = fill(pick(input.preheader, lang), input.links);
  const named = input.topics.map((t) => f.topics[t]);
  const topicText = named.length > 1 ? `${named.slice(0, -1).join(", ")} ${AND[lang]} ${named.at(-1)}` : named[0] ?? f.topics.nieuwsbrief;
  const footer = input.transactional
    ? `<p style="margin:0">${esc(f.confirmWhy)}</p>`
    : `<p style="margin:0 0 8px">${esc(f.why(topicText))}</p><p style="margin:0"><a href="${esc(input.links.preferences)}" style="color:${C["color-text-muted"]}">${esc(f.prefs)}</a> · <a href="${esc(input.links.unsubscribe)}" style="color:${C["color-text-muted"]}">${esc(f.unsubscribe)}</a></p>`;
  const body = input.blocks.map((b) => blockHtml(b, { ...input, language: lang })).join("\n");
  const html = `<!doctype html>
<html lang="${lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><meta name="supported-color-schemes" content="light"><title>${esc(subject)}</title></head>
<body style="margin:0;padding:0;background:${C["color-bg"]}">
<div style="display:none;max-height:0;overflow:hidden;opacity:0">${esc(preheader)}</div>
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background:${C["color-bg"]}"><tr><td align="center" style="padding:24px 12px">
<table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="width:100%;max-width:600px">
<tr><td style="padding:0 8px 16px"><a href="${esc(input.links.site)}" style="text-decoration:none">${logo()}</a></td></tr>
<tr><td style="background:${C["color-surface"]};border:1px solid ${C["color-border"]};border-radius:${tokens.radius.card};padding:8px 0 24px">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
${body}
</table></td></tr>
<tr><td style="padding:16px 8px;${font};font-size:13px;line-height:1.5;color:${C["color-text-muted"]}">${footer}</td></tr>
</table></td></tr></table>
</body></html>
`;
  const text = [
    ...input.blocks.map((b) => blockText(b, { ...input, language: lang })).filter(Boolean),
    "",
    "--",
    input.transactional ? f.confirmWhy : `${f.why(topicText)}\n${f.prefs}: ${input.links.preferences}\n${f.unsubscribe}: ${input.links.unsubscribe}`,
  ].join("\n\n");
  return { subject, html, text };
}
