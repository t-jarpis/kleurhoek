#!/usr/bin/env node
// Zet de leeftijd van elke kleurplaat volgens de regel in age-rule.mjs (ADR 0094).
//   node scripts/plates/ages.mjs           tonen wat er verandert
//   node scripts/plates/ages.mjs --write   plates.json bijwerken en de lijst wijzigingen naar stdout (JSON)
import fs from "node:fs";
import path from "node:path";
import { DATA } from "./lib.mjs";
import { ageFor } from "./age-rule.mjs";

const file = path.join(DATA, "plates.json");
const list = JSON.parse(fs.readFileSync(file, "utf8"));
const changes = [];
for (const p of list) {
  const want = ageFor(p);
  if (want && want !== p.age) { changes.push({ slug: p.slug, from: p.age, to: want }); p.age = want; }
}
if (process.argv.includes("--write")) {
  fs.writeFileSync(file, JSON.stringify(list, null, 2) + "\n");
  process.stdout.write(JSON.stringify(changes));
} else {
  const n = {};
  for (const c of changes) n[`${c.from} → ${c.to}`] = (n[`${c.from} → ${c.to}`] ?? 0) + 1;
  console.log(`${changes.length} platen krijgen een andere leeftijd`);
  console.table(n);
}
