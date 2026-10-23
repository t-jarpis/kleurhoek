#!/usr/bin/env bash
# Browsertest vóór de uitrol (CI): API, website en inlogpagina als productiebuild, een testschool met
# eigen huisstijl, en dan dezelfde controle als na de uitrol (opmaak geladen, geen JavaScript-fouten).
# Verwacht gebouwde apps (pnpm build). DATABASE_URL leeg = de API draait met een database in het geheugen.
# Lokaal: CHROME_PATH=/pad/naar/chromium .github/e2e/run.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
LOGS="${RUNNER_TEMP:-/tmp}/kh-e2e"; mkdir -p "$LOGS"
export INGEST_KEY=e2e-ingest-key-0123456789abcdef0123456789 ADMIN_DEV_TOKEN=e2e-admin-token-0123456789abcdef0123456789
export ORG_WORKER_SECRET=e2e-worker-secret-0123456789abcdef API_URL=http://localhost:3001
pids=()
cleanup() { for p in "${pids[@]}"; do kill "$p" 2>/dev/null || true; done; pkill -f "next-server|next start -p 300[03]|node dist/main.js" 2>/dev/null || true; }
trap cleanup EXIT
fail() { echo "::error::$1"; for f in "$LOGS"/*.log; do echo "--- $f"; tail -40 "$f"; done; exit 1; }

(cd apps/api && exec env NODE_ENV=development ORG_HOST_PATTERN='{slug}-dev.kleurhoek.nl' MIGRATE_ON_START=true SEED_ON_START=true node dist/main.js > "$LOGS/api.log" 2>&1) & pids+=($!)
for i in $(seq 1 60); do curl -fsS -o /dev/null http://localhost:3001/health && break; sleep 2; [ "$i" = 60 ] && fail "API start niet"; done

(cd apps/web && exec env NODE_ENV=production npx next start -p 3000 > "$LOGS/web.log" 2>&1) & pids+=($!)
(cd apps/login && exec env NODE_ENV=production LOGIN_SECRET=e2e-login-secret-0123456789abcdef0123 npx next start -p 3003 > "$LOGS/login.log" 2>&1) & pids+=($!)
for port in 3000 3003; do
  for i in $(seq 1 60); do curl -fsS -o /dev/null "http://localhost:$port/healthz" && break; sleep 2; [ "$i" = 60 ] && fail "app op poort $port start niet"; done
done

# Testschool met eigen lettertype, kleuren en een beperkt aanbod (ADR 0017).
api() { curl -fsS -X "$1" -H "authorization: Bearer $ADMIN_DEV_TOKEN" -H 'content-type: application/json' "http://localhost:3001$2" -d "$3" > /dev/null; }
api POST /v1/admin/organizations '{"slug":"e2e-school","name":"E2E School","kind":"school"}' || fail "organisatie aanmaken mislukte"
api PUT /v1/admin/organizations/e2e-school '{"brand":{"font":"nunito","colors":{"primary":"#1f5f8b","accent":"#b0306a"},"wordmark":"e2e school"},"offer":{"categories":["dieren","natuur"]},"features":{"shop":false}}' || fail "huisstijl zetten mislukte"

plate=$(curl -fsS -H "x-ingest-key: $INGEST_KEY" "http://localhost:3001/v1/markets/nl-nl/plates" | jq -r '.items[0].slug')
.github/diagnose/browser-check.sh \
  "http://localhost:3000/nl-nl" \
  "http://localhost:3000/nl-nl/platen/$plate" \
  "http://localhost:3000/nl-nl/boekje" \
  "http://localhost:3000/nl-nl|e2e-school-dev.kleurhoek.nl" \
  "http://localhost:3003/inloggen" \
  || fail "browsertest mislukte"
