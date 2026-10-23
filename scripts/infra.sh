#!/usr/bin/env bash
# Kleurhoek-infrastructuur in één commando (ADR 0014). Draait op je Mac.
#
#   scripts/infra.sh check        controleert alles en meldt in één keer wat ontbreekt
#   scripts/infra.sh up dev       controle + zone + omgeving + GitHub + eerste images + rooktest
#   scripts/infra.sh up prod      idem voor productie (vraagt altijd bevestiging)
#
# Wat het zelf doet: tools installeren (Homebrew), sleutels veilig in de macOS-sleutelhanger
# bewaren, de state-bucket aanmaken, Terraform draaien, de GitHub-omgeving vullen, de eerste
# images laten bouwen en controleren of de site werkt. Het is idempotent: opnieuw draaien na
# een fout gaat verder waar het bleef.
#
# Terraform-plannen zonder verwijderingen worden zonder vragen toegepast; een plan dat iets
# verwijdert of vervangt wordt eerst getoond en vraagt om bevestiging. Prod vraagt altijd.

set -o pipefail

REPO="t-jarpis/kleurhoek"
REGION="nl-ams"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INFRA="$ROOT/infra"
KEYCHAIN="kleurhoek"
LEGACY_ENV="$HOME/.config/kleurhoek/scaleway.env"

# ---------- uitvoer ----------
bold() { printf '\033[1m%s\033[0m\n' "$*"; }
ok()   { printf '  \033[32m✓\033[0m %s\n' "$*"; }
warn() { printf '  \033[33m!\033[0m %s\n' "$*"; }
step() { printf '\n\033[1;34m▸ %s\033[0m\n' "$*"; }
die()  { printf '\n\033[31m✗ %s\033[0m\n' "$*" >&2; exit 1; }

PROBLEMS=()
problem() { PROBLEMS+=("$*"); printf '  \033[31m✗\033[0m %s\n' "$*"; }

# ---------- hulpjes ----------
have() { command -v "$1" >/dev/null 2>&1; }
version_ge() { # version_ge <versie> <minimum>  (alleen major.minor.patch, werkt met bash 3.2)
  local IFS=. a b i; read -r -a a <<<"$1"; read -r -a b <<<"$2"
  for i in 0 1 2; do
    [ "${a[i]:-0}" -gt "${b[i]:-0}" ] 2>/dev/null && return 0
    [ "${a[i]:-0}" -lt "${b[i]:-0}" ] 2>/dev/null && return 1
  done; return 0
}
tfvar() { # tfvar <bestand> <naam> → waarde tussen aanhalingstekens, leeg als niet gevonden
  sed -nE "s/^[[:space:]]*$2[[:space:]]*=[[:space:]]*\"([^\"]*)\".*/\1/p" "$1" 2>/dev/null | head -n1
}

kc_get() { security find-generic-password -s "$KEYCHAIN" -a "$1" -w 2>/dev/null; }
kc_set() { security add-generic-password -U -s "$KEYCHAIN" -a "$1" -w "$2" >/dev/null; }

# Vraagt een geheim één keer (onzichtbaar), controleert het formaat en bewaart het in de sleutelhanger.
ask_secret() { # ask_secret <account> <omschrijving> <regex>
  local value
  while :; do
    printf '  %s: ' "$2" >&2
    IFS= read -rs value; echo >&2
    value="$(printf '%s' "$value" | tr -d '[:space:]"'"'"'')"
    if [[ "$value" =~ $3 ]]; then kc_set "$1" "$value"; printf '%s' "$value"; return; fi
    printf '  \033[33m!\033[0m Dat lijkt niet te kloppen (formaat). Nog een keer.\n' >&2
  done
}

# ---------- 1. tools ----------
check_tools() {
  step "Tools"
  have brew || { problem "Homebrew ontbreekt: installeer via https://brew.sh en draai dit script opnieuw"; return; }
  local need=()
  have terraform || need+=("hashicorp/tap/terraform")
  have gh || need+=("gh")
  have jq || need+=("jq")
  if [ ${#need[@]} -gt 0 ]; then
    warn "installeren: ${need[*]}"
    brew install "${need[@]}" >/dev/null || problem "brew install ${need[*]} mislukte"
  fi
  local tv gv
  tv="$(terraform version -json 2>/dev/null | jq -r .terraform_version)"
  if ! version_ge "${tv:-0}" "1.10.0"; then
    warn "Terraform $tv is te oud; bijwerken"
    brew upgrade hashicorp/tap/terraform >/dev/null 2>&1 || brew install hashicorp/tap/terraform >/dev/null
    tv="$(terraform version -json | jq -r .terraform_version)"
  fi
  gv="$(gh --version 2>/dev/null | sed -nE '1s/.* ([0-9]+\.[0-9]+\.[0-9]+).*/\1/p')"
  if ! version_ge "${gv:-0}" "2.40.0"; then
    warn "gh $gv is te oud; bijwerken"
    brew upgrade gh >/dev/null 2>&1 || brew install gh >/dev/null
    gv="$(gh --version | sed -nE '1s/.* ([0-9]+\.[0-9]+\.[0-9]+).*/\1/p')"
  fi
  version_ge "${tv:-0}" "1.10.0" && ok "terraform $tv" || problem "terraform ${tv:-ontbreekt} (minimaal 1.10)"
  version_ge "${gv:-0}" "2.40.0" && ok "gh $gv" || problem "gh ${gv:-ontbreekt} (minimaal 2.40)"
  have jq && ok "jq" || problem "jq ontbreekt"
  have curl && ok "curl" || problem "curl ontbreekt"
}

# ---------- 2. sleutels ----------
load_secrets() {
  step "Sleutels (macOS-sleutelhanger, dienst \"$KEYCHAIN\")"
  # Eenmalig overnemen uit het oude env-bestand.
  if [ -f "$LEGACY_ENV" ] && [ -z "$(kc_get scw-secret-key)" ]; then
    # shellcheck disable=SC1090
    ( set +u; source "$LEGACY_ENV"
      [ -n "${SCW_ACCESS_KEY:-}" ] && kc_set scw-access-key "$(printf '%s' "$SCW_ACCESS_KEY" | tr -d '[:space:]')"
      [ -n "${SCW_SECRET_KEY:-}" ] && kc_set scw-secret-key "$(printf '%s' "$SCW_SECRET_KEY" | tr -d '[:space:]')"
      [ -n "${CLOUDFLARE_API_TOKEN:-}" ] && kc_set cloudflare-api-token "$(printf '%s' "$CLOUDFLARE_API_TOKEN" | tr -d '[:space:]')" )
    ok "overgenomen uit $LEGACY_ENV (dat bestand mag je daarna weggooien)"
  fi

  SCW_ACCESS_KEY="$(kc_get scw-access-key)"
  [ -n "$SCW_ACCESS_KEY" ] || SCW_ACCESS_KEY="$(ask_secret scw-access-key "Scaleway access key (SCW…, IAM › API keys)" '^SCW[A-Z0-9]{17}$')"
  SCW_SECRET_KEY="$(kc_get scw-secret-key)"
  [ -n "$SCW_SECRET_KEY" ] || SCW_SECRET_KEY="$(ask_secret scw-secret-key "Scaleway secret key" '^[0-9a-f-]{36}$')"
  CLOUDFLARE_API_TOKEN="$(kc_get cloudflare-api-token)"
  [ -n "$CLOUDFLARE_API_TOKEN" ] || CLOUDFLARE_API_TOKEN="$(ask_secret cloudflare-api-token "Cloudflare API-token" '^[A-Za-z0-9_-]{40,}$')"

  export SCW_ACCESS_KEY SCW_SECRET_KEY CLOUDFLARE_API_TOKEN
  export AWS_ACCESS_KEY_ID="$SCW_ACCESS_KEY" AWS_SECRET_ACCESS_KEY="$SCW_SECRET_KEY"

  # Live controleren.
  local code
  code="$(curl -s -o /dev/null -w '%{http_code}' -H "X-Auth-Token: $SCW_SECRET_KEY" \
    "https://api.scaleway.com/iam/v1alpha1/api-keys/$SCW_ACCESS_KEY")"
  if [ "$code" = 200 ]; then ok "Scaleway-sleutel werkt"
  else problem "Scaleway-sleutel wordt geweigerd (HTTP $code). Nieuwe sleutel? Draai: scripts/infra.sh reset-keys"; fi

  local cf
  cf="$(curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" https://api.cloudflare.com/client/v4/user/tokens/verify | jq -r '.result.status // "ongeldig"')"
  [ "$cf" = active ] && ok "Cloudflare-token actief" || problem "Cloudflare-token: $cf. Nieuw token? Draai: scripts/infra.sh reset-keys"
}

# ---------- 3. instellingen per omgeving ----------
check_config() { # check_config <env>
  local env="$1" f="$INFRA/envs/$1/terraform.tfvars" zf="$INFRA/envs/zone/terraform.tfvars"
  step "Instellingen ($env)"
  [ -f "$zf" ] || { problem "ontbreekt: infra/envs/zone/terraform.tfvars (kopieer terraform.tfvars.example)"; }
  [ -f "$f" ]  || { problem "ontbreekt: infra/envs/$env/terraform.tfvars (kopieer terraform.tfvars.example)"; return; }
  local bad
  bad="$(grep -nE '^[^#]*<[^>]+>' "$f" "$zf" 2>/dev/null | sed "s|$INFRA/||")"
  [ -z "$bad" ] && ok "geen open plekken (<…>) in tfvars" || problem "nog in te vullen:"$'\n'"$(printf '%s\n' "$bad" | sed 's/^/      /')"

  ORG_ID="$(tfvar "$f" scaleway_organization_id)"
  PROJECT_ID="$(tfvar "$f" scaleway_project_id)"
  BUCKET="$(tfvar "$f" state_bucket)"
  ZONE_ID="$(tfvar "$zf" cloudflare_zone_id)"
  local uuid='^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
  [[ "$ORG_ID" =~ $uuid ]] && ok "organisatie-ID" || problem "scaleway_organization_id is geen ID (console › Organization settings › Organization ID)"
  [[ "$PROJECT_ID" =~ $uuid ]] && ok "project-ID" || problem "scaleway_project_id is geen ID (console › Project settings › Project ID)"
  [ -n "$BUCKET" ] && ok "state-bucket: $BUCKET" || problem "state_bucket ontbreekt in tfvars"

  local key; key="$(tfvar "$f" zitadel_key_file)"; key="${key/#\~/$HOME}"
  [ -f "$key" ] && ok "Zitadel-sleutel gevonden" || problem "Zitadel-sleutel niet gevonden: $key"

  if [ -n "${SCW_SECRET_KEY:-}" ] && [[ "$PROJECT_ID" =~ $uuid ]]; then
    local code
    code="$(curl -s -o /dev/null -w '%{http_code}' -H "X-Auth-Token: $SCW_SECRET_KEY" \
      "https://api.scaleway.com/account/v3/projects/$PROJECT_ID")"
    [ "$code" = 200 ] && ok "Scaleway-project bereikbaar" || problem "Scaleway-project $PROJECT_ID niet bereikbaar met deze sleutel (HTTP $code)"
  fi
  if [ -n "${CLOUDFLARE_API_TOKEN:-}" ] && [ -n "$ZONE_ID" ]; then
    local zone
    zone="$(curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" "https://api.cloudflare.com/client/v4/zones/$ZONE_ID" | jq -r '.result.name // empty')"
    [ "$zone" = kleurhoek.nl ] && ok "Cloudflare-zone kleurhoek.nl bereikbaar" || problem "Cloudflare-zone $ZONE_ID niet bereikbaar met dit token (zone toegevoegd aan het token?)"
  fi
}

# ---------- 4. GitHub ----------
check_github() {
  step "GitHub"
  if gh auth status -h github.com >/dev/null 2>&1; then ok "ingelogd bij GitHub"
  else problem "niet ingelogd bij GitHub: draai 'gh auth login' (eenmalig)"; return; fi
  gh repo view "$REPO" --json name >/dev/null 2>&1 && ok "toegang tot $REPO" || problem "geen toegang tot $REPO"
}

# ---------- state-bucket ----------
s3() { # s3 <methode> <pad> [data]
  local m=(-X "$1"); [ "$1" = HEAD ] && m=(-I)
  curl -s -o /dev/null -w '%{http_code}' "${m[@]}" --aws-sigv4 "aws:amz:$REGION:s3" \
    --user "$AWS_ACCESS_KEY_ID:$AWS_SECRET_ACCESS_KEY" ${3:+--data "$3"} "https://s3.$REGION.scw.cloud/$2"
}
ensure_bucket() {
  step "State-bucket"
  local code; code="$(s3 HEAD "$BUCKET")"
  case "$code" in
    200) ok "$BUCKET bestaat" ;;
    404)
      [ "$(s3 PUT "$BUCKET")" = 200 ] || die "bucket $BUCKET aanmaken mislukte (naam al in gebruik bij iemand anders?)"
      ok "$BUCKET aangemaakt" ;;
    403) die "geen toegang tot bucket $BUCKET (HTTP 403). Staat de 'preferred project' voor Object Storage van je sleutel op het juiste project? (IAM › API keys)" ;;
    *) die "bucket $BUCKET: onverwacht antwoord (HTTP $code)" ;;
  esac
  local v='<VersioningConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/"><Status>Enabled</Status></VersioningConfiguration>'
  [ "$(s3 PUT "$BUCKET?versioning" "$v")" = 200 ] && ok "versioning aan" || warn "versioning aanzetten lukte niet (niet blokkerend)"
}

# ---------- Terraform ----------
tf_init() { # tf_init <map>
  rm -rf "$INFRA/envs/$1/plan"
  if grep -qs '"type": *"azurerm"' "$INFRA/envs/$1/.terraform/terraform.tfstate"; then rm -rf "$INFRA/envs/$1/.terraform"; fi
  terraform -chdir="$INFRA/envs/$1" init -input=false -reconfigure -backend-config="bucket=$BUCKET" >/tmp/kh-init-$1.log 2>&1 \
    || { tail -30 /tmp/kh-init-$1.log; die "terraform init ($1) mislukte"; }
}

# Plan, controle op 403's en verwijderingen, dan toepassen.
tf_apply() { # tf_apply <map> [extra args…]
  local dir="$INFRA/envs/$1"; shift
  local log="/tmp/kh-plan-$(basename "$dir").log"
  terraform -chdir="$dir" plan -input=false -out=tfplan -compact-warnings "$@" >"$log" 2>&1
  local rc=$?
  if grep -qiE '403|not authorized|forbidden' "$log"; then
    grep -iE -B2 -A6 '403|not authorized|forbidden' "$log" | head -40
    die "Cloudflare/Scaleway weigert iets (403). Meestal mist het Cloudflare-token een recht; zie infra/README.md › Cloudflare."
  fi
  [ $rc -eq 0 ] || { tail -40 "$log"; die "terraform plan ($(basename "$dir")) mislukte"; }
  local summary changes destroys
  summary="$(terraform -chdir="$dir" show -json tfplan)"
  changes="$(jq '[.resource_changes[]? | select(.change.actions != ["no-op"])] | length' <<<"$summary")"
  destroys="$(jq -r '.resource_changes[]? | select(.change.actions | index("delete")) | "      " + (.change.actions|join("/")) + "  " + .address' <<<"$summary")"
  if [ "$changes" = 0 ]; then ok "geen wijzigingen"; rm -f "$dir/tfplan"; return; fi
  ok "$changes wijziging(en)"
  if [ -n "$destroys" ] || [ "$TARGET" = prod ]; then
    [ -n "$destroys" ] && { warn "dit plan verwijdert of vervangt:"; printf '%s\n' "$destroys"; }
    [ "$TARGET" = prod ] && warn "productie: bevestiging nodig"
    read -rp "  Doorgaan? (ja/nee) " a; [ "$a" = ja ] || die "afgebroken"
  fi
  terraform -chdir="$dir" apply -input=false -compact-warnings tfplan \
    || die "terraform apply ($(basename "$dir")) mislukte; scrol omhoog voor de fout en draai het script daarna opnieuw"
  rm -f "$dir/tfplan"
}

images_ready() { # zijn de drie images er al?
  local n
  n="$(curl -s -H "X-Auth-Token: $SCW_SECRET_KEY" \
    "https://api.scaleway.com/registry/v1/regions/$REGION/images?project_id=$PROJECT_ID&page_size=100" \
    | jq '[.images[]? | select(.name | test("^kleurhoek-(api|web|admin)$"))] | length')"
  [ "${n:-0}" -ge 3 ]
}

github_sync() { # github_sync <env>
  local env="$1" out
  out="$(terraform -chdir="$INFRA/envs/$env" output -json github)" || die "terraform output github mislukte"
  gh api -X PUT "repos/$REPO/environments/$env" >/dev/null || die "GitHub-omgeving $env aanmaken mislukte"
  local k
  for k in $(jq -r '.variables | keys[]' <<<"$out"); do
    gh variable set "$k" --env "$env" -R "$REPO" -b "$(jq -r --arg k "$k" '.variables[$k]' <<<"$out")" >/dev/null || die "GitHub-variabele $k"
  done
  for k in $(jq -r '.secrets | keys[]' <<<"$out"); do
    jq -r --arg k "$k" '.secrets[$k]' <<<"$out" | gh secret set "$k" --env "$env" -R "$REPO" >/dev/null || die "GitHub-secret $k"
  done
  # Oude secret op repo-niveau (eerste poging) opruimen; die zou prod en dev door elkaar halen.
  gh secret delete SCW_SECRET_KEY -R "$REPO" >/dev/null 2>&1 || true
  [ "$env" = dev ] && gh variable set DEPLOY_ENABLED -R "$REPO" -b true >/dev/null
  ok "variabelen en deploy-sleutel gezet in GitHub-omgeving $env"
}

run_deploy() { # run_deploy <env>
  step "Images bouwen via GitHub Actions"
  local before id
  before="$(gh run list -R "$REPO" -w Deploy -L 1 --json databaseId -q '.[0].databaseId // 0')"
  gh workflow run Deploy -R "$REPO" -f environment="$1" >/dev/null || die "Deploy starten mislukte"
  for _ in $(seq 1 30); do
    id="$(gh run list -R "$REPO" -w Deploy -L 1 --json databaseId -q '.[0].databaseId // 0')"
    [ "$id" != "$before" ] && break; sleep 2
  done
  ok "run $id: https://github.com/$REPO/actions/runs/$id"
  gh run watch "$id" -R "$REPO" --exit-status --interval 15 >/dev/null || die "Deploy mislukte; zie de link hierboven"
  ok "klaar"
}

smoke_test() { # smoke_test <url>
  step "Rooktest $1"
  for i in $(seq 1 60); do
    if curl -fsS -o /dev/null "$1/healthz" && curl -fsS -o /dev/null "$1/nl-nl"; then ok "$1 werkt"; return; fi
    [ $((i % 6)) = 0 ] && warn "nog niet bereikbaar (certificaat of koude start), even wachten…"
    sleep 10
  done
  die "$1 reageert na 10 minuten niet. Kijk in de Scaleway-console › Containers › Logs, of stuur de uitvoer aan Claude."
}

# ---------- commando's ----------
preflight() { # preflight <env>
  PROBLEMS=()
  check_tools
  load_secrets
  check_config "$1"
  check_github
  echo
  if [ ${#PROBLEMS[@]} -gt 0 ]; then
    bold "Eerst oplossen (${#PROBLEMS[@]}):"
    printf '  • %s\n' "${PROBLEMS[@]}"
    exit 1
  fi
  bold "Alles in orde."
}

cmd_up() {
  TARGET="${1:-}"; [ "$TARGET" = dev ] || [ "$TARGET" = prod ] || die "gebruik: scripts/infra.sh up dev|prod"
  preflight "$TARGET"
  ensure_bucket

  step "Zone kleurhoek.nl"
  tf_init zone; tf_apply zone

  step "Omgeving $TARGET"
  tf_init "$TARGET"
  if images_ready; then
    tf_apply "$TARGET"
    github_sync "$TARGET"
  else
    warn "nog geen images: eerst de basis, dan bouwen, dan de containers"
    tf_apply "$TARGET" -var apps_enabled=false
    github_sync "$TARGET"
    run_deploy "$TARGET"
    step "Containers en domeinen"
    tf_apply "$TARGET"
    github_sync "$TARGET"
  fi
  smoke_test "$(terraform -chdir="$INFRA/envs/$TARGET" output -raw site_url)"
  echo; bold "Klaar: $(terraform -chdir="$INFRA/envs/$TARGET" output -raw site_url)"
}

cmd_reset_keys() {
  for a in scw-access-key scw-secret-key cloudflare-api-token; do
    security delete-generic-password -s "$KEYCHAIN" -a "$a" >/dev/null 2>&1 || true
  done
  ok "sleutels uit de sleutelhanger verwijderd; de volgende run vraagt ze opnieuw"
}

TARGET=""
case "${1:-}" in
  check) preflight "${2:-dev}" ;;
  up) cmd_up "${2:-}" ;;
  reset-keys) cmd_reset_keys ;;
  *) sed -n '2,9p' "$0" | sed 's/^# \{0,1\}//'; exit 1 ;;
esac
