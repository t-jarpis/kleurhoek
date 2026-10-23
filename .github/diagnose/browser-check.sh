#!/usr/bin/env bash
# Draait browser-check.mjs met playwright-core uit een eigen map (buiten de pnpm-workspace).
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
dir="${RUNNER_TEMP:-/tmp}/kh-browser-check"
if [ ! -d "$dir/node_modules/playwright-core" ]; then
  mkdir -p "$dir" && (cd "$dir" && echo '{"private":true,"type":"module"}' > package.json && npm install --silent --no-audit --no-fund playwright-core@1.56.1)
fi
cp "$here/browser-check.mjs" "$dir/browser-check.mjs"
exec node "$dir/browser-check.mjs" "$@"
