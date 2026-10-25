# 0038 · Bezorging van mail in eigen beheer

- Status: aangenomen
- Datum: 2026-10-25

## Context
Mail gaat via een relay (ADR 0037). Bounces, spamklachten en afleveringen ziet de relay als eerste. Thijs wil daarvoor niet naar de relay hoeven: inzicht en afhandeling horen in het eigen platform, ongeacht welke relay erachter zit.

## Besluit
- **Eén soort melding, ongeacht de bron.** Afgeleverd, vertraagd, soft bounce, harde bounce, spamklacht en afgemeld. Bronnen:
  - het **SMTP-antwoord** bij het afgeven;
  - **webhooks** van de relay: Brevo, Scaleway TEM (via Topics and Events, SNS-formaat met automatische bevestiging) en een **eigen formaat** voor een eigen mailserver of scripts.
  
  Het lezen van de meldingen zijn pure functies (`messaging/deliverability/feedback.ts`). Een nieuwe dienst kost alleen een nieuwe lezer.
- **Terugkoppelen op onze eigen kenmerken.** Elke mail krijgt onze Message-ID (`<id-van-de-mail@afzenderdomein>`) en de header `X-Mail-Ref`. Een melding koppelen we op die verwijzing, dan op Message-ID, en anders aan de laatste mail aan dat adres (14 dagen).
- **Alleen een weigering van de ontvanger is een harde bounce.** Bij SMTP telt alleen een 5xx op `RCPT TO`. Een 5xx bij inloggen of bij de afzender is een fout in onze eigen instellingen en blokkeert de ontvanger niet.
- **Afhandeling:**
  - Harde bounce of spamklacht: de abonnee verdwijnt en het adres gaat blijvend op de blokkeerlijst.
  - Drie soft bounces binnen 30 dagen zonder aflevering ertussen: 90 dagen pauze.
  - Afgemeld bij de relay: de abonnee verdwijnt.
  - Voor elke mail kijkt de wachtrij of het adres geblokkeerd is.
  - Opnieuw aanmelden na een bounce stuurt geen bevestigingsmail; na een spamklacht wel, en bevestigen haalt het adres van de lijst.
  - Aanzetten vanuit het account haalt het adres altijd van de lijst: het adres werkt (inlogcode) en de keuze is bewust.
- **Privacy:**
  - De blokkeerlijst en de meldingen bevatten geen adressen. Ze bewaren een HMAC van het adres (niet terug te rekenen) en het domein van de ontvanger.
  - Uit de reden van de server filteren we adressen weg.
  - Meldingen bewaren we 180 dagen.
  - Opzoeken kan alleen op exact adres.
- **Inzicht in het admin panel** (Mail › Bezorging, `mail.read`):
  - verstuurd, afgeleverd, bounce- en klachtpercentage tegen de gangbare grenzen van Gmail en Yahoo (bounces: let op vanaf 2 %, slecht vanaf 5 %; klachten: let op vanaf 0,1 %, slecht vanaf 0,3 %, onder 50 mails geen oordeel; design system: HealthCard);
  - verloop per dag, per mailprovider van de ontvanger en per mail (workflow, campagne);
  - de laatste meldingen.
  
  Met `mail.manage` ook: adres opzoeken, blokkeren of vrijgeven, en de webhookadressen.
- **Webhooks** komen binnen op de website (`/mail/events/<dienst>?key=…`) en gaan naar de API. De sleutel per dienst is afgeleid van `MAIL_SECRET`. Deze route en `/mail/afmelden` (POST) slaan de IP-afscherming van dev over (ADR 0015), omdat relay en mailprogramma's niet van een toegestaan IP komen; ze controleren zelf een sleutel of token.
- **Platform**: dit onderdeel weet niets van platen of Kleurhoek. Het verhuist naar `t-jarpis/platform` zodra een tweede site mail verstuurt (platform ADR 0001), niet eerder.

## Gevolgen
- Migratie 0023: `messaging.delivery_events`, `messaging.suppressions` en `deliveries.message_id`, met RLS.
- Na het kiezen van de relay: de webhook instellen met het adres uit Mail › Bezorging.
- DSN-bounces direct ontvangen (Return-Path op ons eigen domein, via Cloudflare Email Routing) kan later. Dat is pas nodig bij een eigen mailserver; relays verwerken de DSN's zelf en melden het resultaat via de webhook.
