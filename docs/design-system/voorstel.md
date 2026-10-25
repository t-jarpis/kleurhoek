# Design system Kleurhoek – voorstel

Status: voorstel, nog niets doorgevoerd. **Stijl gekozen op 22-10-2026: Studio** (zie ADR 0012 en het design system); de merk- en tokenwaarden hieronder zijn daardoor deels vervangen · Datum: 2026-10-22 · Bronnen: `kleurhoek/apps/web`, `kleurhoek/apps/admin`, `kleurhoek/docs/adr`, `platform/packages`, screenshots `e2e/shots/1–8`.

**Leidend doel (van de eigenaar):** Kleurhoek moet echt een merk zijn, en tegelijk professioneel. Het moet werken voor jong en oud: voor een kleuter van vier, voor een ouder die snel iets wil printen, en voor een opa van 72 die het op een tablet opent.

In één zin: **"Kleur is voor kinderen en inhoud, rust is voor volwassenen."** De interface zelf is rustig: wit papier op een koelgrijze tafel, inktzwart, één blauw accent. Kleur komt van de platen, de krijtkleuren, het logo en de mascottes. Zo voelt het speels zonder druk te worden, en betrouwbaar zonder saai te worden.

---

## 0. Merk

### 0.1 Merkpositie
**Kleurhoek is de rustige, eerlijke plek waar kinderen kleuren en knutselen met platen die speciaal voor hen gemaakt zijn, en waar volwassenen zonder gedoe kunnen printen, voorbereiden en de juiste spullen vinden.**

- **Belofte:** *Eigen ontwerpen. Eerlijk. Klaar om te printen.* (Gemaakt met hulp van AI en nagekeken; nooit "met de hand" of "zelf getekend" claimen.)
- **Bewijs dat er al is:** eigen ontwerpen, geen bekende figuren (CLAUDE.md), partnerlinks met uitleg erbij, en print op ware grootte. Privacy en geen reclame in het kinderdeel zijn uitgangspunten (ADR 0002 en 0011), geen verkoopargument in teksten.
- **Wat ons onderscheidt van de grote kleurplatensites** (vol advertenties, rommelig): rust, vakmanschap en eerlijkheid. Dat moet je *zien*, en daar is dit design system voor.

### 0.2 Persoonlijkheid (vier eigenschappen, elk met een grens)

| Wel | Niet | Hoe je het ziet |
|---|---|---|
| **Speels** | druk, schreeuwerig | Krijtkleuren in logo, chips en platen. Papier dat bij hover een klein beetje kantelt. Oki en Sjors. Maar nooit meer dan één animatie tegelijk, en geen knipperende dingen. |
| **Warm** | kinderachtig, zoetsappig | Ronde letters (Sniglet) alleen voor koppen, rustige Nunito voor tekst. Je-vorm. Geen babytaal. |
| **Vakkundig** | zakelijk-koud | Strakke printstijl, duidelijke knip-, vouw- en lijmlijnen, exacte informatie ("papier van 160 gram"). |
| **Eerlijk** | belerend, verstoppen | Partnerlinks zichtbaar gemarkeerd, met uitleg. Privacytekst in gewone taal. |

### 0.3 Merkdragers (wat Kleurhoek herkenbaar maakt)
1. **Het krijtdooslogo**: "Kleurhoek" in Sniglet 800, elke letter in een krijtkleur (rood, amber, groen, blauw, paars).
2. **Papier op tafel**: witte vellen (`--color-paper`) met een zachte schaduw op de koelgrijze tafel (`--color-bg`), bij hover licht gekanteld. Dit is de belangrijkste visuele metafoor, en hij moet overal terugkomen: kaarten, studio, boekje, koelkast.
3. **Het labeltje**: de chipvorm met een rechte kant en een ronde kant (`border-radius: 6px 999px 999px 6px` in `.chip`) met een kleurblokje. Dit wordt het vaste vormpje voor categorieën.
4. **Huiselijke objecten als interface**: de scheurkalender (`.tear`), de koelkast met magneten (`.fridge`, `.mag`) en het boekje. Nieuwe functies krijgen waar het kan ook zo'n object (bijvoorbeeld een "knutseldoos" voor de winkel) in plaats van een generiek scherm.
5. **Oki (uil) en Sjors (slak)**: ze staan nu alleen op het voorblad van het boekje (`Booklet.tsx`) en in teksten ("Sjors zoekt nog", "Oki is trots op je"). Ze worden de vaste gidsen in het kinderdeel: lege staten, 404, het feestmoment bij voltooien, en laden.
6. **De lijn**: ronde uiteinden, gelijkmatige dikte die per leeftijd verschilt (3,4 / 2,8 / 2,4 …). Iconen, mascottes en illustraties gebruiken dezelfde lijn.

### 0.4 Tone of voice
Regels:
- Altijd **je/jij**, ook tegen ouders. Korte zinnen; in het kinderdeel maximaal ongeveer 10 woorden en één opdracht per zin.
- **"Tik"** in het kinderdeel (tablets), **"kies"** of **"klik"** nooit in kindteksten.
- Knoppen beginnen met het werkwoord of zijn het werkwoord: "Printen", "Boekje printen", "Op de koelkast".
- Uitroeptekens alleen bij een feestmoment, maximaal één. Geen emoji in de interface.
- Concreet boven bijvoeglijk: "ongeveer 30 minuten" in plaats van "snel en makkelijk".
- **Nooit een kind aansporen om iets te kopen** of een volwassene te vragen dat te doen (ACM, ADR 0011).
- Pijlen en andere tekens horen niet in de vertaalde tekst: nu staat `back: "← Alle platen"` in `nl.ts`. Dat gaat mis bij RTL. Het icoon hoort in de component.

| Situatie | Doen | Niet doen |
|---|---|---|
| Uitleg voor kind | "Tik op een kleur en dan op de tekening." | "Selecteer een kleur uit het palet om een vlak te vullen." |
| Feestmoment | "Helemaal goed! Oki is trots op je." | "SUPER GEDAAN!!! Je bent een kampioen!!!" |
| Lege staat | "Sjors zoekt nog. Kies een ander onderwerp." | "Geen resultaten gevonden." |
| Info voor ouders | "Ongeveer 30 minuten · met hulp van een volwassene · papier van 160 gram" | "Een superleuk en leerzaam knutselavontuur voor het hele gezin!" |
| Partnerlink | "Partnerlink · bij bol. Kleurhoek krijgt een kleine vergoeding, jij betaalt hetzelfde." | "Bestel nu, op = op!" of "Vraag papa of mama om deze schaar!" |
| Fout | "Je account kan nu niet geladen worden. Probeer het later opnieuw." | "Error 500: request failed" |
| Iets definitief verwijderen | "Account verwijderen? Je naam en e-mailadres worden gewist. Dit kun je niet terugdraaien." | "Zeker weten? Tik nog eens" (prima voor "Haal eraf", te licht voor een account) |
| Beheer | "Opgeslagen. De wijziging staat in het auditlog." | "Yay, gelukt!" |
| Privacy | "We bewaren alleen je naam en e-mailadres." | "Wij nemen uw privacy zeer serieus." |

### 0.5 Logogebruik
**Nu:** het logo is live tekst. In `Logo.tsx` is elke letter een `<span>`, en `globals.css:27–29` kleurt de letters met `nth-child(9n+…)`. Daar zitten vier problemen aan:
- het hangt af van het laden van het font (tot dan zie je het in Trebuchet);
- de kleuren zijn hardcoded en het paars (`#9b4fd0`) staat in geen enkele andere lijst;
- het patroon werkt alleen voor precies 9 letters;
- voor de BOIP-registratie, die al als taak in het admin-overzicht staat (`winkel/page.tsx`), heb je een vast beeld nodig.

**Voorstel:**
- **Hoofdlogo als SVG**, met de letters uitgetekend als vormen. Het staat in `@kleurhoek/brand/logo/`.
- **Varianten:** volledige kleur op licht; volledige kleur op donker (blauw `#7c9cff`, paars lichter); één kleur in inkt; één kleur in wit; en een **beeldmerk**: de "K" in rood met een krijtpuntje, voor de favicon, het app-icoon en de sociale avatar.
- **Vrije ruimte** rondom: minstens de hoogte van de "o". **Minimale grootte:** 24 px hoog op scherm, 8 mm in print.
- **Niet doen:** een ander font gebruiken, de kleurvolgorde veranderen, verlopen of schaduwen toevoegen, het logo op een plaat of foto zetten, het uitrekken, of een letter een andere kleur geven per seizoen. Seizoensaccenten mogen wel ernaast, als losse illustratie.
- **In beheer:** het beeldmerk plus "beheer" in Nunito 800, klein. Geen volledig kleurlogo.
- **Toegankelijkheid:** het logo valt onder de uitzondering voor logo's in WCAG 1.4.3 (amber `#f2a516` haalt maar 1,83:1 op `--color-bg`). De toegankelijke naam blijft "Kleurhoek" (`aria-label`), en het logo is een link naar de home van de markt.

### 0.6 Illustratiestijl van de platen (vastleggen, want het werkt al)
- **Formaat:** viewBox-breedte 200; de hoogte volgt A4 (200 voor kleurplaten, 270 voor de lampion, ADR 0010).
- **Lijn:** één inktkleur (`--plate-ink`). Ronde uiteinden en hoeken (`stroke-linecap/linejoin: round`). De dikte komt van de leeftijd (`ages.json`: 3,4 / 2,8 / 2,4 …) en staat nooit vast in de SVG.
- **Vlakken:** gesloten en klikbaar (`.r[data-i]`), zonder vulling in de bron. Minimale vlakgrootte per leeftijd: voor 2–4 jaar groot genoeg voor een vingertop. Dat maakt het ook een touch-eis.
- **Gezichten:** eenvoudig (twee ogen, een glimlach), vriendelijk en nooit eng, ook bij Halloween.
- **Inclusief:** feestdagen en landen uit veel culturen, zoals nu al met Divali, Chanoeka, Suikerfeest en Keti Koti. Mensen zo tekenen dat elke huidskleur werkt (ingekleurd door het kind).
- **Knutsellijnen** blijven vaste klassen: `.cut` (streepjes 4–3), `.fold` (stippels 1–2,5), `.glue` (grijs vlak), `.tip` (6 px uitleg). Altijd met een legenda (knippen, vouwen, lijmen), zoals in screenshot 3.
- **Geen tekst in de tekening.** Tekst (naam, woord, telvraag) is een laag van `Sheet.tsx`, zodat hij vertaald kan worden.
- **Mascottes en iconen** gebruiken dezelfde lijn. Zo hoort de interface bij de platen.

### 0.7 Hoe kind- en ouderdeel bij elkaar horen
Het is één merk met drie "volumes", vastgelegd als **modus** (zie §4.10):

| | **kind** (home, studio, koelkast) | **ouder** ("Voor ouders", account, boekje maken, straks kassa) | **beheer** (admin) |
|---|---|---|---|
| Koppen | Sniglet, groot | Sniglet voor sectietitels, de rest Nunito | alleen Nunito |
| Kleur | krijtkleuren in chips, palet, mascottes | neutraal plus één accent; categoriekleur alleen als blokje | neutraal plus accent; kleur alleen voor status |
| Bediening | ≥ 48 px, icoon plus tekst, pilvorm | ≥ 44 px, pilvorm | ≥ 32 px (WCAG-minimum 24 px), hoek 8 px |
| Tekst | kort, "tik" | volledige zinnen, 17 px lopende tekst (voor grootouders) | compact, 15 px |
| Commercieel | **nooit** | alleen hier, altijd gemarkeerd | rapportage |

De naad tussen kind en ouder is zichtbaar: het blok "Voor ouders" krijgt een eigen bovenlabel met icoon, een ander oppervlak (`--color-surface` met rand) en de modus `ouder`. Een kind ziet dat dit "niet van mij" is. Een ouder ziet dat het zorgvuldig gescheiden is, en dat wekt vertrouwen.

---

## 1. Analyse van de huidige UI

### 1.1 Wat goed is (behouden)
- **Er zijn al tokens.** `apps/web/src/app/globals.css:2–15` gebruikt custom properties (`--bg`, `--surface`, `--fg`, `--muted`, `--line`, `--accent`, `--sheet`, `--ink`) met een donkere variant. Dat is een prima basis zonder Tailwind of runtime.
- **Een sterke, eigen beeldtaal**: papier op tafel, de scheurkalender, de koelkast met magneten, labelchips met kleurblok, leeftijdsstipjes (`.lv`). Screenshot 1 ziet er al als een merk uit.
- **Goede gewoonten:** een globale `:focus-visible` (3 px, offset 3), `prefers-reduced-motion` gerespecteerd, `aria-pressed` op toggles en filters, `role="status"` op de toast, `aria-live` in de PickBar, `rel="sponsored nofollow"` op partnerlinks, `safe-area-inset` voor iPhones, een printstijl met `@page`, en fonts zelf gehost.
- **Server components waar het kan.** `PlateCard`, `ForParents`, `SeasonBand` en `Logo` zijn server-side, en alleen interactieve delen hebben `"use client"`. Dat moet zo blijven.
- **Het admin panel is netjes en rustig** (screenshots 5–7). Tabellen hebben `tabular-nums`, numerieke kolommen staan rechts uitgelijnd en de lege staten zijn goed geschreven.
- **De teksten** (`i18n/nl.ts`) zijn warm, kort en concreet. Dat is al de juiste toon.

### 1.2 Inconsistenties en problemen (concreet)

**Twee losse stijlsets zonder gedeelde bron**

| | `apps/web/.../globals.css` | `apps/admin/.../globals.css` |
|---|---|---|
| achtergrond | `--bg: #eef2f4` | `--bg: #f4f6f8` |
| tekst | `--fg: #22222b` | `--fg: #1f232a` |
| lijn | `--line: #d5dde2` | `--line: #dde3e8` |
| succes | `--ok: #23884a` | `--good: #23884a` (andere naam) |
| fout | `--cal: #e2483d` ("kalender" als foutkleur) | `--bad: #b42318` (andere kleur) |
| randdikte | 2 px | 1 px |
| knop | `.btn` (pil, omlijnd) | globale `button {}`: **elke** knop is blauw en gevuld |
| linkknop | `a.btn` | `a.button` |
| `.note` | voetnoot met stippellijn | info-callout met blauwe rand (zelfde naam, andere betekenis) |
| `.panel` | radius 14, rand 2 px | radius 12, rand 1 px |

**Hardcoded kleuren buiten de tokens** (≥ 25 plekken)
- `globals.css:27–29`: logokleuren `#e2483d #f2a516 #2fa45a #9b4fd0`.
- `globals.css:39–42`: `.tear` met `#1d1b22`, `#fff`, `#5d6672`.
- `globals.css:121`: `.toast { background: #23884a }`. Dat is de waarde van `--ok`, maar zonder de token, dus hij past niet mee in donker.
- `globals.css:90–96, 200–208, 228–231`: platen en A4 met `#1d1b22`, `#8a9099`, `#c3c9cf`, `#6b7280`, `#d5dde2`, `#d5d9de`, `#9aa1a9`, `#4a5260`. `--ink` bestaat al, maar wordt maar half gebruikt.
- `Fridge.tsx:402`: `MAGNETS = ["#e2483d", "#2f5bd3", "#f2c618", …]` in TSX.
- `labels.ts:3` `FEEST = "#13a3a0"` **en** `Browse.tsx:312` `"#13a3a0"` (dubbel), plus de fallback `"#888"` in `labels.ts`.
- `Booklet.tsx:154,163`: `stroke="#1d1b22"`, `fill="#5d6672"` als SVG-attributen.
- Admin `globals.css:280,289,297`: `color: #fff` op `--accent`, ook in donker (zie contrast).
- **Paars bestaat drie keer:** `#9b4fd0` (logo), `#5b4fc9` (categorie Ruimte, `categories.json`), `#7b5bd6` (krijtdoos, `studio.ts`).
- **Categoriekleuren zijn hex in de database** (`catalog.schema.ts: color text`, gevuld uit `categories.json`). Een merkaanpassing of een donkere variant vraagt dan een datamigratie.

**Typografie: geen schaal.** In de web-CSS staan 12 vaste groottes (10, 11, 12, 13, 14, 15, 16, 18, 20, 22, 28, 44 px) plus 6 verschillende `clamp()`-koppen (`.logo`, `.studio-top h1`, `.page-title`, `.sec`, `.parents-head h2`, `.season-txt h2`). Daarbij vier letterafstanden (.04/.08/.12/.14 em). Het label in hoofdletters staat op 12 px (`.eyebrow`, `.flabel`, `.tools h2`, admin `th`). Dat is aan de kleine kant voor grootouders. De tekst "Haal eraf" op de koelkast staat zelfs op 12 px (`.magw small` > `.linkbtn`).

**Spacing: geen schaal.** Er worden 13 verschillende gaps gebruikt (2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 28 px) en paddings als `9px 16px`, `7px 16px 7px 10px`, `5px 12px 5px 8px` en `6px 13px`.

**Radii: 12 waarden.** 2, 3, 4, 6, 8, 10, 12, 14, 20, 22, 999 en de tagvorm `6px 999px 999px 6px`.

**Focus**
- **Bug:** de kleurvakjes in de studio (`.sw`, `globals.css:111`) gebruiken `all: unset`. Die regel staat ná `:focus-visible` en heeft dezelfde specificiteit, dus de focusring verdwijnt. **Met het toetsenbord zie je niet welke kleur focus heeft.** Alleen de gekozen kleur heeft een ring (via `aria-pressed`).
- `.seg button:focus-visible` heeft geen offset, en `.linkbtn` heeft een ring van 2 px in plaats van 3. Dat is ongelijk.
- Admin heeft **geen eigen focusstijl**, dus de standaardring van de browser, die op blauwe knoppen slecht te zien is.

**Contrast (berekend, WCAG 2.2), de belangrijkste overtredingen**

| Paar | Waar | Ratio | Eis | |
|---|---|---|---|---|
| `--line #d5dde2` op wit | rand van `.input`, `.chip`, `.seg`, admin-inputs | **1,38** | 3:1 (1.4.11) | ✗ |
| `--line` op `--bg #eef2f4` | `.chip` en `.seg` op de tafel | **1,22** | 3:1 | ✗ |
| `#e2483d` op wit | `.btn.danger` tekst (15 px/800) | **4,02** | 4,5:1 | ✗ |
| wit op `#23884a` | `.toast` (Sniglet 20 px/400, geen "grote tekst") | **4,48** | 4,5:1 | ✗ (net) |
| `#23884a` op tint 15 % | admin `.pill.on` (12 px) | **≈ 3,7** | 4,5:1 | ✗ |
| wit op `#7c9cff` | admin-knoppen en tabs in **donker** | **2,61** | 4,5:1 | ✗ |
| `#2f5bd3` op `#1f232a` | n.v.t. (web wisselt goed naar `#7c9cff`) | 2,67 | | (ter info) |
| `#22222b` op `#eef2f4` | lopende tekst | 14,0 | | ✓ |
| `--muted #5d6672` op `--bg` | hints, labels | 5,17 | | ✓ |
| `--accent #2f5bd3` op wit / op bg | links, `.offer` | 5,90 / 5,24 | | ✓ |
| `--muted #a3abb6` op `#1f232a` (donker) | | 6,80 | | ✓ |

**Touch targets** (berekend uit de CSS; Nunito `line-height: normal` ≈ 1,36)

| Element | Hoogte ongeveer | Voor kinderen (≥ 48) |
|---|---|---|
| `.btn` | 42 px | ✗ |
| `.chip` / `.chips.sm .chip` | 38 / 33 px | ✗ |
| `.seg button` / `.tools .seg button` (Lijnen, Zo kleur je) | 31 / 30 px | ✗ |
| `.a4 .x` (weghalen in boekje) | 28 px | ✗ |
| `.linkbtn` "Haal eraf" | ≈ 16 px | ✗✗ |
| `.sw` op mobiel (8 kolommen in 343 px) | ≈ 36 px | ✗ |
| `.chk input` | 18 px (label klikbaar) | ± |

**Overige patronen die in een design system thuishoren**
- **Hover op touch:** `.btn:hover` keert de kleuren om. Op een tablet blijft die stand "plakken" na een tik. Alle hover moet achter `@media (hover: hover)`.
- **Geen iconen.** Voorlezers (kinderen van 2–5) kunnen "Ongedaan maken", "Printen" en "Op de koelkast" niet lezen. Pijlen en kruisjes zijn tekst (`"←"`, `"×"`, `"✓"`).
- **Kleurvakjes in de vrije modus** hebben `aria-label={p.hex}`, dus een schermlezer zegt "hekje e2 48 3d". De namen staan al in `colors.json` ("rood", "oranje" …).
- **Bevestigen door twee keer te tikken binnen 2,5 s** komt drie keer los voor (`Studio.tsx` reset, `Fridge.tsx` takeOff, `AccountPanel.tsx` delete). Dat vraagt om één component, en voor het verwijderen van een account om een echte dialoog.
- **Het accountmenu** (`AccountButton.tsx`) sluit niet met Escape of met een klik erbuiten, en heeft geen focusbeheer.
- **Admin-tabs** gebruiken `role="tablist"`/`role="tab"` op links zonder tabpanelen (`winkel/nav.tsx`, `gebruikers/page.tsx`). Dat is verkeerde ARIA: het moet navigatie met `aria-current` zijn. De periodekeuze (7/30/90 dagen) gebruikt `aria-selected` zonder rol.
- **Het zijmenu in admin heeft geen actieve stand** (`(panel)/layout.tsx`, screenshot 5): je ziet niet waar je bent.
- **Scrollende tabellen** (`.panel { overflow-x: auto }`) zijn niet met het toetsenbord bereikbaar (axe: `scrollable-region-focusable`).
- **De 404** (`[market]/not-found.tsx`) heeft hardcoded Nederlandse tekst buiten `i18n`.
- **Fysieke richtingen** (`left`/`right`/`padding-left`) in `.chip` (en de `inset 6px 0`-schaduw), `.tick`, `.kind-badge`, `.acct-menu`, `.fridge::after` en `.steps`. Bij RTL gaan die mis.
- **Print staat vast op A4** (`@page { size: A4 portrait; margin: 14mm }`, `.a4` met `aspect-ratio: 210/297`). Letter (VS en Canada) kan niet.
- **De stijl van de knutsellijnen staat twee keer**: in de API (voor `<img>` en de CDN) en in `globals.css:228–231` (ADR 0010 noemt dit bewust). Dat is een kandidaat voor één tokenbron.
- **Er is geen skip-link.**

---

## 2. Aanbeveling voor de aanpak

### 2.1 Opties vergeleken

| Criterium | **A. Eigen tokens (CSS custom properties) + plain CSS + headless React Aria Components** | B. shadcn-stijl (Radix + Tailwind, componenten kopiëren) | C. Volledige bibliotheek (MUI / Mantine) | D. Tailwind invoeren (los of met A) |
|---|---|---|---|---|
| Server components | Statische componenten (Button, Badge, Card, Table) zijn gewone server components die een `className` en `data-*` uitgeven. Alleen Menu, Dialog en Toast zijn client. | Goed (Radix alleen client voor interactie) | MUI: emotion-runtime, bijna alles `"use client"`. Mantine 7+: CSS-modules, maar componenten zijn client en vragen een Provider. | Neutraal |
| Bundelgrootte | Minimaal: geen CSS-in-JS, en React Aria alleen voor de paar interactieve componenten (tree-shakebaar) | Klein | Groot, en je betaalt voor wat je niet gebruikt | Klein (CSS), maar de markup wordt groter |
| Toegankelijkheid | **Beste in de klasse:** React Aria normaliseert touch, muis en toetsenbord (`usePress`, belangrijk voor kinderen op tablets), heeft focusbeheer, ingebouwde vertaalde schermlezerteksten, RTL en datum/getal per locale | Goed (Radix), minder op touch, i18n en RTL | Goed, maar je bent aan hun markup gebonden | n.v.t. |
| Thema per site | **Natuurlijk:** een site levert één `theme.css` met waarden. Componenten lezen alleen semantische tokens. | Kan (CSS-variabelen in Tailwind-config), maar elke site heeft dan gekopieerde componenten die uit elkaar groeien | Via de thema-API van de bibliotheek. Een speelse kindstijl is vechten tegen de standaardlook. | Tailwind 4 `@theme` werkt met variabelen, maar je herschrijft alle markup |
| Verkoopbaarheid (ADR 0004) | Eén tarball `ui` plus één site-thema. Een koper ziet gewone CSS. | Elke site een kopie, dus geen updates via het platform | Externe afhankelijkheid met eigen breaking changes | Extra buildketen |
| Klein team (één persoon) | Weinig nieuwe kennis: het is de CSS die er al is, netjes gemaakt. React Aria leer je per component. | Copy-in levert onderhoud per kopie | Snel aan de slag, maar later traag (overrides) | Grote migratie zonder gebruikerswinst |
| Kindvriendelijk en merk | Volledige vrijheid in vorm (papier, labelchip, magneten) | Vrij | Materiaal- of Mantine-gevoel blijft zichtbaar | Vrij |

### 2.2 Keuze: **optie A**
**Eigen tokens als CSS custom properties, één `ui.css` met `@layer`, gewone React-componenten die server-first zijn, en [React Aria Components](https://react-spectrum.adobe.com/react-aria/) alleen voor complexe interactie** (Menu, Dialog/AlertDialog, Popover, Tooltip, Toast, ComboBox, Select, DatePicker, Tabs met panelen, RadioGroup voor het kleurpalet). **Geen Tailwind.**

Waarom:
1. De bestaande code is al 80 % optie A. De migratie is opruimen, geen herbouw.
2. Een thema per site via custom properties is precies wat "meerdere sites op hetzelfde platform met een eigen merk" vraagt, zonder build-stap per site.
3. React Aria geeft de touch-afhandeling die kinderen op tablets nodig hebben, plus RTL en vertaalde schermlezerteksten voor de meertalige toekomst. Zelf bouwen of Radix vraagt daar handwerk.
4. Server components blijven de standaard, en de cache (ISR) en het kleine aantal JS-bundels blijven zoals ze zijn (ADR 0006).

**Alternatief als React Aria tegenvalt:** Base UI (van het MUI- en Radix-team, ook headless). De API's lijken genoeg op elkaar dat de keuze per component omkeerbaar is.

### 2.3 Technische afspraken
- **CSS-architectuur:** `@layer reset, tokens, base, components, patterns, site, utilities;`. Componentklassen krijgen het voorvoegsel `ui-` (bijvoorbeeld `ui-btn`); varianten gaan via `data-variant` en `data-size`; staten via de attributen van React Aria (`[data-pressed]`, `[data-focus-visible]`, `[data-selected]`) of via ARIA (`[aria-pressed="true"]`).
- **Geen CSS-modules in het gedeelde pakket.** Het levert één `ui.css` die de app één keer importeert. Dat is voorspelbaar, werkt met elke bundler, en een koper ziet gewone CSS.
- **Bron van de tokens:** JSON in het W3C-formaat voor design tokens (`*.tokens.json`). Een klein buildscript van ongeveer 80 regels zet dat om naar `tokens.css` (web), `tokens.ts` (later de mobiele app, en voor de SVG-stijl in de API) en `print.css`. Style Dictionary pas als het script te klein wordt.
- **Logische CSS-eigenschappen overal** (`margin-inline-start`, `inset-inline-end`, `border-start-start-radius`), zodat RTL straks gratis is.
- **Iconen:** een `Icon`-primitive die elke SVG accepteert (`currentColor`, `aria-hidden` standaard). Beheer gebruikt Lucide (ISC, tree-shakebaar, werkt als server component). Kleurhoek krijgt een **eigen set van ongeveer 16 kindiconen in de lijnstijl van de platen**: printen, koelkast, ongedaan maken, gum, terug, boekje, verras me, lijnen, nummer, palet, schaar, vouwen, lijm, ouders, sluiten, vinkje. Tot die getekend zijn, Lucide met een lijndikte van 2,5.
- **Lint:** stylelint verbiedt hex, `rgb()` en kleurnamen, losse `z-index` en `font-family` buiten de tokenbestanden. ESLint verbiedt hex-strings in `style={{…}}` en in TSX-constanten (dat vangt `MAGNETS` en `FEEST`).

---

## 3. Lagen en plek in de repos

### 3.1 Vijf lagen

| Laag | Inhoud | Weet van Kleurhoek? |
|---|---|---|
| **L0 Tokenschema** | namen van alle semantische tokens, de modi (kind/ouder/beheer), een neutraal standaardthema, het buildscript | Nee |
| **L1 Primitives** | Button, Field, Checkbox, Badge, Card, Stack, Heading/Text, Icon, VisuallyHidden … | Nee |
| **L2 Patronen** | FilterGroup, DataTable, AdminShell, EmptyState, SponsoredLink, Price, Pagination … | Nee (teksten komen via props) |
| **L3 Merkthema** | waarden van de tokens, logo, fonts, mascottes, kindiconen, plaatstijl (`.cut`, `.fold` …), categoriekleuren | **Ja** |
| **L4 Sitecomponenten** | PlateCard, Studio, Sheet, Fridge, SeasonBand, Booklet, ForParents … | **Ja** |

### 3.2 Waar het staat: eerst incuberen in de Kleurhoek-repo, later naar het platform
Volgens de platform-CLAUDE.md komt code pas naar het platform "als een tweede site hem nodig heeft". Voor een design system is dat ook inhoudelijk de beste regel: wat echt generiek is, weet je pas bij het tweede merk. Daarom:

**Nu, in `t-jarpis/kleurhoek`:**
```
packages/
  ui-core/        → @kleurhoek/ui-core   (L0 + L1 + L2, site-agnostisch)
    tokens/schema.tokens.json   neutraal thema + modi
    src/primitives/…  src/patterns/…  src/admin/…
    ui.css
    guard: geen "kleurhoek"/"Kleurhoek", geen imports uit brand/ of apps/
  brand/          → @kleurhoek/brand     (L3)
    tokens/kleurhoek.tokens.json   (+ dark)
    logo/  fonts.css  mascots/  icons/  plate.css  categories.ts
apps/web/src/components/  (L4, kindcomponenten blijven hier)
apps/admin/               (gebruikt ui-core/admin + brand in modus "beheer")
```
- De guard is dezelfde regel als `platform/guard.config.json`, maar dan op de map `packages/ui-core`. Zo is de latere verhuizing mechanisch: verplaatsen, hernoemen, tarball in `vendor/`.
- `apps/api` haalt de plaatstijl (`.cut`, `.fold`, `.glue`, `.tip`, inkt) uit `@kleurhoek/brand/plate`, zodat de dubbele definitie uit ADR 0010 verdwijnt.

**Zodra er een tweede site komt** (of de eigenaar dat eerder kiest, zie open vragen), naar `t-jarpis/platform`:

| Pakket | Inhoud |
|---|---|
| `@t-jarpis/tokens` | tokenschema, neutraal thema, modi, buildscript, printtokens (A4/Letter) |
| `@t-jarpis/ui` | `ui.css`, primitives, patronen; subpath-exports `@t-jarpis/ui/admin` (AdminShell, DataTable, StatCard, FilterBar, ImportWizard) en `@t-jarpis/ui/shop` (Price, CartLine, CheckoutSteps …) |

`@kleurhoek/brand` en de kindcomponenten gaan **nooit** naar het platform. Een koper van Kleurhoek krijgt de site-repo met `brand` en de tarballs van `tokens` en `ui` in `vendor/` (ADR 0009), dus alles wat nodig is om te bouwen.

**Waarom admin-UI in het platform (later)?** Elke site heeft hetzelfde soort beheer (ADR 0006/0007: rechten, gebruikers, rate limits). De shell en de datatabel zijn niet merkgebonden. Het merk zit alleen in de thema-waarden en het beeldmerk.

### 3.3 Wat een tweede site moet doen
Eén `brand`-pakket met een eigen `*.tokens.json`, een logo en fonts. Optioneel eigen L4-componenten. Geen enkele L1/L2-component kopiëren. Lukt dat niet, dan is het schema niet generiek genoeg, en dan pas je het schema aan, niet de component.

---

## 4. Design tokens

Drie niveaus: **primitief** (merkpalet, alleen in `brand`), **semantisch** (rollen, het contract waar componenten naar kijken) en **component** (alleen waar nodig, bijvoorbeeld `--btn-h`). Componenten gebruiken **nooit** primitieve tokens.

### 4.1 Primitieven Kleurhoek (L3)

**Inkt en papier (neutraal, licht)**

| Token | Waarde | Herkomst / gebruik |
|---|---|---|
| `--kh-papier` | `#ffffff` | `--sheet`, `--surface` |
| `--kh-grijs-50` | `#f6f8f9` | vervangt admin-`--bg #f4f6f8` |
| `--kh-grijs-100` | `#eef2f4` | "tafel", web-`--bg` |
| `--kh-grijs-200` | `#dde3e8` | |
| `--kh-grijs-300` | `#d5dde2` | decoratieve lijn (`--line`) |
| `--kh-grijs-500` | `#7a8591` | **nieuw:** rand voor bedieningselementen (3,76 op wit, 3,33 op tafel) |
| `--kh-grijs-600` | `#5d6672` | gedempte tekst |
| `--kh-grijs-700` | `#4a5260` | `.tip`, secundaire tekst in print |
| `--kh-inkt` | `#1d1b22` | één inkt voor tekst **en** platen (vervangt `#22222b` en `#1f232a`) |

**Nacht (donker):** `--kh-nacht-900 #15181d`, `-800 #1f232a`, `-700 #323842`, `-500 #68737f` (rand, 3,26:1 op 800), `-300 #a3abb6`, `-100 #eef0f3`.

**Krijtkleuren (merk en categorie).** Per kleur drie tinten. **basis** is de vulling, het logo en het blokje (dit is de bestaande waarde). **sterk** is tekstveilig, ≥ 4,5:1 op wit én op de tafel. **zacht** is een tint als achtergrond (basis gemengd met 14 % wit).

| Kleur | basis | sterk (tekst) | zacht | Contrast basis op wit | Inkt op basis |
|---|---|---|---|---|---|
| rood | `#e2483d` | `#d22b1f` (5,11 / 4,54) | `#fbe5e4` | 4,02 | 4,24 |
| oranje | `#ff8a3d` | `#ba4a00` (5,16 / 4,58) | `#ffefe4` | 2,35 | 7,27 |
| amber | `#f2a516` | `#956308` (5,16 / 4,58) | `#fdf2de` | 2,07 | 8,25 |
| geel | `#f2c618` | `#836a07` (5,21 / 4,63) | `#fdf7df` | 1,63 | 10,44 |
| groen | `#2fa45a` | `#247c44` (5,20 / 4,61) | `#e2f2e8` | 3,19 | 5,34 |
| blauw | `#2f5bd3` | `#2f5bd3` (5,90 / 5,24) | `#e2e8f9` | 5,90 | 2,89 |
| lucht | `#1d8fce` | `#1773a6` (5,20 / 4,62) | `#dfeff8` | 3,58 | 4,77 |
| teal | `#13a3a0` | `#0e7a78` (5,16 / 4,58) | `#def2f2` | 3,10 | 5,50 |
| paars | `#9b4fd0` | `#9647ce` (5,14 / 4,56) | `#f1e6f8` | 4,75 | 3,59 |
| roze | `#d0479b` | `#c2328a` (5,10 / 4,53) | `#f8e5f1` | 4,15 | 4,10 |

Keuzes:
- **Eén paars:** `#9b4fd0` uit het logo. Ruimte (`#5b4fc9`) wordt paars. Dat onderscheidt ook beter van Voertuigen (blauw).
- **Tekst op zacht:** altijd inkt, niet sterk (sterk op zacht komt maar op 4,2–4,8).
- **Op basis:** gebruik inkt als tekst voor oranje, amber, geel, groen, teal en lucht. Gebruik wit alleen op blauw (5,90).
- De **krijtdoos van de studio** (`FREE_PALETTE`, `colors.json`) is inhoud, geen UI. Ze blijft levendig en wordt gegenereerd uit `colors.json` als `--kh-krijt-<code>`, met de kleurnaam als toegankelijke naam.

**Categorie naar token, niet naar hex.** `categories.json` en de DB-kolom `color` krijgen een sleutel (`"rood"`, `"blauw"`, `"teal"` …) in plaats van een hex. Het thema bepaalt de hex. Dat gaat via een kleine migratie in de API plus een fallback die een hex blijft accepteren. Huidige toewijzing: dieren=rood, voertuigen=blauw, natuur=groen, eten=amber, ruimte=paars, feest=teal, wereld=lucht, patronen=roze.

### 4.2 Semantische kleuren (L0-contract, waarden van Kleurhoek)

| Token | Licht | Donker | Gebruik |
|---|---|---|---|
| `--color-bg` | `#eef2f4` | `#15181d` | pagina (tafel) |
| `--color-bg-subtle` | `#f6f8f9` | `#15181d` | achtergrond van beheer |
| `--color-surface` | `#ffffff` | `#1f232a` | panelen, kaarten |
| `--color-surface-sunken` | `#eef2f4` | `#15181d` | regels in "Wat heb je nodig" |
| `--color-paper` | `#ffffff` | `#ffffff` | platen, A4, magneten (**altijd wit**) |
| `--color-text` | `#1d1b22` | `#eef0f3` | |
| `--color-text-muted` | `#5d6672` | `#a3abb6` | |
| `--color-text-on-accent` | `#ffffff` | `#0f1320` | **ook in admin** (lost 2,61 op) |
| `--color-border` | `#d5dde2` | `#323842` | **alleen** scheidingslijnen en kaartranden |
| `--color-border-control` | `#7a8591` | `#68737f` | randen van invoer, chips, seg, checkbox (≥ 3:1) |
| `--color-border-strong` | `#1d1b22` | `#eef0f3` | omlijnde knop, open menu |
| `--color-accent` | `#2f5bd3` | `#7c9cff` | primaire actie, link, selectie |
| `--color-accent-hover` | `#2546b0` | `#9db4ff` | |
| `--color-accent-soft` | `#e2e8f9` | `#222b45` | geselecteerde rij, info-callout |
| `--color-focus` | `#2f5bd3` | `#9db4ff` | focusring (5,90 / 8,82) |
| `--color-success` | `#247c44` | `#5fd08a` | tekst en icoon |
| `--color-success-soft` | `#e2f2e8` | `#1d3326` | |
| `--color-on-success` | `#ffffff` (5,20) | `#0f1320` | toast |
| `--color-danger` | `#c0352b` (5,55 op wit, 4,92 op tafel) | `#f0675c` (5,10) | |
| `--color-danger-soft` | `#fbe9e7` | `#3a2020` | |
| `--color-warning` | `#8a5300` (6,33) | `#f2a516` | |
| `--color-warning-soft` | `#fdf2de` | `#2f2615` | |
| `--color-info` | = accent | = accent | |
| `--color-sponsored-fg` | `#8a4b00` | `#e8b061` | label "Partnerlink" |
| `--color-sponsored-bg` | `#fff4dd` (6,23:1 met fg) | `#2b2418` (7,90:1) | |
| `--color-sponsored-border` | `#e9c98f` | `#5a4526` | |
| `--color-celebrate` | `#f2c618` (geel) | idem | feestmoment, confetti (kind) |
| `--color-cat-*` | basis-krijtkleur | basis | blokje en markering (niet-tekst) |
| `--color-overlay` | `rgb(20 30 50 / .45)` | `rgb(0 0 0 / .6)` | achter een dialoog |

**De partnermarkering bewust níet blauw.** Blauw is "doe dit". Zandkleur zegt "let op, dit is commercieel". De markering is altijd tekst plus kleur, nooit alleen kleur.

### 4.3 Contrastcontrole voorgestelde paren (berekend)

| Voorgrond / achtergrond | Ratio | Niveau |
|---|---|---|
| tekst `#1d1b22` / tafel `#eef2f4` | 15,1 | AAA |
| tekst `#1d1b22` / wit | 17,0 | AAA |
| muted `#5d6672` / tafel · / wit | 5,17 · 5,82 | AA |
| accent `#2f5bd3` / wit · / tafel | 5,90 · 5,24 | AA |
| wit / accent (primaire knop) | 5,90 | AA |
| accent-hover `#2546b0` met wit | 8,13 | AAA |
| danger `#c0352b` / wit · / tafel | 5,55 · 4,92 | AA |
| success `#247c44` / wit · wit op success | 5,20 · 5,20 | AA |
| warning `#8a5300` / wit | 6,33 | AA |
| sponsored fg / bg (licht · donker) | 6,23 · 7,90 | AA |
| border-control `#7a8591` / wit · / tafel | 3,76 · 3,33 | 1.4.11 ✓ |
| donker: tekst `#eef0f3` / `#15181d` | 15,6 | AAA |
| donker: muted `#a3abb6` / `#1f232a` | 6,80 | AA |
| donker: accent `#7c9cff` / `#15181d` · accent-ink op accent | 6,83 · 7,10 | AA |
| donker: focus `#9db4ff` / `#15181d` | 8,82 | ✓ |
| donker: border-control `#68737f` / `#1f232a` | 3,26 | 1.4.11 ✓ |
| inkt op geel / amber / teal (labels op kleur) | 9,66 / 7,64 / 5,09 | AA |
| print `.tip #4a5260` / wit | 7,87 | AAA |
| print `.trace #8a9099` (overtrekwoord, bewust licht) | 3,22 | decoratief, uitgezonderd |

### 4.4 Typografie

**Families**
- `--font-display: "Sniglet", "Nunito", system-ui, sans-serif`. Alleen koppen en het logo. Gewicht 400 voor koppen, 800 alleen voor het logo en de naam op een plaat.
- `--font-body: "Nunito", system-ui, -apple-system, "Segoe UI", sans-serif`. Gewichten 400, 600 en 800.
- `--font-mono: ui-monospace, SFMono-Regular, Menlo, monospace`. Alleen in beheer.
- **Per schrift:** Sniglet heeft alleen Latijn. Dus `:lang(ru, uk, bg)` gebruikt Nunito 800 voor koppen; `:lang(ar)` wordt "Baloo Bhaijaan 2", `:lang(he)` "Varela Round". Beide zijn OFL, rond en zelf te hosten. Kies pas bij de eerste markt in dat schrift.
- **Leerblad (open vraag):** voor het overtrekwoord kan een schoolletter met een enkele "a" en "g" (zoals Andika, OFL) beter zijn dan Sniglet.

**Schaal** (rem bij 16 px; niets onder 13 px op scherm)

| Token | Waarde | Voorbeeld |
|---|---|---|
| `--text-2xs` | 0,8125rem (13) | bovenlabel, tabelkop, voetnoot |
| `--text-xs` | 0,875rem (14) | hint, badge |
| `--text-sm` | 0,9375rem (15) | lopende tekst in beheer, knop in beheer |
| `--text-md` | 1rem (16) | lopende tekst |
| `--text-lg` | 1,125rem (18) | knoppen in kindmodus, h3 |
| `--text-xl` | 1,25rem (20) | kaarttitel (Sniglet), toast |
| `--text-2xl` | 1,5rem (24) | |
| `--text-3xl` | clamp(1,5rem, 4vw, 1,9rem) | sectiekop (`.sec`, `.parents-head h2`) |
| `--text-4xl` | clamp(1,8rem, 5vw, 2,4rem) | paginatitel |
| `--text-display` | clamp(2,2rem, 7vw, 3,6rem) | logo (als het SVG niet beschikbaar is) |

- **Regelhoogte:** `--leading-tight 1.1` (display), `--leading-snug 1.3`, `--leading-body 1.5`, `--leading-relaxed 1.6` (lange oudertekst).
- **Letterafstand:** `--tracking-display -0.01em`, `--tracking-label 0.1em` (alleen Latijn; `:lang(ar,he,zh,ja)` krijgt 0 en geen hoofdletters).
- **Cijfers:** `--numeric: tabular-nums` in tabellen, prijzen en statistieken.

**Tekststijlen (samengesteld):** `display`, `title` (h1), `section` (h2, Sniglet), `subhead` (h3, Nunito 800 lg), `body`, `body-sm`, `label` (Nunito 800 sm), `eyebrow` (2xs, 800, label-tracking, hoofdletters), `caption` (xs muted), `numeric-lg` (stat 28 px/800). Dat zijn 10 stijlen in plaats van de huidige 18+ losse combinaties.

### 4.5 Spacing (basis 4 px)
`--space-0: 0` · `--space-px: 2px` · `--space-1: 4px` · `--space-2: 8px` · `--space-3: 12px` · `--space-4: 16px` · `--space-5: 20px` · `--space-6: 24px` · `--space-8: 32px` · `--space-10: 40px` · `--space-12: 48px` · `--space-16: 64px` · `--space-24: 96px`.
Afronden van wat er nu staat: 6 wordt 4 of 8, 10 wordt 8 of 12, 14 wordt 12 of 16, 18 wordt 16 of 20, 22 wordt 24, 28 wordt 24 of 32.

### 4.6 Radii, randen en schaduwen

| Token | Waarde | Gebruik |
|---|---|---|
| `--radius-xs` | 2px | foto op de magneet |
| `--radius-paper` | 4px | papier, A4 |
| `--radius-sm` | 8px | kleurvakje, menu-item, bediening in beheer |
| `--radius-md` | 12px | invoerveld, paneel in beheer, callout |
| `--radius-lg` | 16px | paneel en seizoensband op het web (nu 14) |
| `--radius-xl` | 20px | koelkast |
| `--radius-pill` | 999px | knoppen (kind/ouder), seg, badge |
| `--radius-tag-start` / `-end` | 6px / 999px | labelchip, via `border-start-start-radius` enz. (dus RTL-veilig) |
| `--border-thin` | 1px | beheer |
| `--border-thick` | 2px | kind/ouder |
| `--focus-width` / `--focus-offset` | 3px / 2px | |

Schaduwen (koel, "papier op tafel"):
- `--shadow-paper-sm: 0 1px 0 var(--color-border), 0 6px 16px -10px rgb(20 30 50 / .45)` (kaart)
- `--shadow-paper-md: 0 8px 20px -14px rgb(20 30 50 / .6)` (A4)
- `--shadow-paper-lg: 0 10px 30px -18px rgb(20 30 50 / .6)` (canvas)
- `--shadow-overlay: 0 10px 24px -14px rgb(20 30 50 / .6)` (menu, popover)
- `--shadow-raised: 0 12px 30px -12px rgb(0 0 0 / .5)` (toast, dialoog)
- `--shadow-bar: 0 -10px 24px -18px rgb(20 30 50 / .5)` (PickBar, straks winkelwagenbalk)
- `--shadow-magnet: 0 2px 3px rgb(0 0 0 / .3)`
- In donker zijn schaduwen nauwelijks te zien. Daar telt `--color-border` voor de afbakening.

### 4.7 Beweging
`--dur-instant: 80ms` · `--dur-fast: 150ms` (nu `.15s`) · `--dur-base: 250ms` · `--dur-slow: 400ms`
`--ease-out: cubic-bezier(.2, .8, .2, 1)` · `--ease-playful: cubic-bezier(.34, 1.56, .64, 1)` (alleen in kindmodus: feest, magneet)
`--tilt-hover: -1.5deg` · `--lift-hover: -3px`
Bij `prefers-reduced-motion: reduce` worden alle duur-tokens 0 ms, en `--tilt-hover` en `--lift-hover` 0. Eén regel op token-niveau, in plaats van per component zoals nu (`globals.css:130, 179`).

### 4.8 Breakpoints en containers
`--bp-sm: 560px` (telefoon) · `--bp-md: 760px` (tablet staand, nu de hoofdgrens) · `--bp-lg: 1024px` (tablet liggend, laptop) · `--bp-xl: 1280px`.
Custom properties werken niet in media queries. Daarom: `@custom-media --md (width >= 760px)` via `postcss-custom-media`, wat Next al met PostCSS doet. Componenten zoals PlateCard, MaterialItem en DataTable gebruiken **container queries**, zodat ze in de studio-zijbalk en in het hoofdraster goed werken.
Containers: `--container-max: 1100px` · `--container-narrow: 640px` · `--measure: 70ch` · `--sidebar-admin: 220px` · `--tools-width: 280px`.

### 4.9 Z-index
`--z-base: 0` · `--z-raised: 1` (badge, vinkje) · `--z-sticky: 10` (gereedschap in het boekje) · `--z-dropdown: 20` (accountmenu, nu 10) · `--z-actionbar: 30` (PickBar, nu 15) · `--z-toast: 40` · `--z-overlay: 50` · `--z-modal: 60` · `--z-skiplink: 70`.

### 4.10 Modi: kind / ouder / beheer
Ingesteld met `data-mode` op een container. Ze kunnen in elkaar zitten: de pagina is `kind`, het blok "Voor ouders" is `ouder`, admin is overal `beheer`.

| Token | kind | ouder | beheer |
|---|---|---|---|
| `--control-h` | 48px | 44px | 32px |
| `--control-px` | 20px | 16px | 12px |
| `--control-font` | `--text-lg` | `--text-md` | `--text-sm` |
| `--tap-min` | 48px | 44px | 24px |
| `--tap-gap` | 12px | 8px | 4px |
| `--control-border` | 2px | 2px | 1px |
| `--control-radius` | pill | pill | `--radius-sm` |
| `--text-body` | 16px | 17px | 15px |
| `--stack-gap` | `--space-6` | `--space-4` | `--space-3` |
| `--swatch-size` | 56px | 44px | 28px |
| `--heading-font` | display | display (alleen h1/h2) | body |
| `--icon-with-label` | verplicht | aanbevolen | optioneel |
| `--motion` | speels toegestaan | alleen fast/out | alleen fast/out |

Extra regels voor kindmodus:
- Geen informatie die alleen bij hover verschijnt.
- Geen lang indrukken of dubbel tikken als enige weg.
- Bij omkeerbare acties **liever ongedaan maken dan bevestigen**. "Opnieuw" in de studio kan een toast met "Terugzetten" worden in plaats van "Zeker? Tik nog eens".

### 4.11 Donkere modus: standpunt
- **Behouden, automatisch** (`prefers-color-scheme`), voor site en beheer. Voorlopig geen schakelaar (open vraag). Wel `[data-theme="light"|"dark"]` in het schema, zodat een schakelaar later alleen UI is.
- **Papier blijft altijd wit**: platen, A4, koelkastmagneten. Het kind kleurt op wit, ook 's avonds. De tafel eromheen wordt donker.
- **Het logo in donker** gebruikt de lichtere blauw- en paarsvariant (blauw `#2f5bd3` haalt maar 3,01 op `#15181d`).
- **Print is altijd licht** (`@media print` reset naar het lichte thema).
- **Admin donker** krijgt dezelfde tokens. De fout met `color: #fff` op `#7c9cff` (2,61) verdwijnt doordat `--color-text-on-accent` wordt gebruikt.

### 4.12 Printtokens
De papiermaat per markt kan niet met custom properties in `@page`. Daarom **benoemde pagina's**: `@page a4 { size: A4; margin: 14mm }` en `@page letter { size: letter; margin: 12.7mm }`, en `html[data-paper="letter"] .print-sheet { page: letter }`. Dat werkt in Chrome, Firefox en recente Safari. De markt bepaalt `data-paper` (US/CA wordt Letter).

| Token | A4 | Letter |
|---|---|---|
| `--print-margin` | 14mm | 12.7mm |
| `--print-sheet-h` | 268mm | 253mm |
| `--print-content-w` | 170mm | 170mm |
| `--print-plate-max-h` | 225mm | 205mm |
| `--print-cover-max-h` | 240mm | 220mm |
| `--print-title` | 22pt | 22pt |
| `--print-foot` | 10pt, `#444` | idem |
| `--print-ink` | `#000` (één toner, scherper dan `#1d1b22`) | idem |

Plaattokens, gedeeld met de API via `tokens.ts`:
- `--plate-ink`
- `--plate-stroke-2-4: 3.4` · `-4-6: 2.8` · `-6-9: 2.4` · `-9plus: …` (uit `ages.json`)
- `--plate-cut: 1 / "4 3"`
- `--plate-fold: .8 / "1 2.5"`
- `--plate-glue-fill: #d5d9de` · `--plate-glue-stroke: #9aa1a9`
- `--plate-tip: 6px #4a5260`
- `--plate-trace: #8a9099` · `--plate-guide: #c3c9cf`

Overige printregels:
- `print-color-adjust: exact` alleen op `.print-sheet` (nu staat het op `*`).
- Er komt een printvoorbeeld in de werkbank voor A4 en Letter.

---

## 5. Componenteninventaris

Legenda **laag:** P = platform-geschikt (nu `ui-core`, later `@t-jarpis/ui`); S = site (`@kleurhoek/brand` of `apps/web`). **Status:** bestaat (alleen tokens aansluiten) / aanpassen / nieuw.

### 5.1 Website (huidig)

| Nu (bestand, klasse) | DS-component | Laag | Status | Varianten | Toegankelijkheidseisen |
|---|---|---|---|---|---|
| `Logo.tsx`, `.logo` | **Logo** | S | aanpassen (SVG) | kleur, kleur-donker, mono, wit, beeldmerk | link naar markt-home; naam "Kleurhoek"; letters `aria-hidden` |
| `page.tsx` `.mast` | **SiteHeader** | S (op P-`Cluster`) | aanpassen | home, subpagina (met terug) | `<header>`; skip-link ervoor |
| — | **SkipLink** | P | nieuw | — | eerste focusbare element; zichtbaar bij focus |
| `.lede`, `.hint`, `.muted`, `.soon` | **Text** | P | aanpassen | body, body-sm, caption, muted | — |
| `.eyebrow`, `.flabel`, `.tools h2`, admin `th` | **Eyebrow** | P | aanpassen | — | geen hoofdletters in niet-Latijnse talen; min 13 px |
| `.page-title`, `.sec`, `.studio-top h1`, `.season-txt h2`, `.parents-head h2` | **Heading** | P | aanpassen | level 1–4 × style title/section/subhead | semantisch niveau los van stijl |
| `.btn`, `.btn.primary`, `.btn.danger`, `:disabled` | **Button** | P | aanpassen | primary, secondary (omlijnd), danger, quiet, link; sizes volgen de modus; icoon start/eind/alleen; loading | ≥ `--tap-min`; focusring; hover alleen `(hover:hover)`; disabled met uitleg (`aria-describedby`); alleen-icoon vraagt een `aria-label` |
| `a.btn` (Link) | **ButtonLink** | P | aanpassen | als Button | echte `<a>`; geen `role=button` |
| `BookButton` (`aria-pressed`) | **ToggleButton** | P | aanpassen | als Button + pressed | `aria-pressed`; staat ook visueel zonder kleur |
| `.linkbtn` | Button `variant="link"` | P | aanpassen | — | ≥ 24 px doel (beheer), 44 (ouder) |
| `.row` | **Cluster** / **Stack** | P | nieuw | gap uit tokens, wrap, justify | — |
| `.chip` (+`--c`, count) | **FilterChip** | P (kleur via prop/token) | aanpassen | md, sm; met kleurblok, met teller | `aria-pressed`; rand ≥ 3:1; geselecteerd niet alleen via kleur (vinkje of dikke rand); teller in de toegankelijke naam ("Dieren, 5 platen") |
| `.chips`, `.frow`, `.flabel` | **FilterGroup** | P | nieuw | rij met label, inklapbaar op mobiel | `role="group"` + `aria-labelledby` (niet `<nav>` om knoppen) |
| `.seg` | **SegmentedControl** | P (React Aria `ToggleButtonGroup`, enkele keuze) | aanpassen | md, sm; met icoon/stipjes | pijltjestoetsen; ≥ `--tap-min` per segment (nu 30 px) |
| `.lv` | **LevelDots** (leeftijd) | S | bestaat | 1–4 | `aria-hidden`, tekst ernaast |
| `SeasonBand`, `.season` | **SeasonBand** | S | aanpassen | met/zonder minis | `<section aria-label>` |
| `.tear` | **TearCalendar** | S | aanpassen (tokens) | groot, compact (mobiel) | `aria-hidden` (datum staat in tekst) of als `<time>` |
| `.minis` | **ScrollRow** | P | nieuw | met/zonder pijlknoppen | regio focusbaar (`tabindex=0`, label); pijlen ≥ 44 px; scroll-snap |
| `PlateCard`, `.card`, `.paper` | **PlateCard** | S (op P-`Card`) | aanpassen | link, kiesbaar (boekje), mini | hele kaart één doel; titel = naam; afbeelding `alt=""`; kiesbaar: `aria-pressed` + zichtbaar vinkje |
| `.kind-badge`, `.yr` | **Badge** | P | aanpassen | neutral, accent, success, warning, danger, sponsored, category | tekst ≥ 4,5:1; nooit alleen kleur |
| `.tick` | **SelectionMark** (deel van PlateCard) | S | aanpassen | — | `aria-hidden` (staat zit in `aria-pressed`) |
| `.grid` | **Grid** (auto-fill) | P | nieuw | min-breedte via prop | — |
| `.empty`, `not-found.tsx` | **EmptyState** | P (+ S-illustratieslot met Sjors/Oki) | aanpassen | leeg filter, 404, fout | kop + uitleg + één actie; teksten via i18n |
| `.note` (web voetnoot) | **FooterNote** | S | aanpassen | — | — |
| `Sheet.tsx`, `.sheet` | **PlateSheet** | S | bestaat (tokens) | studio, magneet, A4 | `role="img"` + naam; vlakken klikbaar met muis/touch; toetsenbordkleuren via "volgend vlak" (open vraag) |
| `Studio.tsx`, `.studio`, `.canvas`, `.tools`, `.tool` | **StudioLayout**, **ToolPanel**, **ToolSection** | S | aanpassen | desktop zijbalk, mobiel onder | gereedschap als `<aside>` met kopjes |
| `.pal`, `.sw`, `.sw.eraser` | **SwatchPicker** | S (op React Aria `RadioGroup`) | aanpassen | vrij, op nummer (met cijfer), gum | **focusring (nu weg)**; naam = kleurnaam uit `colors.json`; ≥ `--swatch-size`; geselecteerd met dubbele ring |
| `.prog`, `.bar` | **ProgressBar** | P | aanpassen | success, accent | `role="progressbar"` + waarden, of `aria-hidden` als de tekst ernaast staat |
| `.input` | **TextField** | P | aanpassen | met label, beschrijving, fout, teller (maxLength) | label gekoppeld; rand ≥ 3:1; foutmelding `aria-describedby` |
| `.chk` | **Checkbox** | P | aanpassen | md, kind (24 px vak) | hele label klikbaar; vak ≥ 24 px in kindmodus |
| `.toast` | **Toast** | P (React Aria) + S-variant **Celebration** (Oki, confetti) | aanpassen | success, info, error, met actie ("Terugzetten") | `role="status"`; niet onder 5 s als er een actie in zit; pauze bij hover/focus |
| `t.back` "← Alle platen" | **BackLink** | P | nieuw | — | icoon spiegelt in RTL; tekst zonder pijl |
| `.panel` | **Card / Panel** | P | aanpassen | surface, sunken, outlined | — |
| `.facts` (`<dl>`) | **DescriptionList** | P | aanpassen | rijen, kolommen | `<dl>` behouden |
| reset/`takeOff`/`deleteAccount` "tik nog eens" | **ConfirmButton** (licht) en **AlertDialog** (zwaar) | P | nieuw | — | ConfirmButton: staat aangekondigd via `aria-live`, geen tijdslimiet onder 5 s; AlertDialog: focus naar "Annuleren", Escape sluit |
| `AccountButton`, `.acct-menu` | **Menu** (React Aria) | P | aanpassen | — | Escape, buitenklik, pijltjes, focus terug naar de knop |
| `Fridge`, `.fridge`, `.magw`, `.mag` | **Fridge**, **Magnet** | S | aanpassen (tokens; `MAGNETS` naar krijtkleur-tokens) | — | magneet = knop met naam; "Haal eraf" ≥ 44 px |
| `PickBar`, `.pickbar` | **ActionBar** (onderbalk) | P | aanpassen | — | `role="region"` + label; `aria-live` voor het aantal; ruimte onderaan de pagina |
| `Booklet`, `.book`, `.sheets` | **BookletBuilder** | S | aanpassen | — | — |
| `.a4`, `.pg`, `.foot` | **PrintSheet** | S (op P-printtokens) | aanpassen | A4, Letter; cover | — |
| `.a4 .x` | **IconButton** | P | nieuw | quiet, danger | ≥ 44 px (nu 28); `aria-label` |
| `Cover` | **BookCover** | S | bestaat | — | `role="img"` + label |
| `ForParents`, `.parents`, `.parents-head` | **ParentsSection** | S | aanpassen | knutsel, kleurplaat | `<section aria-labelledby>`; `data-mode="ouder"`; herkenbaar label met icoon |
| `.facts-line` | **MetaLine** | P | nieuw | — | scheidingstekens `aria-hidden` |
| `.steps` | **StepList** | P | aanpassen | genummerd, met afbeelding (later) | `<ol>` |
| `.needs`, `li` | **MaterialList**, **MaterialItem** | S | aanpassen | met/zonder product, optioneel | — |
| `.offer` | **SponsoredLink** | P | aanpassen | inline, als kaart | label "Partnerlink" zichtbaar **bij de link** (niet alleen onderaan); `rel="sponsored nofollow noopener"`; nieuw venster aangekondigd |
| `.disclosure` | **SponsoredDisclosure** | P | aanpassen | — | in de buurt van de links; geen kleine lettertjes onder 13 px |
| `SeenTracker`, `Track` | (geen UI) | S | — | — | — |
| `.no-print` | utility `[data-print="hide"]` en `PrintOnly` | P | aanpassen | — | — |
| — (knippen/vouwen/lijmen in de SVG) | **CraftLegend** | S | nieuw als HTML-component (ook buiten de plaat) | — | tekst + lijnvoorbeeld; niet alleen kleur of patroon |

### 5.2 Admin (huidig)

| Nu | DS-component | Laag | Status | Varianten | Toegankelijkheidseisen |
|---|---|---|---|---|---|
| `(panel)/layout.tsx` `.shell` | **AdminShell** | P/admin | aanpassen | met/zonder zijbalk | landmarks `nav` + `main`; skip-link |
| `nav.side a` | **SideNav** | P/admin | aanpassen | met iconen, met teller | **actieve stand** + `aria-current="page"` (nu niet aanwezig) |
| `nav.side .who`, `LogoutButton` | **UserBox** | P/admin | aanpassen | lokaal, ingelogd | — |
| `h1` + `.lead` | **PageHeader** | P | nieuw | met acties, met tabs | één h1 |
| `.panel` | **Card / Panel** | P | aanpassen | — | — |
| `.cards .stat` | **StatCard** | P/admin | aanpassen | met trend (+/−), met toestand (danger) | trend niet alleen via kleur (pijl + tekst) |
| `table`, `td.num`, `td.rule` | **DataTable** | P/admin | aanpassen | compact, met subregel, sorteerbaar, met selectie (later) | `<caption>` of `aria-labelledby`; scrollcontainer focusbaar met label; sorteerstand via `aria-sort` |
| `.pill.on/.off` | **StatusBadge** | P | aanpassen | success, neutral, danger, warning | tekst ≥ 4,5:1 (nu 3,7) |
| `.bad` | Text `tone="danger"` | P | aanpassen | — | — |
| globale `button`, `.ghost`, `a.button` | **Button** / **ButtonLink** | P | aanpassen | als web, in beheergrootte | **geen element-selector meer** |
| `.err` | **Callout** `tone="danger"` / **ErrorState** | P | aanpassen | info, success, warning, danger | `role="alert"` alleen bij nieuwe fouten |
| `.note` (melding) | **Callout** + **Toast** voor `?melding=` | P | aanpassen | — | `role="status"` |
| `.toolbar`, `.row-between` | **Toolbar** / **Cluster** | P | aanpassen | — | — |
| `.tabs` (ShopNav, Gebruikers) | **NavTabs** | P | aanpassen | — | `<nav>` met links + `aria-current` (**geen** `tablist`) |
| `.tabs` periode 7/30/90 | **SegmentedControl** (als links) | P | aanpassen | — | `aria-current` of radio-semantiek |
| `input[type=search]` + knop | **SearchField** | P (React Aria) | aanpassen | — | label (nu alleen `aria-label`); wissen met Escape |
| `input[type=number]` | **NumberField** | P (React Aria) | aanpassen | met eenheid ("s") | eenheid in de toegankelijke naam |
| `.field`, `select`, `.mono`, `:read-only` | **TextField**, **Select**, **Fieldset** | P | aanpassen | mono, read-only, met beschrijving, met fout | servervalidatie per veld terugtonen (`aria-invalid`) |
| `.check`, `.checks`, `form.roles` | **Checkbox**, **CheckboxGroup** | P | aanpassen | horizontaal, verticaal | groep met `legend` |
| `.grid-form`, `.wide` | **FormGrid** | P | aanpassen | 1–3 kolommen | volgorde in DOM = leesvolgorde |
| `form.inline` | **InlineForm** | P/admin | aanpassen | — | elke invoer een label |
| `.pager` | **Pagination** | P | aanpassen | — | `nav aria-label`; huidige pagina `aria-current` |
| `.center` (uitgelogd) | **CenteredLayout** | P | aanpassen | — | — |
| "Nog geen rol" | **EmptyState** `tone="warning"` | P | aanpassen | — | — |
| `title=` op rollen | **Tooltip** (of uitklaptekst) | P (React Aria) | nieuw | — | geen info alleen in `title` |
| "Markten" als vrije tekst "nl-NL, nl-BE" | **MultiSelect / TagField** | P | nieuw | — | combobox-semantiek |

### 5.3 Nodig voor geplande functies

| Functie | Component | Laag | Status | Kern van de toegankelijkheidseisen |
|---|---|---|---|---|
| Productfeed importeren | **FileDropzone** | P | nieuw | ook een knop "Kies bestand"; voortgang aangekondigd |
| | **ImportWizard / Stepper** | P/admin | nieuw | huidige stap `aria-current="step"` |
| | **DiffTable** (nieuw / gewijzigd / verdwenen) | P/admin | nieuw | status als tekst + icoon, niet alleen kleur |
| | **ComboBox** (product zoeken in de feed) | P (React Aria) | nieuw | volledige combobox-ARIA |
| | **JobStatus** (draaiende import) | P/admin | nieuw | `aria-live="polite"` |
| Partnerrapportages | **DateRangePicker** | P (React Aria) | nieuw | locale-kalender; typen mag ook |
| | **Chart** (lijn/staaf) + charttokens | P/admin | nieuw | tabel als alternatief; patronen naast kleur |
| | **MoneyAmount / Price** | P | nieuw | `Intl.NumberFormat` per markt; btw-label |
| Meer knutselsoorten | **CraftLegend**, **DifficultyMeter**, **MaterialChecklist** (afvinken), **StepList** met afbeelding | S | nieuw | afvinken = checkbox |
| | **PaperSizeSwitch** (A4/Letter) | P | nieuw | seg-semantiek |
| Eigen webshop | **ProductCard** (alleen ouderzone) | P/shop | nieuw | prijs leesbaar als één zin |
| | **QuantityStepper** | P/shop (React Aria NumberField) | nieuw | ≥ 44 px knoppen |
| | **CartDrawer**, **CartLine**, **CartSummary** | P/shop | nieuw | drawer = dialoog met focusval |
| | **CheckoutSteps**, **AddressForm** (adresformaat per land), **PaymentMethodPicker** (iDEAL/Wero, kaart) | P/shop | nieuw | `autocomplete`-attributen; fouten bovenaan samengevat |
| | **OrderStatusTimeline** | P/shop | nieuw | lijst met huidige stap |
| | **KitCard** (co-branded pakket) met **PartnerLockup** | S | nieuw | partnerlogo met alt; regels voor het lock-up in de merkgids |
| | **ParentGate** ("Voor ouders": kleine som of vasthouden) | P | nieuw | **verplicht** voor kassa en partnerlinks in de app; niet alleen op motoriek gebaseerd (alternatief voor toetsenbord en schermlezer) |
| | **LegalFooter** (KvK, voorwaarden, retour) | S | nieuw | — |
| Betaalde functies | **PlanCard**, **PlusBadge** / **LockedOverlay** op platen | P + S | nieuw | slot niet alleen als icoon; geen verkoop richting kinderen (overlay alleen ouderzone) |
| | **Dialog** | P (React Aria) | nieuw | focusval, Escape, titel |
| Meer markten | **MarketSwitcher** (land + taal) | P | nieuw | `lang` per optie |
| | RTL-ondersteuning in alle P-componenten | P | aanpassen | logische eigenschappen; iconen spiegelen waar nodig |
| Mobiele app later | `tokens.ts` export (kleur, spacing, type) | P | nieuw | — |
| Meerdere sites | **BrandSlot** (logo, beeldmerk in AdminShell en SiteHeader) | P | nieuw | — |
| Algemeen | **Skeleton** (laden), **Spinner** (alleen beheer), **Divider**, **VisuallyHidden**, **Icon** | P | nieuw | Skeleton `aria-busy` op de container |

---

## 6. Spelregels en governance

### 6.1 Hoofdregel: **eerst in het design system, dan in de feature**
Elke nieuwe of gewijzigde component, inclusief elke nieuwe variant of staat, gaat in deze volgorde:
1. **Spec**: `docs/design-system/componenten/<naam>.md`, maximaal één pagina, met: doel, anatomie, varianten, staten, gebruikte tokens, modus-gedrag (kind/ouder/beheer), toegankelijkheid, tekstregels (toon) en een do/don't.
2. **Tokens**: nieuwe tokens eerst in `*.tokens.json`. Geen nieuwe hex of losse maat in een component.
3. **Werkbank**: een pagina met alle varianten × staten.
4. **Pas dan** gebruiken in de feature.

Deze regel komt in de CLAUDE.md van beide repos, zodat ook agents hem volgen. Daarbij een PR-sjabloon met de checklist uit 6.2. Lint (stylelint, ESLint, guard) dwingt het technische deel af.

### 6.2 Definition of done (per component)
- [ ] Spec staat in `docs/design-system/componenten/`.
- [ ] Gebruikt alleen semantische tokens; stylelint groen (geen hex, geen losse `z-index` of `font-family`).
- [ ] Staten aanwezig: standaard, hover (alleen `(hover:hover)`), focus-visible, actief/ingedrukt, geselecteerd, uitgeschakeld (met uitleg), laden, fout, leeg.
- [ ] Werkt in de drie modi (of de spec zegt waarom niet), licht en donker, LTR en RTL, en print (verbergen of printstijl).
- [ ] Doelgrootte ≥ `--tap-min` van de modus; contrast tekst ≥ 4,5:1 en UI ≥ 3:1 (de werkbank toont de berekende ratio).
- [ ] Volledig met het toetsenbord te bedienen; schermlezernaam gecontroleerd (VoiceOver op iPad voor kindcomponenten).
- [ ] Server component tenzij interactie nodig is; `"use client"` zo diep mogelijk.
- [ ] Teksten via i18n-props; geen Nederlands in P-componenten; geen tekens als "←" in teksten.
- [ ] axe zonder fouten op de werkbankpagina; visuele baseline vastgelegd.
- [ ] P-component: geen import uit `brand` of `apps`, geen "Kleurhoek" (guard groen).
- [ ] Changelog-regel (vanaf de verhuizing naar het platform: een changeset).

### 6.3 Documentatie: **werkbank-pagina's in de app, geen Storybook**
- **Aanbeveling:** een dev-only route `apps/web/src/app/werkbank/[component]/page.tsx`, met een eigen root-layout naast `[market]`. Die geeft `notFound()` tenzij `WERKBANK=1`, en `proxy.ts` blokkeert hem in productie. Per component één pagina met een raster van varianten × staten, schakelaars voor modus, thema, richting en papier, en de spec-markdown erboven.
- **Waarom niet Storybook:**
  - Het is een tweede buildketen met eigen webpack/Vite-configuratie.
  - RSC-ondersteuning is er nog experimenteel.
  - Voor één persoon is het onderhoud groter dan het nut.
  - De werkbank draait met de echte Next, de echte fonts, de echte server components en de echte `globals.css`, en Playwright kan er direct op testen.
- **Site-agnostisch bewijzen:** de werkbank kan elke P-component ook in het **neutrale thema** tonen (`data-brand="neutral"`). Valt iets daar om, dan zit er merk in de kern.
- Admin krijgt dezelfde route (`apps/admin/src/app/werkbank`) voor de `admin`-patronen.
- **Overzicht:** `docs/design-system/README.md` met de tokenlijst (gegenereerd), de merkgids (§0) en de inventaris (§5).

### 6.4 Versiebeheer
- **Tijdens incubatie** (`packages/ui-core`, `packages/brand`): workspace-pakketten zonder losse versies. Wijzigingen staan in een `CHANGELOG.md` per pakket.
- **Na de verhuizing:** `@t-jarpis/tokens` en `@t-jarpis/ui` volgen semver met changesets, zoals `auth` en `config` nu.
  - **Major:** token hernoemd of verwijderd, component-API gebroken, standaardvariant veranderd.
  - **Minor:** nieuwe tokens, varianten of componenten, of een **zichtbare waardewijziging** (met voor/na-screenshot in de changeset).
  - **Patch:** bugfix zonder visueel verschil.
  - **Deprecaties:** een oude token blijft minstens één minor bestaan als alias (`--accent: var(--color-accent)`), met een lintwaarschuwing.
- `@kleurhoek/brand` blijft privé en wordt samen met de site uitgerold.

### 6.5 Visuele regressietests
- **Playwright `toHaveScreenshot`** op de werkbankpagina's.
  - Matrix: modus (kind/ouder/beheer, per component wat relevant is) × licht/donker × LTR/RTL × viewport (375 en 1024 px).
  - Omdat één pagina alle staten toont, blijft het aantal screenshots beperkt (ongeveer 4–8 per component).
- **Altijd in de officiële Playwright-Docker-image** (dezelfde fonts en rendering lokaal en in CI). De baselines staan in git.
- **Print:** `page.emulateMedia({ media: "print" })` plus screenshot van PlateSheet, PrintSheet en BookletBuilder in A4 en Letter. Daarbij één `page.pdf()`-rooktest per papiermaat (aantal pagina's klopt).
- **`@axe-core/playwright`** op elke werkbankpagina en op de echte pagina's die er nu al zijn (`e2e/shots` 1–8). Een nieuwe overtreding laat CI falen.
- **Updaten** gaat met een bewuste `--update-snapshots` in een aparte commit, zodat je bij een review de diff ziet.

---

## 7. Gefaseerd migratiepad (nog niet uitvoeren)

Schattingen zijn voor één persoon. Elke fase kan los live, zonder big bang.

**Fase 0: besluit en vastleggen (½ dag)**
- ADR 0012 "Design system": aanpak A, de lagen, incubatie in de Kleurhoek-repo, de hoofdregel uit §6.1.
- Architectuurdocument en diagrammen bijwerken (pakketten `ui-core` en `brand`, en de latere verhuizing naar het platform).
- CLAUDE.md van beide repos aanvullen met de regel en de DoD.

**Fase 1: vangnet en snelle winst (2–3 dagen)**
1. Werkbank-route plus Playwright-baselines van de huidige pagina's (vóór de refactor, zodat je ziet wat verandert).
2. `packages/brand/tokens/kleurhoek.tokens.json` plus een buildscript. De oude namen (`--bg`, `--fg`, `--line`, `--accent` …) worden aliassen, zodat er niets breekt.
3. Contrast- en focusfouten oplossen:
   - focusring van `.sw`;
   - `--color-border-control` op invoer, chips en seg;
   - danger `#c0352b`;
   - toast `#247c44`;
   - admin `--color-text-on-accent`;
   - `.pill.on` met donkerder tekst;
   - hover achter `(hover:hover)`;
   - "Haal eraf" en `.a4 .x` groter;
   - kleurnamen op de vakjes;
   - admin: zijmenu met `aria-current`, NavTabs zonder `tablist`, focusbare scrollregio;
   - 404 via i18n.
4. stylelint en ESLint tegen nieuwe hex-waarden. Bestaande overtredingen staan op een lijst om af te bouwen.

**Fase 2: kern-primitives (4–6 dagen)**
- `packages/ui-core` met `ui.css` (`@layer`) en Button, ButtonLink, ToggleButton, IconButton, Icon, Text, Heading, Eyebrow, Stack, Cluster, Grid, Card, Badge, StatusBadge, Callout, TextField, Checkbox, CheckboxGroup, Select, FilterChip, FilterGroup, SegmentedControl, ProgressBar, EmptyState, DescriptionList, SkipLink.
- Modi via `data-mode`.
- **Pagina voor pagina omzetten:** eerst admin (de risicoloze pagina's), dan account, dan de home, dan de studio.
- Admin-`globals.css` krimpt tot de shell. De element-selector op `button` verdwijnt.

**Fase 3: interactie met React Aria (3–4 dagen)**
- Menu (accountknop), AlertDialog (account verwijderen), ConfirmButton (koelkast), Toast met actie ("Opnieuw" wordt ongedaan maken), SwatchPicker als RadioGroup, SearchField, NumberField, NavTabs, Pagination, Tooltip.
- AdminShell, SideNav, PageHeader, DataTable, StatCard in `ui-core/admin`.

**Fase 4: merk (3–5 dagen, plus illustratiewerk)**
- Logo als SVG met varianten en een beeldmerk (ook voor de BOIP-aanvraag).
- Kindiconen in de plaatstijl. Oki en Sjors in EmptyState, 404 en Celebration.
- SponsoredLink met het label bij de link. "Voor ouders" krijgt de oudermodus en een eigen label.
- Categorieën naar tokensleutels (API-migratie). Eén paars.
- Plaatstijl uit `@kleurhoek/brand/plate` ook in de API.
- Printtokens met A4 en Letter via benoemde pagina's. RTL-check van alle P-componenten (logische eigenschappen).

**Fase 5: op verzoek (per geplande functie)**
- Componenten uit §5.3 volgens de hoofdregel: eerst spec en werkbank.
- **Verhuizing naar het platform** (`@t-jarpis/tokens`, `@t-jarpis/ui`) bij de start van de tweede site: verplaatsen, hernoemen, tarball in `vendor/`, ADR in het platform, changeset `0.1.0`.

---

## 8. Open vragen voor de eigenaar

1. **Platform nu of later?** Mijn advies: incuberen in de Kleurhoek-repo en verhuizen bij de tweede site, volgens je eigen regel. Wil je de admin-shell toch meteen in het platform, omdat elke site beheer heeft?
2. **Eén paars:** mag Ruimte van `#5b4fc9` naar het logopaars `#9b4fd0`? En mogen categoriekleuren in de database een sleutel worden in plaats van een hex?
3. **Logo:** laten we het SVG-woordmerk en het beeldmerk "K" (opnieuw) tekenen door een illustrator of letterontwerper, vóór de BOIP-registratie? Met welk budget?
4. **Oki en Sjors:** mogen ze de vaste gidsen worden (lege staten, feest, 404)? Zijn de namen definitief, ook voor andere talen?
5. **Eigen kindiconen** (ongeveer 16) tekenen in de plaatstijl, of voorlopig Lucide?
6. **Donkere modus:** automatisch houden zonder schakelaar (mijn advies), een schakelaar toevoegen, of het kinderdeel altijd licht?
7. **Letter:** vanaf welke markt? Bepaalt de markt het papier, of mag de ouder kiezen (PaperSizeSwitch)?
8. **Leerblad-letter:** Sniglet houden voor het overtrekwoord, of een schoolletter (enkele a/g) zoals Andika?
9. **Oudermodus 17 px** voor lopende tekst (grootouders): akkoord, ook al wordt het blok "Voor ouders" iets langer?
10. **ParentGate:** akkoord dat de kassa (en in de app ook de partnerlinks) achter een eenvoudige oudercheck komt?
11. **Admin-taal:** blijft beheer alleen Nederlands, of moet het voor een koper of een tweede site ook vertaalbaar zijn (dan ook i18n-props in de admin-patronen)?
12. **Toetsenbord in de studio:** moet kleuren ook zonder muis of touch kunnen (vlak voor vlak met Tab of pijltjes)? Voor toegankelijkheid wel aan te raden, maar het is extra werk.
