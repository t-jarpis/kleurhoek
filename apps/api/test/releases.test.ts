import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { notesBetween, ReleasesService, type LogEntry } from "../src/modules/operations/releases.service";
import { createTestApp } from "./app";

const LOG: LogEntry[] = [
  { sha: "c3".padEnd(40, "0"), date: "2026-10-24T10:00:00+02:00", subject: "Goals in admin", note: "Doelen in het admin panel", public: "" },
  { sha: "c2".padEnd(40, "0"), date: "2026-10-24T09:00:00+02:00", subject: "Terraform fmt", note: "", public: "" },
  { sha: "c1".padEnd(40, "0"), date: "2026-10-23T09:00:00+02:00", subject: "Print fix", note: "Printen werkt weer", public: "Printen werkt weer op alle telefoons." },
];

describe("releasenotes (ADR 0023)", () => {
  let ctx: Awaited<ReturnType<typeof createTestApp>>;
  beforeAll(async () => { ctx = await createTestApp(); });
  afterAll(async () => { await ctx.app.close(); });

  it("neemt de commits sinds de vorige release, met de Nederlandse tekst als die er is", () => {
    expect(notesBetween(LOG, LOG[0]!.sha, LOG[2]!.sha)).toEqual([
      { sha: LOG[0]!.sha, date: LOG[0]!.date, text: "Doelen in het admin panel", technical: false },
      { sha: LOG[1]!.sha, date: LOG[1]!.date, text: "Terraform fmt", technical: true },
    ]);
    expect(notesBetween(LOG, LOG[1]!.sha, null)).toHaveLength(2);
  });

  it("legt een nieuwe versie één keer vast, en een oudere versie als terugdraaien", async () => {
    const svc = ctx.app.get(ReleasesService);
    expect(await svc.record("c1".padEnd(40, "0"), LOG)).toBe("recorded");
    expect(await svc.record("c1".padEnd(40, "0"), LOG)).toBe("unchanged");
    expect(await svc.record("c3".padEnd(7, "0"), LOG)).toBe("recorded");
    expect(await svc.record("c1".padEnd(40, "0"), LOG)).toBe("recorded");
    const res = await ctx.http.inject({ method: "GET", url: "/v1/admin/releases", headers: { authorization: "Bearer analist" } });
    expect(res.statusCode).toBe(200);
    const list = res.json().releases as { kind: string; sha: string; notes: { text: string }[] }[];
    expect(list.map((r) => r.kind)).toEqual(["rollback", "release", "first"]);
    expect(list[1]!.sha).toBe(LOG[0]!.sha);
    expect(list[1]!.notes.map((n) => n.text)).toEqual(["Doelen in het admin panel", "Terraform fmt"]);
    expect(list[0]!.notes).toEqual([]);
  });

  it("bewaart de publieke tekst bij de note (ADR 0030)", () => {
    expect(notesBetween(LOG, LOG[2]!.sha, null)[0]).toMatchObject({ text: "Printen werkt weer", public: "Printen werkt weer op alle telefoons." });
    expect(notesBetween(LOG, LOG[0]!.sha, LOG[2]!.sha)[0]).not.toHaveProperty("public");
  });
});
