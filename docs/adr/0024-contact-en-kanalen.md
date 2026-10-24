# 0024 Contact: formulier, inbox en kanalen

Datum: 24-10-2026. Status: aangenomen.

## Context
Bezoekers moeten ons kunnen bereiken (vragen, ideeën, fouten, auteursrecht, privacyverzoeken). Liever via de website dan via een los e-mailadres, en alles op één plek in het admin panel. Later wil Thijs WhatsApp koppelen en mogelijk andere kanalen.

## Besluit
- Nieuw domein **Contact** (schema `contact`): `conversations` (één gesprek per afzender en kanaal, met onderwerp en status nieuw/open/beantwoord/gesloten), `messages` (in, out, note) en `channels` (aan/uit en instellingen per kanaal, zonder geheimen).
- **Webformulier** op `/{markt}/contact`: onderwerp, naam (optioneel), e-mail, bericht. De website stuurt het door naar `POST /v1/contact` met het IP van de bezoeker alleen voor de rate limit (`contact-submit`: 5 per uur per IP). Geen captcha (privacy); wel een verborgen veld en een minimale invultijd. Spam krijgt gewoon "ontvangen" te zien maar wordt niet opgeslagen.
- **Inbox** in het admin panel (`/contact`) met teller in het menu: lijst per status, gesprek met notities en vastgelegde antwoorden, status wijzigen en direct verwijderen (AVG-verzoek). Een antwoord op een webbericht stuur je vanuit je eigen mail (knop opent het mailprogramma met citaat); in het gesprek leg je vast wat je antwoordde.
- Rechten `contact.read` en `contact.manage` (platformbeheerder en support). Auditregels bevatten nooit naam, e-mail of berichttekst.
- **Bewaartermijn**: een gesprek wordt 12 maanden na het laatste bericht automatisch verwijderd.
- **Kanalen**: web staat standaard aan. WhatsApp staat als kanaal in het model en op de pagina Kanalen, maar is nog niet gekoppeld en kan pas aan als dat wel zo is.

## WhatsApp (volgende stap)
- WhatsApp Cloud API van Meta: een Business-nummer, een app met webhook.
- Token en app-geheim in de secret manager van Scaleway (env van de API), nooit in de database of het admin panel.
- Webhook op de website (`/hooks/whatsapp`, gedeeld pad buiten de organisatie-rewrite) die de handtekening (`X-Hub-Signature-256`) controleert en het bericht aan de API doorgeeft; de API maakt of vindt het gesprek op telefoonnummer (`external_id` voorkomt dubbele aflevering).
- Antwoorden uit het admin panel gaan dan echt naar buiten via de Graph API, binnen het 24-uursvenster van WhatsApp.

## Gevolgen
- Persoonsgegevens van afzenders staan alleen in het domein Contact en gaan niet naar analytics of audit.
- E-mail versturen vanuit Kleurhoek zit er bewust nog niet in; dat vraagt een mailprovider en SPF/DKIM.
