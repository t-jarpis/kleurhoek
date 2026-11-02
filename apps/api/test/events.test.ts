import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { DomainEvents } from "../src/shared/events";
import { createTestApp } from "./app";

/** Domeinevents (ADR 0066): wie reageert op wat, en een mislukte reactie bij een account houdt het verwijderen tegen. */
describe("domeinevents", () => {
  let ctx: Awaited<ReturnType<typeof createTestApp>>;
  beforeAll(async () => { ctx = await createTestApp(); });
  afterAll(async () => { await ctx.app.close(); });

  it("elk domein met gegevens van een gebruiker ruimt op als het account verdwijnt", () => {
    const events = ctx.app.get(DomainEvents);
    expect(events.listeners("identity.account.deleted").sort()).toEqual(["engagement", "messaging", "organizations"]);
    expect(events.listeners("catalog.plates.published")).toContain("social");
  });

  it("strict: een mislukte reactie geeft een fout, anders alleen een log", async () => {
    const events = new DomainEvents();
    events.on("catalog.plates.published", "test", () => { throw new Error("stuk"); });
    await expect(events.emit("catalog.plates.published", { added: ["x"], changed: [] })).resolves.toBeUndefined();
    await expect(events.emit("catalog.plates.published", { added: ["x"], changed: [] }, { strict: true })).rejects.toThrow(/mislukt/);
  });
});
