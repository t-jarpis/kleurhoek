# 0018 · Eigen inlogpagina op het eigen domein

- Status: aangenomen
- Datum: 2026-10-23

## Aanleiding
Inloggen op de website ging naar de inlogpagina van Zitadel Cloud (`…zitadel.cloud`), in de stijl van Zitadel. De eigenaar wil dat inloggen op het Kleurhoek-domein blijft en in dezelfde stijl, ook voor organisaties met een eigen huisstijl (ADR 0017). Een eigen domein voor Zitadel zelf kan alleen op het Pro-plan (circa $100 per maand) en geeft nog steeds de pagina van Zitadel.

## Besluit
**Een eigen app `apps/login`** op `login.kleurhoek.nl` (dev: `login-dev.kleurhoek.nl`), gebouwd op de openbare v2-API's van Zitadel. Het is eigen code; we nemen niets over uit de login-app van Zitadel.

- Zitadel stuurt de browser met *login v2* en een eigen `base_uri` naar `/login?authRequest=V2_…`. De app haalt het verzoek op, kiest de huisstijl van de organisatie op basis van de host van de redirect-URI, en doet de stappen met de Session API. Daarna rondt hij het verzoek af (`POST /v2/oidc/auth_requests/{id}`), en Zitadel stuurt terug naar de site met een gewone OIDC-code. De BFF van de website verandert niet.
- **Inlogmethoden.** Een code per e-mail, of een passkey. Zitadel accepteert een e-mailcode alleen als die methode bij de gebruiker aanstaat; de app zet hem aan zodra het e-mailadres bevestigd is. Na inloggen met een code stelt de app een passkey voor. Wachtwoorden zijn er niet. Inloggen met Google, Apple of Microsoft volgt (identity provider intents).
- **Passkeys met RP-ID `kleurhoek.nl`**, zodat één passkey werkt op alle Kleurhoek-adressen. Passkeys die eerder op de pagina van Zitadel zijn gemaakt, horen bij het domein van Zitadel en moeten opnieuw worden gemaakt.
- **Account maken** vraagt een voornaam, het e-mailadres en de bevestiging "16 jaar of ouder" (ADR 0002). Het adres bevestigen met de code is meteen het bewijs voor die eerste keer inloggen.
- **Niet verklappen wie een account heeft.** Bij een onbekend adres toont de pagina hetzelfde codescherm, maar gaat er geen mail de deur uit. Account maken met een bestaand adres stuurt gewoon een inlogcode.
- **Toestand zonder opslag**: één versleutelde cookie (AES-256-GCM, `__Host-`, 15 minuten) met het auth request, de stap en het Zitadel-sessietoken.
- **Rechten**: een service user `kleurhoek-login` met alleen de instance-rol `IAM_LOGIN_CLIENT`; het token komt uit Terraform en gaat als geheim naar de container.
- **Bescherming**: alleen via Cloudflare (geheime header), rate limit aan de rand op de inloghosts, strikte CSP, geen externe scripts of lettertypen, opnieuw sturen hooguit eens per 30 seconden.
- **Alleen de website** gebruikt de eigen pagina (`own_login`, standaard aan). Het admin panel blijft voorlopig op de pagina van Zitadel, met verplichte passkeys uit Org Beheer. Terug naar de pagina van Zitadel kan met `own_login = false` en `scripts/infra.sh up`.
- **Lokaal** (`docker compose`) blijft de eigen login van de lokale Zitadel in gebruik.

## Afwegingen
- *Zitadel Pro met eigen domein*: duur, en de pagina blijft die van Zitadel. Alleen de kleuren en het logo zijn in te stellen.
- *De login-app van Zitadel zelf hosten*: die valt onder een licentie die we niet in een verkoopbare site willen (ADR 0004), en hij is groter dan wat we nodig hebben.
- *Eén Zitadel-sessie per inlogpoging* in plaats van "ingelogd blijven" op de inlogpagina: eenvoudiger en privacyvriendelijker. De site heeft zelf een sessie van 12 uur of langer.
- *Huisstijl per organisatie* volgt nu uit de redirect-URI. Zodra organisaties ook op hun eigen domein inloggen (inloggen per organisatie staat standaard uit), krijgt elk domein zijn eigen redirect-URI.
