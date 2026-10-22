# 0007 · Inloggen, rollen en sessies

- Status: aangenomen
- Datum: 2026-10-22

## Context
Inloggen loopt via Zitadel (zie ADR 0003 in `t-jarpis/platform`). Kleurhoek moet bepalen wie in het admin panel mag, welke websitegebruikers er zijn, en waar de sessie staat.

## Besluit
- **Twee soorten gebruikers, twee organisaties in Zitadel.** Websitegebruikers (ouders, leerkrachten; 16+) zitten in organisatie *Kleurhoek*. Beheerders zitten in *Org Beheer*, met verplichte passkeys. De API accepteert op `/v1/admin/*` alleen tokens van Org Beheer en op `/v1/me` alleen tokens van de site-organisatie. Een beheeraccount werkt dus niet op de website en andersom.
- **Wie iemand is, zegt Zitadel; wat iemand mag, zegt Kleurhoek.** Rollen en permissies staan in `identity.roles` en `identity.user_roles`, niet in het token. Ingebouwde rollen (platformbeheerder, contentbeheerder, analist, support) worden bij elke start bijgewerkt naar de code (`permissions.ts`). Bij verkoop gaan rollen en toekenningen mee met de database.
- **Just-in-time accounts.** Bij het eerste geldige token maakt de API de gebruiker aan in `identity.users` en haalt naam, e-mail en taal op via Zitadel userinfo (hooguit één keer per dag opnieuw). We bewaren niets anders: geen geboortedatum, geen IP-adres.
- **Eerste beheerder.** `ADMIN_BOOTSTRAP_SUBJECTS` noemt de Zitadel-ID's die bij hun eerste login platformbeheerder worden. Daarna gaat alles via het admin panel, met auditlog. Een beheerder kan zijn eigen rollen en status niet wijzigen, zodat niemand zichzelf per ongeluk buitensluit.
- **Deny by default.** Elk admin-endpoint vraagt precies één permissie. Een endpoint zonder permissie is voor niemand; een nieuwe beheerder zonder rol ziet niets. Geblokkeerde gebruikers worden bij elk verzoek geweigerd, ook met een nog geldig token.
- **Sessie als versleutelde cookie, niet in Redis.** Website en admin panel gebruiken de BFF uit `@t-jarpis/auth`: tokens blijven op de server en de browser krijgt één `HttpOnly`-, `Secure`-, `SameSite=Lax`-cookie, versleuteld met AES-256-GCM (`__Host-`-prefix in productie). Websitesessies duren 30 dagen, beheerderssessies 12 uur. De proxy van het admin panel ververst het access token vóór een pagina rendert.
- **Pagina's blijven cachebaar.** De website rendert voor iedereen dezelfde HTML. De accountknop vraagt `/auth/session` los op; die geeft alleen een voornaam terug, nooit tokens.
- **Wijzigingen alleen vanaf de eigen site.** Uitloggen en account verwijderen accepteren alleen `POST`/`DELETE` met `Sec-Fetch-Site: same-origin` (of een gelijke `Origin`). Uitloggen geeft het Zitadel-adres terug in JSON, zodat de CSP `form-action 'self'` kan blijven.
- **Recht op vergetelheid.** `DELETE /v1/me` verwijdert het account met rollen. Het auditlog bewaart alleen het ID, geen naam of e-mail. Het login-account in Zitadel beheert de gebruiker daar zelf; dat koppelen we in een volgende stap aan een Zitadel-actie.

## Afwegingen
- **Cookie in plaats van Redis**: geen extra dienst en geen opslag van sessies, en het schaalt vanzelf over replica's. Nadelen: een cookie is niet centraal in te trekken. Daarom zijn beheerderssessies kort, controleert de API bij elk verzoek de status van de gebruiker, en trekt uitloggen bij Zitadel de refresh token in. Cookies mogen maximaal 4 KB zijn; met Zitadel-tokens zitten we rond de 2 tot 3 KB. Wordt dat te krap, dan splitsen we de cookie of stappen we alsnog over op Redis, zonder dat sites iets merken.
- **Rollen in de eigen database in plaats van Zitadel-projectrollen**: iets meer code, maar rechten zijn te testen, staan in het auditlog en gaan mee bij verkoop.

## Gevolgen
- Productie start niet zonder `OIDC_ISSUER`, `OIDC_AUDIENCE`, `ADMIN_ORG_ID` en `SITE_ORG_ID` (API) en zonder Zitadel-instellingen (admin panel). `ADMIN_DEV_TOKEN` blijft alleen lokaal.
- Tests draaien tegen de nep-Zitadel uit `@t-jarpis/auth/testing`, ook een volledige browserflow.
