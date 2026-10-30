# 0063 · Social media: voorstellen, goedkeuren en automatisch plaatsen

- Status: aangenomen
- Datum: 2026-10-30

## Context
Kleurhoek heeft bezoekers nodig. Pinterest, Facebook en Instagram zijn voor kleurplaten de beste bronnen, maar elke dag zelf posten kost tijd. Thijs wil dat het zoveel mogelijk vanzelf gaat, en alleen akkoord geven.

## Besluit
- **Domein.** Nieuw domein Social (`apps/api/src/modules/social`, schema `social`) met drie tabellen:
  - kanalen: Pinterest, Facebook, Instagram;
  - posts;
  - instellingen.
- **Voorstellen.** Elke ochtend (vanaf 5 uur, Nederlandse tijd) maakt het domein voorstellen voor vandaag en de twee dagen erna. Dubbele voorstellen worden overgeslagen.
  - **Pinterest:** elke dag een paar platen die er nog niet op staan (standaard 5). Eerst platen van feestdagen die eraan komen, dan het seizoen. Bord per onderwerp of feestdag, het staande plaatje (ADR 0057) en de link naar de plaat.
  - **Facebook, Instagram en delen** (standaard maandag, woensdag en vrijdag om 19.30 uur): één post met dezelfde inhoud in drie vormen. Facebook krijgt een link, Instagram "link in bio" met hashtags, en "delen" krijgt een tekst om zelf in groepen en WhatsApp te zetten. De inhoud kiest het domein in deze volgorde:
    - in december het deurtje van de aftelkalender;
    - anders een feestdag binnen twee weken;
    - anders op maandag een lespakket, op vrijdag iets om te knutselen en verder de plaat van de week.

    Platen van de laatste 60 dagen komen niet terug.
  - **Teksten:** vaste Nederlandse sjablonen met variatie, geen AI-tekstgenerator. Alles is aan te passen voordat het geplaatst wordt.
- **Goedkeuren.** Niets wordt geplaatst zonder akkoord.
  - Elke ochtend om 7 uur komt er één mail met de voorstellen. De mail gaat via de SMTP van Berichten (MAIL_TRANSPORT, nu geëxporteerd).
  - In het admin panel (Social) kan Thijs goedkeuren, afwijzen, de tekst aanpassen of alles in één keer goedkeuren. Het menu toont hoeveel er wacht.
  - Een tekst om te delen heeft knoppen voor kopiëren en de deelknop van de telefoon, en "Gedeeld".
- **Plaatsen.** Elke 5 minuten plaatst het domein goedgekeurde posts waarvan het moment is aangebroken.
  - Pinterest: API v5. Het bord wordt aangemaakt als het nog niet bestaat.
  - Facebook: Graph API v25.0, foto met tekst op de pagina.
  - Instagram: container en publiceren, met een JPEG van 1080 × 1350 (4:5), want Instagram neemt geen PNG aan. Daarvoor is er een nieuw plaatje `post.jpg` in de API, op de site te vinden als `/v1/pins/<markt>/<plaat>.jpg`.
  - Mislukt een post, dan probeert het domein het nog twee keer en zet hem daarna op "mislukt" met de foutmelding. Goedkeuren probeert het opnieuw.
- **Koppelen.** Alleen via de officiële OAuth van Pinterest en Meta, vanuit het admin panel. We gebruiken geen wachtwoorden en geen scraping.
  - De app-sleutels staan in Terraform (blok `social`) en gaan als geheim naar de API.
  - De sleutels die we na het koppelen krijgen, staan versleuteld in de database (AES-256-GCM met SOCIAL_SECRET).
  - De OAuth-state is ondertekend en 15 minuten geldig, en het terugkeeradres moet op het admin panel liggen (ADMIN_URL).
  - De toegangssleutel van Pinterest wordt vernieuwd voordat hij verloopt. Een paginasleutel van Meta verloopt niet.
- **Rechten.** `social.read` en `social.manage`. Contentbeheerders krijgen beide, analisten alleen lezen.

## Gevolgen
- **Pinterest:** pins zijn pas voor iedereen zichtbaar als de Pinterest-app "Standard access" heeft. Die vraag je aan met een demofilmpje van de koppeling. Tot die tijd zijn ze alleen voor jezelf zichtbaar.
- **Meta:** voor de eigen pagina is geen App Review nodig zolang Thijs een rol op de app heeft. De app moet wel op Live staan.
- **Facebook-groepen:** kan niet automatisch, want Meta sloot de Groups API in 2024. Daarom bestaat het kanaal "delen".
- Zonder gekoppelde kanalen maakt het domein alleen teksten om te delen.
- De markt is voorlopig alleen nl-nl; de teksten zijn Nederlands.
