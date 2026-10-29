# 0055 · Vindbaarheid: onderwerppagina's, kruimelpad, afbeeldingen en AI-zoekdiensten

- Status: aangenomen
- Datum: 2026-10-29

## Context
Op "kleurhoek" werd de site gevonden, op "kleurplaat" niet. Een controle van de live site liet zien waarom:
- De voorpagina had geen H1.
- Plaatjes hadden een lege alt-tekst.
- Onderwerpen bestonden alleen als `?`-filter. Er was dus geen pagina die "kleurplaten dieren" of "Ausmalbilder Weihnachten" heette.
- Plaatpagina's hadden geen afbeelding voor delen, geen kruimelpad en geen links naar andere platen.

Daarnaast wil Thijs gevonden worden via AI-diensten (ChatGPT, Claude, Copilot, Perplexity). robots.txt weerde sinds ADR 0045 ook PerplexityBot, terwijl dat een zoekindex is en geen trainer.

## Besluit
- **Onderwerppagina's.** Elke waarde van een filter krijgt een eigen adres met eigen titel, H1, korte tekst, meta-omschrijving en JSON-LD (CollectionPage + ItemList + BreadcrumbList):
  - `/onderwerp/<slug>` en `/feestdag/<slug>`;
  - `/leeftijd/<slug>` en `/soort/<slug>`;
  - `/werelddeel/<slug>`.

  Een pagina bestaat alleen als er platen zijn. De filters op de voorpagina blijven zoals ze zijn (`lib/topics.ts`, `components/TopicPage.tsx`).
- **Feestdagpagina's** hebben geen taalversies (hreflang), want ze bestaan alleen in landen die het feest vieren. De sitemap volgt dat.
- **Interne links.** Een nieuwe component TopicLinks staat op de voorpagina en op elke onderwerppagina, met links naar alle onderwerppagina's per groep. Elke plaat is zo met twee klikken bereikbaar.
- **Voorpagina.** De openingszin is de H1.
- **Plaatkaarten.** Kaarten hebben een alt-tekst ("Kleurplaat kat"). Op onderwerppagina's is die alt-tekst langer.
- **Plaatpagina:**
  - een kruimelpad (Kleurhoek › onderwerp › plaat);
  - "Meer <onderwerp>" met tot 12 platen van hetzelfde onderwerp, eerst die van dezelfde leeftijd, plus een link naar de onderwerppagina;
  - og:image en twitter `summary_large_image` met de PNG van de plaat;
  - JSON-LD CreativeWork met ImageObject en BreadcrumbList.

  De PNG-renderer laadt nu ook de tekensets latin-ext, Grieks en Cyrillisch, zodat deelplaatjes in alle talen kloppen.
- **Design system.** Er zijn drie nieuwe componenten: Breadcrumb, TopicLinks en SectionHead (`.ui-crumbs`, `.ui-topiclinks`, `.ui-sectionhead`).
- **Sitemap.** Per markt staan de onderwerppagina's in de sitemap.
- **AI-zoekdiensten:**
  - robots.txt heeft een aparte groep die zoek- en assistentbots expliciet toelaat: OAI-SearchBot, ChatGPT-User, Claude-SearchBot, Claude-User, PerplexityBot, Perplexity-User, DuckAssistBot, MistralAI-User, Applebot en bingbot. Ze krijgen dezelfde uitzonderingen als iedereen (account, beheer, auth).
  - Trainers blijven geweerd, zoals in ADR 0045: GPTBot, ClaudeBot, CCBot, Google-Extended en de andere.
  - PerplexityBot gaat van de trainerslijst af.
- **llms.txt.** Elk productiedomein krijgt een `/llms.txt` volgens llmstxt.org. Daarin staan per markt de beginpagina en de onderwerppagina's, met de titel in de taal van die markt en het aantal platen. Het bestand staat in `SHARED_PATH` en bestaat buiten productie niet (ADR 0040).
- **Cloudflare.** De oude instelling "Block AI bots" (ADR 0045) blokkeert alleen de categorie Training. Search en Agent blijven toegestaan. In Terraform hoeft niets te veranderen.

## Gevolgen
- Per markt komen er tientallen pagina's bij die op een zoekterm passen. Op .com en .be zijn ze er ook in elke taal.
- ChatGPT en Copilot zoeken via de Bing-index en Claude onder meer via Brave. Daarom zijn aanmelden bij Bing Webmaster Tools en Google Search Console en links van andere sites (backlinks) minstens zo belangrijk als deze code.
- De voorpagina wordt langer door de TopicLinks onder het rooster.
