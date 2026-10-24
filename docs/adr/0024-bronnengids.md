# 0024 Bronnengids: linken naar kleurplaten bij de maker

Datum: 24-10-2026. Status: aangenomen.

## Context
Mensen zoeken veel naar kleurplaten van bekende figuren en plekken (een pretpark, een tekenfilmserie). Die tekeningen zijn auteursrechtelijk beschermd en de namen vaak merken. Concurrenten kopiëren ze van internet met een disclaimer "mail ons als het van jou is"; dat beschermt niet, en voor een site met winstoogmerk (partnerlinks) gelden strengere eisen (HvJ EU, GS Media C-160/15). Linken naar werk dat de rechthebbende zelf vrij online zet is geen nieuwe openbaarmaking (Svensson C-466/12, BestWater C-348/13); framen/embedden wel zodra de maker dat technisch tegenhoudt (VG Bild-Kunst C-392/19). Kopiëren, ook als thumbnail, is verveelvoudigen.

## Besluit
- Nieuw domein **Bronnen** (schema `sources`) met `themes` en `sources`. Naam en beschrijving van thema's en titels van bronnen zijn **eigen tekst** in Lokalisatie (entity `theme` en `source`).
- **Alleen links, nooit beeld of inhoud van de maker.** Geen afbeeldingen, thumbnails, embeds of overgenomen tekst. Op de site per thema een eigen letterteken en een knop "Bekijk bij de maker" (nieuw tabblad, `noopener noreferrer nofollow`).
- Elke bron heeft een **basis**: `link` (geen toestemming nodig) of `license` (schriftelijke toestemming van de maker, met notitie en datum). Alleen bij een licentie mag later beeld van de maker getoond worden; daar is nu nog geen veld voor.
- **Alleen officiële bronnen** van de maker of rechthebbende; geen verzamelsites.
- **Goedkeuring**: een nieuwe bron wordt direct gecontroleerd en komt pas online na goedkeuring in het admin panel (`sources.manage`). Een thema gaat pas online met minstens één werkende, goedgekeurde bron.
- **Controle** (`SourceCheckScheduler`): elke bron hooguit eens per 24 uur, hooguit 30 per uur, één tegelijk met pauze. Volgt robots.txt (user agent `KleurhoekLinkCheck`), alleen https, nooit privé-adressen (SSRF-bescherming, ook bij doorverwijzingen), hooguit 1,5 MB, 10 s time-out. We bewaren alleen statuscode, paginatitel (als hulp in het admin panel) en een vingerafdruk van de zichtbare tekst.
  - 404/410 twee keer, of drie fouten op rij, of robots.txt verbiedt het, of doorverwezen naar een ander domein: **automatisch offline** en in de lijst Nakijken. Een goede controle zet hem weer online.
  - Andere vingerafdruk dan bij goedkeuring: blijft online, gemarkeerd als "veranderd" tot iemand hem nakijkt.
- **Producten bij een thema**: een thema kan producten uit de Winkel tonen (echte producten met partnerlink, via `/ga`). De doorklik telt met bron `thema-{code}`. Geen logo's of beeld van het merk.
- Openbare API via Storefront: `GET /v1/markets/{markt}/themes` en `/themes/{code}`. Website: `/{markt}/themas` en `/{markt}/themas/{code}`; link in de voettekst van elke pagina.

## Later: toegang voor makers
Zodra een maker meedoet: een rol `maker` die alleen bij de eigen thema's kan (bronnen bijwerken, eigen platen aanleveren onder licentie, eventueel een feed of API-sleutel). Inloggen via Zitadel zoals beheerders. Pas bouwen als er een echte maker is.

## Gevolgen
- De API maakt uitgaande verbindingen naar sites van makers; alleen vanuit de controle en altijd met de beperkingen hierboven.
- Juridisch blijft het linken; de disclaimer (ADR 0025) legt dit uit en beschrijft hoe een maker een link laat aanpassen.
