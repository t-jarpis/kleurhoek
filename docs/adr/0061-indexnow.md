# 0061 · IndexNow: nieuwe pagina's zelf aanmelden bij Bing

- Status: aangenomen
- Datum: 2026-10-30

## Context
ChatGPT en Copilot zoeken in de index van Bing. Een zoekmachine vindt nieuwe pagina's vanzelf via de sitemap, maar dat kan weken duren. Voor de aftelkalender (ADR 0058) telt elke week. Google biedt geen manier om gewone pagina's automatisch aan te melden; dat kan alleen met de hand in Search Console.

## Besluit
- **Sleutel.** De productiedomeinen geven een IndexNow-sleutel op `/indexnow.txt`. De sleutel staat in de code (`lib/indexnow.ts` en `scripts/indexnow.mjs`) en is geen geheim: zoekmachines gebruiken hem om te zien dat een aanmelding echt van het domein komt. Buiten productie geeft het adres 404 (ADR 0040).
- **Aanmelden.** Na elke geslaagde uitrol naar productie draait `scripts/indexnow.mjs` in de Deploy-workflow:
  - het leest de sitemaps van kleurhoek.nl, .be en .com;
  - het vergelijkt die met de lijst van de vorige keer, die in de cache van GitHub Actions staat;
  - het meldt alleen nieuwe adressen aan bij api.indexnow.org, dat ze doorgeeft aan Bing, Yandex, Seznam en Naver.

  De eerste keer, of met `--all`, gaat alles mee.
- **Mislukken.** Een mislukte aanmelding laat de uitrol niet mislukken. De lijst wordt dan niet bijgewerkt, zodat de volgende uitrol het opnieuw probeert.

## Gevolgen
- Nieuwe platen, onderwerppagina's en lespakketten staan meestal binnen een dag bij Bing.
- Gewijzigde pagina's met hetzelfde adres worden niet opnieuw aangemeld; die vindt Bing via de sitemap.
- Google blijft handwerk: indexering aanvragen in Search Console.
