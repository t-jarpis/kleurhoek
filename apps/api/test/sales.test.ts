import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { detectMapping, parseAmount, parseCsv, parseDay, toRows } from "../src/modules/shop/sales.import";
import { createTestApp } from "./app";

// Rapport zoals Amazon het exporteert: een titelregel, dan de kopregel, bedragen met valuta in de kop.
const AMAZON = `Fee-Earnings report from 2026-10-01 to 2026-10-23
Category,Name,ASIN,Seller,Tracking ID,Date Shipped,Price(€),Items Shipped,Returns,Revenue(€),Ad Fees(€),Device Type Group
Kunst,"Kleurpotloden, 12 stuks",B0STEMPEL1,Amazon,kleurhoek-kat,2026-10-21,8.99,1,0,8.99,0.63,DESKTOP
Kunst,Kinderschaar,B000000002,Amazon,kleurhoek-21,2026-10-22,6.99,2,0,13.98,0.98,PHONE
Total,,,,,,,,,,1.61,
`;
// Rapport met puntkomma's en Nederlandse bedragen, zoals een netwerk of bol het levert.
const BOL = `Datum;Kenmerk;EAN;Aantal;Omzet;Commissie
24-10-2026;kleurhoek-lampion-maken;8710000000001;1;€ 12,50;€ 0,75
24-10-2026;kleurhoek;8710000000002;1;"1.234,00";"61,70"
`;

describe("rapporten van partners lezen (ADR 0033)", () => {
  it("herkent kolommen, bedragen en datums in verschillende vormen", () => {
    const a = parseCsv(AMAZON);
    expect(a.headers).toContain("Tracking ID");
    expect(detectMapping(a.headers)).toMatchObject({ date: "Date Shipped", subId: "Tracking ID", product: "ASIN", items: "Items Shipped", revenue: "Revenue(€)", commission: "Ad Fees(€)" });
    const r = toRows(a, detectMapping(a.headers));
    expect(r.rows).toHaveLength(2);
    expect(r.skipped).toBe(1); // de totaalregel
    expect(r.rows[1]).toMatchObject({ day: "2026-10-22", product: "B000000002", items: 2, revenueCents: 1398, commissionCents: 98, currency: "EUR" });
    const b = parseCsv(BOL);
    expect(detectMapping(b.headers)).toMatchObject({ date: "Datum", subId: "Kenmerk", product: "EAN", commission: "Commissie" });
    expect(toRows(b, detectMapping(b.headers)).rows[1]).toMatchObject({ day: "2026-10-24", revenueCents: 123400, commissionCents: 6170 });
    expect(parseAmount("-0,50")).toBe(-50);
    expect(parseAmount("1,234.56")).toBe(123456);
    expect(parseDay("October 24, 2026")).toBe("2026-10-24");
    expect(parseDay("24. Okt. 2026")).toBe("2026-10-24");
    expect(parseDay("totaal")).toBeNull();
  });
});

describe("verkopen inlezen en tonen", () => {
  let ctx: Awaited<ReturnType<typeof createTestApp>>;
  const admin = { authorization: "Bearer beheerder" };
  beforeAll(async () => {
    ctx = await createTestApp();
    await ctx.http.inject({ method: "POST", url: "/v1/admin/shop/products/amazon", headers: admin, payload: { asin: "B0STEMPEL1", name: "Kleurpotloden test", materials: ["kleurpotloden"], stores: ["amazon-nl"] } });
  });
  afterAll(async () => { await ctx.app.close(); });

  it("toont eerst een voorbeeld, leest daarna in en vervangt bij opnieuw inlezen", async () => {
    const pre = await ctx.http.inject({ method: "POST", url: "/v1/admin/shop/sales/preview", headers: admin, payload: { partner: "amazon-nl", csv: AMAZON } });
    expect(pre.statusCode).toBe(201);
    expect(pre.json()).toMatchObject({ total: 2, from: "2026-10-21", to: "2026-10-22", matchedProducts: 1, matchedPlates: 1, problem: null });
    const mapping = pre.json().mapping;
    for (let i = 0; i < 2; i++) {
      const imp = await ctx.http.inject({ method: "POST", url: "/v1/admin/shop/sales/import", headers: admin, payload: { partner: "amazon-nl", csv: AMAZON, fileName: "amazon.csv", mapping } });
      expect(imp.json()).toMatchObject({ from: "2026-10-21", to: "2026-10-22", rows: 2 });
    }
    const rep = (await ctx.http.inject({ method: "GET", url: "/v1/admin/shop/sales?from=2026-10-01&to=2026-10-31", headers: admin })).json();
    expect(rep.byPartner).toEqual([{ partner: "amazon-nl", currency: "EUR", orders: 2, items: 3, revenueCents: 2297, commissionCents: 161 }]);
    expect(rep.byProduct).toEqual(expect.arrayContaining([expect.objectContaining({ product: "kleurpotloden-test-amazon-nl", matched: true }), expect.objectContaining({ product: "B000000002", matched: false })]));
    expect(rep.byPlate).toEqual([{ plate: "kat", orders: 1, commissionCents: 63, currency: "EUR" }]);
    expect(rep.coverage).toEqual([{ partner: "amazon-nl", lastDay: "2026-10-22" }]);
    // De kolomkeuze wordt onthouden: zonder mapping stelt het voorbeeld dezelfde voor.
    expect((await ctx.http.inject({ method: "POST", url: "/v1/admin/shop/sales/preview", headers: admin, payload: { partner: "amazon-nl", csv: AMAZON } })).json().mapping).toEqual(mapping);
  });

  it("weigert een onbekende partner of een bestand zonder datum", async () => {
    expect((await ctx.http.inject({ method: "POST", url: "/v1/admin/shop/sales/preview", headers: admin, payload: { partner: "bestaat-niet", csv: BOL } })).statusCode).toBe(404);
    const pre = await ctx.http.inject({ method: "POST", url: "/v1/admin/shop/sales/preview", headers: admin, payload: { partner: "bol", csv: "Product;Commissie\nx;1,00\n" } });
    expect(pre.json().problem).toBe("Kies de kolom met de datum.");
  });
});
