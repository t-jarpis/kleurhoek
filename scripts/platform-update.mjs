#!/usr/bin/env node
// Haalt een nieuwe versie van een platformpakket op en zet hem in vendor/.
// Gebruik: node scripts/platform-update.mjs auth 0.3.0
//   - uit GitHub Packages (NODE_AUTH_TOKEN met read:packages), of
//   - met --from <pad naar platform-repo> uit een lokale checkout (pnpm pack).
// Daarna: pnpm install, pnpm check, committen. Zo heeft niemand anders een token nodig.
import { execFileSync } from "node:child_process";
import { existsSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import path from "node:path";

const [name, version, flag, from] = process.argv.slice(2);
if (!name || !/^[a-z-]+$/.test(name) || !version || !/^\d+\.\d+\.\d+(-[\w.]+)?$/.test(version)) {
  console.error("Gebruik: node scripts/platform-update.mjs <pakket> <versie> [--from <platform-repo>]");
  process.exit(1);
}
const root = path.resolve(import.meta.dirname, "..");
const vendor = path.join(root, "vendor");
const file = `t-jarpis-${name}-${version}.tgz`;

if (flag === "--from") {
  execFileSync("pnpm", ["--filter", `@t-jarpis/${name}`, "build"], { cwd: from, stdio: "inherit" });
  execFileSync("pnpm", ["pack", "--pack-destination", vendor], { cwd: path.join(from, "packages", name), stdio: "inherit" });
} else {
  if (!process.env.NODE_AUTH_TOKEN) { console.error("Zet NODE_AUTH_TOKEN (GitHub-token met read:packages)"); process.exit(1); }
  const npmrc = path.join(vendor, ".npmrc.tmp");
  writeFileSync(npmrc, "@t-jarpis:registry=https://npm.pkg.github.com\n//npm.pkg.github.com/:_authToken=${NODE_AUTH_TOKEN}\n");
  try {
    execFileSync("npm", ["pack", `@t-jarpis/${name}@${version}`, "--pack-destination", vendor, "--userconfig", npmrc], { stdio: "inherit" });
  } finally { rmSync(npmrc); }
}

for (const f of readdirSync(vendor)) {
  if (f.startsWith(`t-jarpis-${name}-`) && f !== file) rmSync(path.join(vendor, f));
}
for (const app of readdirSync(path.join(root, "apps"))) {
  const p = path.join(root, "apps", app, "package.json");
  if (!existsSync(p)) continue;
  const pkg = JSON.parse(readFileSync(p, "utf8"));
  if (pkg.dependencies?.[`@t-jarpis/${name}`]) {
    pkg.dependencies[`@t-jarpis/${name}`] = `file:../../vendor/${file}`;
    writeFileSync(p, JSON.stringify(pkg, null, 2) + "\n");
    console.log(`apps/${app}: @t-jarpis/${name} → ${version}`);
  }
}
console.log("Klaar. Nu: pnpm install && pnpm check");
