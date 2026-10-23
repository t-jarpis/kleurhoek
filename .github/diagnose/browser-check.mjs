// Rooktest in een echte browser: laadt elke pagina, wacht tot React klaar is en controleert dat de
// opmaak er is en dat er geen JavaScript-fouten zijn (een hydratiefout kan de CSS laten verdwijnen).
//
// Gebruik: node browser-check.mjs <pagina> [<pagina> …]
//   <pagina> = een URL, of URL|host om een organisatiedomein na te bootsen (zoals de Worker doet:
//   x-kh-host plus x-kh-worker uit ORG_WORKER_SECRET). Dan moet ook de huisstijl (#kh-brand) er zijn.
// CHROME_PATH kiest de browser (standaard de Chrome van de GitHub-runner).
import { chromium } from "playwright-core";

const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH ?? "/usr/bin/google-chrome" });
let failed = false;
for (const arg of process.argv.slice(2)) {
  const [url, host] = arg.split("|");
  const context = await browser.newContext(host ? { extraHTTPHeaders: { "x-kh-host": host, "x-kh-worker": process.env.ORG_WORKER_SECRET ?? "" } } : {});
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message.slice(0, 200)));
  let status = 0;
  try {
    status = (await page.goto(url, { waitUntil: "networkidle", timeout: 60_000 }))?.status() ?? 0;
    await page.waitForTimeout(2000);
  } catch (e) {
    errors.push(String(e).slice(0, 200));
  }
  const { sheets, brand } = await page.evaluate(() => ({ sheets: document.styleSheets.length, brand: !!document.getElementById("kh-brand") })).catch(() => ({ sheets: 0, brand: false }));
  const problems = [
    ...(status >= 400 || status === 0 ? [`HTTP ${status}`] : []),
    ...(sheets === 0 ? ["geen opmaak"] : []),
    ...(host && !brand ? ["huisstijl ontbreekt"] : []),
    ...errors.map((e) => `fout: ${e}`),
  ];
  console.log(`${problems.length ? "FOUT" : "ok  "} ${url}${host ? ` (als ${host})` : ""}: ${sheets} stylesheet(s)${problems.length ? ` — ${problems.join("; ")}` : ""}`);
  if (problems.length) failed = true;
  await context.close();
}
await browser.close();
process.exit(failed ? 1 : 0);
