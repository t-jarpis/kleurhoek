#!/usr/bin/env node
// IndexNow (ADR 0061): meldt nieuwe pagina's van de productiedomeinen aan bij Bing, Yandex, Seznam en Naver.
// Leest de sitemaps (ADR 0050), vergelijkt met de lijst van de vorige keer en stuurt alleen wat nieuw is.
// Zonder vorige lijst (of met --all) gaat alles mee. Draait na elke uitrol naar productie (deploy.yml).
//
//   node scripts/indexnow.mjs --previous vorige.txt --out nu.txt [--all] [--dry-run]
import { existsSync, readFileSync, writeFileSync } from "node:fs";

const KEY = "53075bde558b1ae534a24a6c12389173"; // Zelfde als apps/web/src/lib/indexnow.ts; geen geheim.
const SITES = (process.env.INDEXNOW_SITES ?? "https://www.kleurhoek.nl,https://www.kleurhoek.be,https://www.kleurhoek.com").split(",").map((s) => s.trim()).filter(Boolean);
const ENDPOINT = "https://api.indexnow.org/indexnow";
const BATCH = 10_000;

const arg = (name) => { const i = process.argv.indexOf(name); return i > 0 ? process.argv[i + 1] : undefined; };
const flag = (name) => process.argv.includes(name);
const locs = (xml) => [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1].replace(/&amp;/g, "&"));

async function get(url) {
  for (let i = 0; i < 3; i++) {
    const res = await fetch(url, { headers: { "user-agent": "kleurhoek-indexnow" } }).catch(() => null);
    if (res?.ok) return res.text();
    await new Promise((r) => setTimeout(r, 2000 * (i + 1)));
  }
  throw new Error(`Niet op te halen: ${url}`);
}

async function urlsOf(site) {
  // De sleutel moet op dit domein staan, anders weigert IndexNow alles.
  const key = (await get(`${site}/indexnow.txt`)).trim();
  if (key !== KEY) throw new Error(`${site}/indexnow.txt geeft een andere sleutel`);
  const index = await get(`${site}/sitemap.xml`);
  const out = [];
  for (const sm of locs(index)) out.push(...locs(await get(sm)).filter((u) => u.startsWith(site)));
  return out;
}

const previousFile = arg("--previous");
const previous = previousFile && existsSync(previousFile) && !flag("--all") ? new Set(readFileSync(previousFile, "utf8").split("\n").filter(Boolean)) : null;
const all = [];
let failed = false;
for (const site of SITES) {
  let urls;
  try { urls = await urlsOf(site); } catch (e) { console.log(`::warning::${e.message}`); failed = true; continue; }
  all.push(...urls);
  const fresh = previous ? urls.filter((u) => !previous.has(u)) : urls;
  console.log(`${site}: ${urls.length} adressen, ${fresh.length} nieuw`);
  const host = new URL(site).host;
  for (let i = 0; i < fresh.length; i += BATCH) {
    const urlList = fresh.slice(i, i + BATCH);
    if (flag("--dry-run")) { console.log(urlList.slice(0, 5).join("\n")); continue; }
    const res = await fetch(ENDPOINT, { method: "POST", headers: { "content-type": "application/json; charset=utf-8" },
      body: JSON.stringify({ host, key: KEY, keyLocation: `${site}/indexnow.txt`, urlList }) });
    // 200 en 202 zijn goed; 422 = adressen horen niet bij dit domein, 429 = te vaak.
    console.log(`  aangemeld: ${urlList.length} (${res.status})`);
    if (res.status >= 400) failed = true;
  }
}
// Alleen bij succes de lijst bewaren, anders proberen we het de volgende keer opnieuw.
const out = arg("--out");
if (out && !failed && all.length) writeFileSync(out, [...new Set(all)].sort().join("\n") + "\n");
if (failed) console.log("::warning::IndexNow niet helemaal gelukt; de volgende uitrol probeert het opnieuw.");
