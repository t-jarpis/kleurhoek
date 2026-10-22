#!/bin/sh
# Richt de lokale Zitadel in (zie main.tf). Draait in de dienst "zitadel-setup" van compose.yaml.
# Idempotent: de state staat in een volume, dus een tweede keer verandert er niets.
set -eu
until [ -s /zitadel-bootstrap/terraform.pat ]; do echo "Wachten op het toegangstoken van Zitadel..."; sleep 2; done
export TF_DATA_DIR=/state/.terraform TF_PLUGIN_CACHE_DIR=/state/plugins TF_IN_AUTOMATION=1
mkdir -p "$TF_PLUGIN_CACHE_DIR"
cd /infra/envs/local
terraform init -input=false -lockfile=readonly
terraform apply -input=false -auto-approve
echo "Zitadel is ingericht."
