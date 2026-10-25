# 0042 · Inloggen op de website aan- en uitzetten

- Status: aangenomen
- Datum: 2026-10-25

## Context
Inloggen op de website (ouders, leerkrachten, beheerders van scholen) loopt via Zitadel. Bij een storing of een probleem met accounts, of als we inloggen tijdelijk niet willen aanbieden, willen we dat met één knop uitzetten. Per organisatie kon dat al (functie "Inloggen voor ouders", ADR 0017); voor de hele website niet.

## Besluit
- In het admin panel staat onder **Toegang** de schakelaar **Inloggen op de website**. Je hebt het recht `operations.access.manage` nodig. De stand staat in `operations.site_access.login_enabled` (standaard aan) en elke wijziging komt in het auditlog (`operations.login.update`).
- Uit betekent:
  - de API geeft aan de website voor elke organisatie `features.accounts = false`, dus de inlogknop, de accountpagina en de accountfuncties verdwijnen;
  - `/auth/login` stuurt terug naar de pagina;
  - `/auth/callback` maakt geen nieuwe sessie.
  - Kleuren, printen en favorieten op het apparaat blijven werken.
- Het admin panel valt hier niet onder: dat heeft een eigen inlog en blijft achter Cloudflare Access.
- De API onthoudt de stand 5 seconden en de website onthoudt de organisatie 30 seconden. Een wijziging is dus binnen een minuut zichtbaar.

## Gevolgen
- Migratie 0027: kolom `login_enabled` op `operations.site_access`.
- Wie al is ingelogd, houdt een sessiecookie, maar ziet geen accountfuncties meer zolang inloggen uit staat.
