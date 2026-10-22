"""Eenmalige migratie: haalt alle platen, categorieën, leeftijden, werelddelen en feestdagen
uit het prototype en schrijft ze naar packages/catalog-data. Draait de tekenfuncties in een
echte browser, zodat ook de nummerposities voor kleur-op-nummer exact kloppen.

Gebruik: python3 -I scripts/extract_prototype.py
"""
import asyncio, json, pathlib
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "prototype" / "kleurhoek-standalone.html"
OUT = ROOT / "packages" / "catalog-data"

JS = r"""() => {
  const plates = PAGES.map((p, order) => {
    let i = 0;
    const body = p.draw().replace(/class="r"/g, () => `class="r" data-i="${i++}"`);
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">${body}</svg>`;
    const labels = computeLabels(p).map(l => ({ region: l.i, number: l.num, x: l.x, y: l.y, size: l.fs }));
    return {
      slug: p.id, order, category: p.cat, age: p.age,
      world: p.world ? { continent: p.world[0], country: p.world[1] || null } : null,
      holiday: p.hol || null,
      regionCount: p.n,
      colorByNumber: { codes: p.nums, palette: legendKeys(p).map(k => ({ code: k, hex: KEYS[k] })), labels },
      i18n: { "nl": { name: p.name, word: p.word || null, countQuestion: p.count || null } },
      svg,
    };
  });
  return {
    plates,
    categories: CATS.map((c, order) => ({ slug: c.id, order, color: c.c, i18n: { nl: { name: c.name } } })),
    ages: AGES.map((a, order) => ({ slug: a.id, order, level: a.lv, strokeWidth: a.sw, i18n: { nl: { name: a.name + ' jaar', hint: a.hint } } })),
    continents: CONTS.map((c, order) => ({ slug: c.id, order, color: c.c, i18n: { nl: { name: c.name } } })),
    holidays: HOLIDAYS.map((h, order) => ({ slug: h.id, order, fixed: h.fixed || null, dates: h.dates || null, leadDays: h.lead || 0, afterDays: h.after || 0, approximate: !!h.approx, label: h.label || null, countries: ['NL'], i18n: { nl: { name: h.name } } })),
    seasons: SPANS.map(s => ({ slug: s.id, from: s.from, to: s.to, plates: s.pages, countries: ['NL'], i18n: { nl: { name: s.name } } })),
    colors: Object.entries(KEYS).map(([code, hex]) => ({ code, hex, i18n: { nl: { name: KEYNAME[code] } } })),
  };
}"""

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page()
        await pg.goto(SRC.as_uri())
        await pg.wait_for_timeout(800)
        data = await pg.evaluate(JS)
        await b.close()
    (OUT / "plates").mkdir(parents=True, exist_ok=True)
    for pl in data["plates"]:
        (OUT / "plates" / f"{pl['slug']}.svg").write_text(pl.pop("svg") + "\n")
    for key in ["plates", "categories", "ages", "continents", "holidays", "seasons", "colors"]:
        (OUT / f"{key}.json").write_text(json.dumps(data[key], ensure_ascii=False, indent=2) + "\n")
    print(len(data["plates"]), "platen geschreven")

asyncio.run(main())
