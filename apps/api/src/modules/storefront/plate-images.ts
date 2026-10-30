import { readdirSync } from "node:fs";
import { createRequire } from "node:module";
import { join } from "node:path";
import { Injectable, Logger, type OnModuleInit } from "@nestjs/common";
import { encode as encodeJpeg } from "jpeg-js";

type ResvgModule = typeof import("@resvg/resvg-js");

/** Lettertypen voor de PNG's: Nunito (Latijn, Latijn-uitgebreid, Cyrillisch) en Grieks uit Manrope, als TTF. */
const FONT_DIR = join(__dirname, "..", "..", "..", "fonts");

/**
 * PNG van een plaat, voor mails (ADR 0037), deelplaatjes (ADR 0055) en Pinterest (ADR 0057). Gemaakt met resvg,
 * met het lettertype van de platen. De lettertypen staan als complete TTF-bestanden in apps/api/fonts, samengevoegd
 * uit de subsets van packages/theme (ADR 0062). Losse subsets met dezelfde naam gaven in productie geen tekst of
 * blokjes: resvg koos er één en vond daar de letters niet in. Adres per versie en taal, dus eeuwig te cachen.
 */
@Injectable()
export class PlateImages implements OnModuleInit {
  private readonly log = new Logger(PlateImages.name);
  private resvg: ResvgModule | null = null;
  private readonly fonts = readdirSync(FONT_DIR).filter((f) => f.endsWith(".ttf")).map((f) => join(FONT_DIR, f));
  private readonly cache = new Map<string, Buffer>();

  private render(svg: string, width: number): Buffer {
    this.resvg ??= createRequire(__filename)("@resvg/resvg-js") as ResvgModule;
    const r = new this.resvg.Resvg(svg, { fitTo: { mode: "width", value: width }, background: "#ffffff", font: { fontFiles: this.fonts, loadSystemFonts: false, defaultFontFamily: "Nunito" } });
    return Buffer.from(r.render().asPng());
  }

  /**
   * Tekent resvg echt letters? Zonder lettertype komt er niets, met een verkeerd lettertype een rij blokjes. In
   * beide gevallen zien "iiii", "WWWW" en niets er hetzelfde uit; met echte letters verschillen ze.
   */
  textWorks(sample = ["iiii", "WWWW"]): boolean {
    const svg = (t: string) => `<svg xmlns="http://www.w3.org/2000/svg" width="120" height="30"><text x="4" y="22" font-family="Nunito" font-size="20" fill="#000">${t}</text></svg>`;
    const [a, b, none] = [this.render(svg(sample[0]!), 120), this.render(svg(sample[1]!), 120), this.render(svg(""), 120)];
    return !a.equals(none) && !b.equals(none) && !a.equals(b);
  }

  onModuleInit() {
    // Melden als er geen tekst op de plaatjes komt (in de logs van de container).
    setTimeout(() => {
      try { if (!this.textWorks()) this.log.error("PNG-plaatjes tekenen geen tekst: lettertypen niet geladen"); }
      catch (e) { this.log.error(`PNG-plaatjes werken niet: ${e}`); }
    }, 0).unref();
  }

  /** JPEG voor Instagram, dat geen PNG aanneemt (ADR 0063). */
  async jpeg(key: string, svg: string, width: number): Promise<Buffer> {
    const hit = this.cache.get(`jpg:${key}`);
    if (hit) return hit;
    this.resvg ??= createRequire(__filename)("@resvg/resvg-js") as ResvgModule;
    const img = new this.resvg.Resvg(svg, { fitTo: { mode: "width", value: width }, background: "#ffffff", font: { fontFiles: this.fonts, loadSystemFonts: false, defaultFontFamily: "Nunito" } }).render();
    const jpg = Buffer.from(encodeJpeg({ data: Buffer.from(img.pixels), width: img.width, height: img.height }, 88).data);
    if (this.cache.size > 200) this.cache.clear();
    this.cache.set(`jpg:${key}`, jpg);
    return jpg;
  }

  async png(key: string, svg: string, width = 400): Promise<Buffer> {
    const hit = this.cache.get(key);
    if (hit) return hit;
    const png = this.render(svg, width);
    if (this.cache.size > 200) this.cache.clear();
    this.cache.set(key, png);
    return png;
  }
}
