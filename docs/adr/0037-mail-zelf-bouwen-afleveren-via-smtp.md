# 0037 · Mail: alles zelf, afleveren via SMTP

- Status: aangenomen
- Datum: 2026-10-25

## Context
Bezoekers willen een mail als er nieuwe platen zijn, als er een feestdag aankomt, of af en toe een nieuwsbrief. De inhoud moet makkelijk te maken zijn (templates), en wat er automatisch gebeurt moet flexibel zijn (workflows). Thijs wil niet afhankelijk zijn van een externe dienst.

## Besluit
- **Alles zelf, behalve het laatste stuk.** Abonnees, templates, workflows, campagnes, de wachtrij, afmelden en tellers zitten in een eigen domein **Berichten** (`apps/api/src/modules/messaging`, schema `messaging`, migratie 0022). Afleveren gaat via SMTP achter één adapter (`MAIL_TRANSPORT`): lokaal Mailpit, op dev en prod een relay. Zonder SMTP staat versturen uit en wachten mails hooguit 3 dagen.
- **Geen eigen mailserver (nog).** Scaleway blokkeert uitgaande mailpoorten tot je je ID verifieert, Serverless Containers kunnen het niet, en een nieuw IP-adres moet maanden reputatie opbouwen bij Gmail en Microsoft. Gaat het mis, dan komen ook bevestigingsmails niet aan. Wordt het volume groot en stabiel, dan wordt een eigen MTA (bijvoorbeeld Postal op een server met vast IP) een extra adapter; verder verandert er niets.
- **Twee soorten verkeer.** Transactioneel (de bevestigingsmail) via `MAIL_TRANSACTIONAL_SMTP_URL`, bulk (welkom, nieuwe platen, feestdagen, nieuwsbrief) via `MAIL_SMTP_URL`. Scaleway TEM staat alleen transactionele mail toe; voor bulk is een dienst nodig die nieuwsbrieven toestaat (bijvoorbeeld Brevo). Beide alleen als SMTP-adres, dus overstappen is één instelling.
- **Aanmelden**: e-mailadres, onderwerpen (nieuwe platen, feestdagen, nieuwsbrief), verklaring 16 jaar of ouder (ADR 0002), bevestigen met een link (double opt-in, 7 dagen geldig). Het antwoord verraadt niet of een adres bekend is; een actief abonnement verandert nooit door opnieuw aanmelden. Vanuit het account: meteen actief, want het adres is bij inloggen al bevestigd. Bevestigen gebeurt met JavaScript op de pagina, zodat linkscanners in mailprogramma's niets bevestigen.
- **Afmelden**: elke bulkmail heeft onderaan Voorkeuren en Afmelden en de headers `List-Unsubscribe` en `List-Unsubscribe-Post` (één klik, RFC 8058, via `/mail/afmelden` op de website). Links werken zonder inloggen met een HMAC-token van de abonnee. Afmelden **verwijdert** de abonnee; alleen tellers zonder persoonsgegevens blijven (`messaging.daily_stats`). Een verwijderd account verdwijnt ook als abonnee.
- **Geen tracking**: geen trackingpixels, geen omgeleide links, geen open- of klikcijfers.
- **Templates zijn blokken** (kop, tekst, knop, platen, lijn) met tekst per taal; ontbreekt een taal, dan Nederlands. De renderer (`render.ts`) maakt mailveilige HTML (tabellen, inline stijlen) en een tekstversie, met kleuren uit `packages/theme/generated/email.json`. Platen staan erin als PNG (resvg, met het lettertype van de platen), op een adres per versie en taal dat eeuwig gecachet mag worden. De mail wordt pas bij versturen gemaakt, met de platen die dan in de markt van de abonnee zichtbaar zijn.
- **Workflows zijn regels met stappen**, geen canvas: een aanleiding (na aanmelden, vaste dag en tijd, nieuwe platen, feestdag komt eraan) en stappen (filter op onderwerp en markt, alleen als er genoeg nieuwe platen zijn, wachten, mail sturen). Elke abonnee loopt per aanleiding hooguit één keer door een workflow, en elke mail is uniek per bron en abonnee: herhaald verwerken (of meerdere API-instances) stuurt niets dubbel. Behalve na aanmelden moet een workflow met een filter op onderwerp beginnen.
- **Campagnes**: een template aan abonnees van gekozen onderwerpen (en eventueel markten), nu of gepland. "Nu versturen" vraagt een vinkje dat de testmail bekeken is.
- **Beheer**: Mail in het zijmenu (overzicht, campagnes, workflows, templates), rechten `mail.read` en `mail.manage`. Een abonnee opzoeken kan alleen op exact adres; er is geen lijst om door te bladeren of te exporteren.
- **Startinhoud**: templates bevestigen, welkom (vast), nieuwe platen, feestdag, nieuwsbrief; workflows welkom, nieuwe platen elke maandag 8:00 (minstens 3), twee weken voor een feestdag.
- Abonnementen gelden voor Kleurhoek zelf; de kolom `organization` houdt de deur open voor scholen later.

## Gevolgen
- Nieuwe afhankelijkheden in de API: `nodemailer`, `@resvg/resvg-js`, `wawoff2`.
- Terraform: variabele `mail` (afzender, SMTP-adressen) en het geheim `MAIL_SECRET`; zonder dat geheim leidt de API het af van `INGEST_KEY`. DNS (SPF, DKIM, DMARC) volgt zodra de dienst gekozen is.
- `docker compose up` heeft Mailpit op http://localhost:8025.
- Bounces en klachten verwerken we nog niet automatisch; bij een relay doet die dienst dat (blocklist). Volgt via een webhook als het volume groeit.
