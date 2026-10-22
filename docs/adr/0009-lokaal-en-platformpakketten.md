# 0009 · Lokaal draaien met docker compose, platformpakketten in de repo

- Status: aangenomen
- Datum: 2026-10-22

## Context
Lokaal moet alles met één commando werken, met de echte Zitadel en zonder handwerk. Twee dingen zaten in de weg: de platformpakketten stonden alleen in GitHub Packages (daar is altijd een token nodig, ook om te bouwen), en de uitgever van de tokens moet voor de browser en voor de containers hetzelfde adres hebben.

## Besluit
- **`docker compose up`** start PostgreSQL, Zitadel (zelf gehost, v4, ingebouwde loginpagina), een Terraform-stap die Zitadel inricht, een migratie-en-seedstap, de API, de website en het admin panel.
- **Zitadel inrichten met dezelfde module** als dev en prod (`infra/modules/zitadel`), via `infra/envs/local`. Lokaal komen daar Org Beheer en testaccounts met wachtwoord bij. Client-ID's en -geheimen gaan als env-bestanden naar de apps; niets met de hand overtypen.
- **Eén netwerkruimte** voor Zitadel en de apps (`network_mode: service:net`), zodat `http://localhost:8080` voor de browser én de containers Zitadel is. Poorten luisteren alleen op 127.0.0.1.
- **Http alleen op localhost.** `insecureDevelopment` in `@t-jarpis/auth` werkt alleen als site en uitgever op localhost draaien; anders weigert de BFF te starten. De API accepteert een http-uitgever in productiemodus alleen op localhost. Zo kan deze uitzondering nooit in Azure terechtkomen.
- **Platformpakketten als tarball in `vendor/`.** Installeren, CI en Docker-builds hebben geen token meer nodig. Bijwerken met `scripts/platform-update.mjs` (uit GitHub Packages of een lokale checkout). Dit past ook bij ADR 0004: wie de site koopt, krijgt alles wat nodig is om te bouwen.

## Afwegingen
- *Echte Zitadel in plaats van een nep-versie*: zwaarder, maar je test precies de flow van productie (organisaties, scopes, tokens, uitloggen). De nep-Zitadel blijft voor de geautomatiseerde tests.
- *Wachtwoorden lokaal*: zodat inloggen werkt zonder e-mail of passkey. Ze bestaan alleen in de lokale Zitadel.
- *Tarballs in git*: een paar tientallen KB per versie. Daarvoor geen tokens, geen Renovate-configuratie en een site die op zichzelf staat.

## Gevolgen
- Een echte login in compose bracht een fout boven: de versleutelde sessie met Zitadel-tokens was groter dan 4 KB en werd door de browser genegeerd. `@t-jarpis/auth` 0.3.0 verdeelt grote sessies over maximaal vier cookies.
