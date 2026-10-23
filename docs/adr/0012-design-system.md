# 0012 · Design system: eerst vastleggen, dan bouwen

- Status: aangenomen; stijl Studio doorgevoerd in website en admin op 23-10-2026 (zie ADR 0016)
- Datum: 2026-10-22

## Context
Kleurhoek moet een echt merk worden en tegelijk professioneel zijn, voor jong en oud: kinderen van 2 tot 9+ (deels nog niet lezend, vaak op een tablet), ouders en grootouders, en de beheerder. De website en het admin panel hebben elk een eigen `globals.css` zonder gedeelde bron: losse kleuren (meer dan 25 hex-waarden buiten de tokens, drie paarse tinten), geen schaal voor letters, ruimte en radii, en een aantal toegankelijkheidsfouten (randen van invoer en chips op 1,38:1, geen focusring op de kleurvakjes, knoppen onder de 48px voor kinderen, witte knoptekst in admin donker op 2,61:1). Er komen meer functies (feedimport, rapportages, eigen webshop, betaalde functies, meer markten, later een app) en mogelijk meer sites op hetzelfde platform.

## Besluit
- **Eén design system** met merk, tokens, componenten en spelregels: het [Kleurhoek design system](https://claude.ai/artifact/L7Df2x1wNxdihbVvuKuRMt). Het volledige voorstel van de UX-review staat in `docs/design-system/voorstel.md`.
- **Hoofdregel:** elke nieuwe of gewijzigde component, variant of staat komt eerst in het design system (spec, tokens, preview) en wordt pas daarna gebouwd. Geen losse hex-waarden of maten in componenten.
- **Merk:** kleur is voor kinderen en inhoud, rust is voor volwassenen. Oki en Sjors als gidsen in het kinderdeel.
- **Stijl: Studio** (gekozen door de eigenaar op 22-10-2026 uit zeven richtingen; de eerste vier vond hij te speels). Gebroken wit (`#f6f6f4`) met witte kaarten, 1px randen, hoeken van 8px, inktzwarte knoppen (`#18181b`), één lettertype (Manrope). Kleur alleen in de platen, de krijtdoos, categoriestippen van 8px en het logo: vier krijtblokjes (2 bij 2) plus "kleurhoek" in kleine letters. Blauw (`#2f5bd3`) alleen voor links en focus. Geen pilvormen, geen kanteling.
- **Drie modi** via `data-mode`: kind (48px, icoon plus tekst, nooit commercieel), ouder (44px, 17px tekst, partnerlinks alleen hier) en beheer (compact).
- **Techniek:** tokens als CSS custom properties uit één tokenbestand (ook als TypeScript voor de API en later de app), één gelaagde `ui.css`, server components als standaard, React Aria Components alleen voor complexe interactie. Geen Tailwind, geen componentbibliotheek. Logische CSS-eigenschappen voor RTL; A4 en Letter via benoemde printpagina's.
- **Plek:** eerst in deze repo als `packages/ui-core` (site-agnostisch, met guard) en `packages/brand` (merk). Bij een tweede site verhuist `ui-core` naar het platform als `@t-jarpis/tokens` en `@t-jarpis/ui`; het merk en de kindcomponenten blijven altijd in de site (platform ADR 0001, ADR 0004).
- **Documentatie en tests:** werkbankpagina's in de app (geen Storybook), Playwright-screenshots in Docker, axe-controles en printtests in CI.

## Gevolgen
- Het architectuurdocument heeft een sectie Design system en een open beslissing over de merkkeuzes.
- Doorvoeren gebeurt in fasen (zie het voorstel, §7): vangnet en snelle reparaties, kern-componenten, interactie, merk, daarna per functie. Pas bij uitvoering gaat de status naar aangenomen.
- Open vragen voor de eigenaar staan in het voorstel, §8.
