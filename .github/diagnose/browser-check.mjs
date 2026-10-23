// Rooktest in een echte browser: laadt de pagina, wacht tot React klaar is en controleert dat de
// opmaak er nog is en dat er geen JavaScript-fouten zijn (een hydratiefout kan de CSS laten verdwijnen).
// Gebruik: node browser-check.mjs <url> [<url> …]
import { chromium } from "playwright-core";

const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH ?? "/usr/bin/google-chrome" });
let failed = false;
for (const url of process.argv.slice(2)) {
  const page = await browser.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message.slice(0, 200)));
  await page.goto(url, { waitUntil: "networkidle", timeout: 60_000 });
  await page.waitForTimeout(2000);
  const sheets = await page.evaluate(() => document.styleSheets.length);
  const ok = sheets > 0 && errors.length === 0;
  console.log(`${ok ? "ok " : "FOUT"} ${url}: ${sheets} stylesheet(s)${errors.length ? `, fouten: ${errors.join(" | ")}` : ""}`);
  if (!ok) failed = true;
  await page.close();
}
await browser.close();
process.exit(failed ? 1 : 0);
