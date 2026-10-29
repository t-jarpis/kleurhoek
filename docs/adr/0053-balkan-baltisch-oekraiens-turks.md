# 0053 · Bulgarije, Balkan, Baltische staten, Oekraïne en Turkije

- Status: aangenomen
- Datum: 2026-10-26

## Context
Na ADR 0052 waren er 43 markten in zeventien talen. Van de EU-landen ontbraken nog Bulgarije, Kroatië, Slovenië en de Baltische staten. Buiten de EU ontbraken Oekraïne en Turkije, en de landen rond Kroatië, waar men Kroatisch goed leest.

## Besluit
- **Nieuwe markten op kleurhoek.com:** bg-bg, hr-hr, sl-si, et-ee, lv-lv, lt-lt, uk-ua en tr-tr. Daarnaast hr-ba (Bosnië) en hr-me (Montenegro) met de Kroatische vertaling. Browsers die `bs` sturen, komen op hr-ba.
- **Acht nieuwe talen** met alle onderdelen (ADR 0029), gecontroleerd met `check-lang`. Bulgaars en Oekraïens gebruiken de Cyrillische tekenset uit ADR 0052.
- **Kalenders:**
  - **Pasen:** Bulgarije, Oekraïne en Montenegro vieren Pasen op de orthodoxe datum.
  - **Sint-Nicolaas:** op 6 december in Kroatië, Slovenië (Miklavž), Oekraïne, Bosnië en Montenegro.
  - **Kerst en Pasen in Turkije:** daar staan ze niet in de kalender, omdat ze er niet algemeen gevierd worden. Oud en nieuw, het Suikerfeest en het Offerfeest staan er wel.
  - **Moederdag:** in Slovenië op 25 maart en in Litouwen op de eerste zondag van mei.
  - **Vaderdag:**
    - Kroatië: 19 maart
    - Estland: tweede zondag van november
    - Letland: tweede zondag van september
    - Litouwen: eerste zondag van juni
  - Verder per land de eerste schooldag, de tijdzone, Driekoningen en carnaval.
- **Leeftijd voor een account:** per land volgens de AVG-grens. In Turkije is dat 18 jaar, omdat de KVKK voor minderjarigen toestemming van een ouder vraagt.

## Gevolgen
- Er zijn 53 markten in 25 talen, en alle EU-landen hebben een markt.
- Servië, Noord-Macedonië, Albanië en IJsland ontbreken nog.
- Rusland en Belarus blijven buiten beschouwing vanwege de sancties.
