import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { Injectable } from "@nestjs/common";

/**
 * PNG van een plaat, voor mails (ADR 0037): mailprogramma's tonen geen SVG. Gemaakt met resvg, met het
 * lettertype van de platen (Nunito, uit packages/theme). Adres per versie en taal, dus eeuwig te cachen.
 */
@Injectable()
export class PlateImages {
  private fonts: Promise<Buffer[]> | null = null;
  private readonly cache = new Map<string, Buffer>();

  private loadFonts(): Promise<Buffer[]> {
    this.fonts ??= (async () => {
      const req = createRequire(__filename);
      const woff2 = req("wawoff2") as { decompress: (b: Buffer) => Promise<Uint8Array> };
      const fonts = join(dirname(req.resolve("@kleurhoek/theme/manifest.json")), "..", "fonts");
      // Alle tekensets (ADR 0052): latin-ext voor Pools, Tsjechisch …, Cyrillisch, en Grieks uit Manrope (Nunito heeft geen Grieks).
      const files = [
        ...["latin", "latin-ext", "cyrillic"].flatMap((s) => ["400", "600", "700"].map((w) => join(fonts, "nunito", `nunito-${s}-${w}-normal.woff2`))),
        ...["400", "700"].map((w) => join(fonts, "manrope", `manrope-greek-${w}-normal.woff2`)),
      ];
      return Promise.all(files.map(async (f) => Buffer.from(await woff2.decompress(readFileSync(f)))));
    })();
    return this.fonts;
  }

  async png(key: string, svg: string, width = 400): Promise<Buffer> {
    const hit = this.cache.get(key);
    if (hit) return hit;
    const { Resvg } = createRequire(__filename)("@resvg/resvg-js") as typeof import("@resvg/resvg-js");
    const fontBuffers = await this.loadFonts();
    // fontBuffers werkt in resvg-js 2.6, maar staat (nog) niet in de typen.
    const options = { fitTo: { mode: "width", value: width }, background: "#ffffff", font: { fontBuffers, loadSystemFonts: false, defaultFontFamily: "Nunito" } } as unknown as ConstructorParameters<typeof Resvg>[1];
    const png = new Resvg(svg, options).render().asPng();
    if (this.cache.size > 200) this.cache.clear();
    this.cache.set(key, png);
    return png;
  }
}
