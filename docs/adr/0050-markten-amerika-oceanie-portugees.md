# 0050 · Veertien markten erbij: Amerika, Oceanië, Luxemburg en Portugees

- Status: aangenomen
- Datum: 2026-10-26

## Context
Na ADR 0046 waren er veertien markten in zeven talen. Een groot deel van de vraag naar kleurplaten zit in landen die een taal delen met een bestaande markt (Latijns-Amerika, Canada, Australië) en in Brazilië.

## Besluit
- **Nieuwe markten op kleurhoek.com:**
  - Engels: en-ca, en-au, en-nz.
  - Frans: fr-ca, fr-lu.
  - Duits: de-lu, de-li.
  - Italiaans: it-ch.
  - Spaans: es-mx, es-ar, es-co, es-us.
  - Portugees: pt-br, pt-pt.
- **Papier:** Letter in Canada, Mexico, Colombia en de VS (`isLetter`, `paperSize` in de seed). Elders A4.
- **Schrijfwijze per markt** (`messages(market)`, ADR 0047):
  - Latijns-Amerika en es-us krijgen "ustedes" in plaats van "vosotros", "celular" en "computadora" (`i18n/es-419.ts`). Letter-markten krijgen "tamaño carta".
  - fr-ca krijgt "format lettre", en-ca "letter".
  - de-li krijgt geen ß, net als de-ch.
  - Portugees is één vertaling op Braziliaanse basis, waar mogelijk met woorden die ook in Portugal goed klinken. pt-pt leest dus Braziliaans Portugees.
- **Kalenders:**
  - Moederdag, vaderdag en eerste schooldag per land. Het schooljaar begint op het zuidelijk halfrond in januari, februari of maart.
  - Thanksgiving in Canada (2e maandag van oktober).
  - Valentijn in Brazilië op 12 juni en in Colombia in september.
  - Driekoningen, carnaval en Sinterklaas (6 december) waar die gevierd worden.
  - De herfst op het zuidelijk halfrond is een eigen seizoen (`herfst-zuid`, maart tot mei) voor AU, NZ, AR en BR.
  - Tijdzones per land.
- **Taal zonder eigen landmarkt:** Frans buiten Europa gaat naar fr-fr, Spaans uit Latijns-Amerika naar es-mx en Portugees naar pt-br (`bestMarket`).
- **Sitemap als index:** /sitemap.xml wordt een sitemapindex met per markt /sitemap/<markt>.xml. Met 28 markten zou één bestand met alle taalversies boven de grens van 50 MB uitkomen.
- **Vindbaarheid:** standaardtitels en -omschrijvingen per markt in seo.json (ADR 0047), met de zoekwoorden van dat land, zoals "colouring in pages" (AU, NZ) en "desenhos para colorir" (BR, PT).

## Gevolgen
- Er zijn 28 markten in acht talen. Een markt in een bestaande taal kost alleen kalender, seo-tekst en een regel in de seed.
- De vertalingen van platen zijn per taal. Spaans in Latijns-Amerika leest in platen dus soms Spaans uit Spanje, en Engels in de VS Britse spelling.
- In Search Console de sitemap per domein opgeven: /sitemap.xml (de index) is genoeg.
