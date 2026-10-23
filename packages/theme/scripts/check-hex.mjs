// Spelregel van het design system: geen losse kleuren in componenten, alleen tokens (var(--…)).
// Uitzondering: een regel met "theme-allow" (bijvoorbeeld de krijtkleuren van de studio, dat is inhoud).
import { readdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";

const repo = join(dirname(fileURLToPath(import.meta.url)), "../../..");
const roots = ["apps/web/src", "apps/admin/src", "apps/login/src"].map((r) => join(repo, r));
const HEX = /#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?(?:[0-9a-fA-F]{2})?\b/;
const bad = [];
const walk = (d) => {
  for (const n of readdirSync(d)) {
    const p = join(d, n);
    if (statSync(p).isDirectory()) { walk(p); continue; }
    if (!/\.(css|tsx|ts)$/.test(n) || /\.test\.ts$/.test(n)) continue;
    readFileSync(p, "utf8").split("\n").forEach((line, i) => {
      if (HEX.test(line.replace(/&#\d+;|href="#[^"]*"|url\(#[^)]*\)|`#\$\{/g, "")) && !line.includes("theme-allow")) bad.push(`${relative(repo, p)}:${i + 1}: ${line.trim().slice(0, 120)}`);
    });
  }
};
roots.forEach(walk);
if (bad.length) { console.error(`Losse kleuren gevonden; gebruik een token (packages/theme):\n${bad.join("\n")}`); process.exit(1); }
console.log("Geen losse kleuren in apps/web, apps/admin en apps/login");
