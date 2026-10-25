import type { Block, I18nText, Step, TemplateKind, Trigger } from "./messaging.types";

/**
 * Startinhoud (ADR 0037): de vaste templates en drie workflows. De seed zet ze alleen neer als ze nog niet bestaan;
 * daarna zijn ze van het admin panel. Teksten in alle talen van de site; ontbreekt een taal, dan Nederlands.
 */
const t = (nl: string, de: string, en: string, fr: string, es: string, it: string, pl: string): I18nText => ({ nl, de, en, fr, es, it, pl });

export const DEFAULT_TEMPLATES: { slug: string; name: string; kind: TemplateKind; subject: I18nText; preheader: I18nText; blocks: Block[] }[] = [
  {
    slug: "bevestigen", name: "Aanmelding bevestigen", kind: "system",
    subject: t("Bevestig je aanmelding bij Kleurhoek", "Bestätige deine Anmeldung bei Kleurhoek", "Confirm your Kleurhoek sign-up", "Confirmez votre inscription à Kleurhoek", "Confirma tu suscripción a Kleurhoek", "Conferma la tua iscrizione a Kleurhoek", "Potwierdź zapis do Kleurhoek"),
    preheader: t("Nog één klik, dan krijg je onze mails.", "Noch ein Klick, dann bekommst du unsere Mails.", "One more click and you're in.", "Encore un clic et c'est fait.", "Un clic más y listo.", "Ancora un clic ed è fatta.", "Jeszcze jedno kliknięcie."),
    blocks: [
      { id: "h", type: "heading", text: t("Bijna klaar", "Fast geschafft", "Almost done", "Presque fini", "Casi listo", "Quasi fatto", "Prawie gotowe") },
      { id: "p", type: "text", text: t("Klik op de knop om je aanmelding te bevestigen. Daarna sturen we je alleen mails over de onderwerpen die je koos.", "Klicke auf den Button, um deine Anmeldung zu bestätigen. Danach schicken wir dir nur Mails zu den Themen, die du gewählt hast.", "Click the button to confirm your sign-up. After that we'll only email you about the topics you chose.", "Cliquez sur le bouton pour confirmer votre inscription. Ensuite, nous vous écrirons uniquement sur les sujets choisis.", "Pulsa el botón para confirmar tu suscripción. Después solo te escribiremos sobre los temas que elegiste.", "Clicca il pulsante per confermare l'iscrizione. Poi ti scriveremo solo sugli argomenti scelti.", "Kliknij przycisk, aby potwierdzić zapis. Potem będziemy pisać tylko o wybranych tematach.") },
      { id: "b", type: "button", label: t("Aanmelding bevestigen", "Anmeldung bestätigen", "Confirm sign-up", "Confirmer l'inscription", "Confirmar suscripción", "Conferma iscrizione", "Potwierdź zapis"), url: "{{bevestigen}}" },
      { id: "q", type: "text", text: t("De link werkt 7 dagen.", "Der Link ist 7 Tage gültig.", "The link works for 7 days.", "Le lien est valable 7 jours.", "El enlace funciona durante 7 días.", "Il link vale 7 giorni.", "Link działa przez 7 dni.") },
    ],
  },
  {
    slug: "welkom", name: "Welkom", kind: "system",
    subject: t("Welkom bij Kleurhoek", "Willkommen bei Kleurhoek", "Welcome to Kleurhoek", "Bienvenue chez Kleurhoek", "Bienvenido a Kleurhoek", "Benvenuto in Kleurhoek", "Witaj w Kleurhoek"),
    preheader: t("Een paar platen om mee te beginnen.", "Ein paar Vorlagen für den Anfang.", "A few pages to start with.", "Quelques coloriages pour commencer.", "Unos dibujos para empezar.", "Qualche disegno per iniziare.", "Kilka plansz na początek."),
    blocks: [
      { id: "h", type: "heading", text: t("Welkom!", "Willkommen!", "Welcome!", "Bienvenue !", "¡Bienvenido!", "Benvenuto!", "Witaj!") },
      { id: "p", type: "text", text: t("Leuk dat je erbij bent. Alle platen zijn zelf getekend, gratis te printen of online in te kleuren. Om mee te beginnen:", "Schön, dass du dabei bist. Alle Vorlagen sind selbst gezeichnet, kostenlos zum Drucken oder online Ausmalen. Für den Anfang:", "Great to have you. Every page is drawn by us, free to print or colour in online. To start with:", "Ravi de vous compter parmi nous. Tous les coloriages sont dessinés par nous, gratuits à imprimer ou à colorier en ligne. Pour commencer :", "Nos alegra tenerte aquí. Todos los dibujos son nuestros, gratis para imprimir o colorear en línea. Para empezar:", "Che bello averti qui. Tutti i disegni sono nostri, gratis da stampare o colorare online. Per iniziare:", "Cieszymy się, że jesteś. Wszystkie plansze rysujemy sami, za darmo do druku lub kolorowania online. Na początek:") },
      { id: "pl", type: "plates", source: "new", max: 6, columns: 3 },
      { id: "b", type: "button", label: t("Naar Kleurhoek", "Zu Kleurhoek", "Go to Kleurhoek", "Aller sur Kleurhoek", "Ir a Kleurhoek", "Vai a Kleurhoek", "Przejdź do Kleurhoek"), url: "{{site}}" },
    ],
  },
  {
    slug: "nieuwe-platen", name: "Nieuwe platen", kind: "automation",
    subject: t("Nieuwe platen bij Kleurhoek", "Neue Vorlagen bei Kleurhoek", "New pages at Kleurhoek", "Nouveaux coloriages chez Kleurhoek", "Nuevos dibujos en Kleurhoek", "Nuovi disegni su Kleurhoek", "Nowe plansze w Kleurhoek"),
    preheader: t("Vers getekend, klaar om te kleuren.", "Frisch gezeichnet, bereit zum Ausmalen.", "Freshly drawn, ready to colour.", "Tout juste dessinés, prêts à colorier.", "Recién dibujados, listos para colorear.", "Appena disegnati, pronti da colorare.", "Świeżo narysowane, gotowe do kolorowania."),
    blocks: [
      { id: "h", type: "heading", text: t("Nieuw deze week", "Neu diese Woche", "New this week", "Nouveau cette semaine", "Nuevo esta semana", "Novità della settimana", "Nowości tego tygodnia") },
      { id: "pl", type: "plates", source: "new", max: 9, columns: 3 },
      { id: "b", type: "button", label: t("Alle platen bekijken", "Alle Vorlagen ansehen", "See all pages", "Voir tous les coloriages", "Ver todos los dibujos", "Vedi tutti i disegni", "Zobacz wszystkie plansze"), url: "{{site}}" },
    ],
  },
  {
    slug: "feestdag", name: "Feestdag komt eraan", kind: "automation",
    subject: t("Platen voor de feestdag die eraan komt", "Vorlagen für den kommenden Feiertag", "Pages for the upcoming holiday", "Des coloriages pour la fête qui arrive", "Dibujos para la fiesta que se acerca", "Disegni per la festa in arrivo", "Plansze na nadchodzące święto"),
    preheader: t("Op tijd printen.", "Rechtzeitig drucken.", "Print them in time.", "À imprimer à temps.", "Imprímelos a tiempo.", "Da stampare in tempo.", "Wydrukuj na czas."),
    blocks: [
      { id: "h", type: "heading", text: t("Het is bijna feest", "Bald wird gefeiert", "Almost time to celebrate", "C'est bientôt la fête", "Pronto es fiesta", "Presto si festeggia", "Już niedługo święto") },
      { id: "pl", type: "plates", source: "holiday", max: 9, columns: 3 },
      { id: "b", type: "button", label: t("Meer feestplaten", "Mehr Festvorlagen", "More holiday pages", "Plus de coloriages de fête", "Más dibujos de fiesta", "Altri disegni di festa", "Więcej świątecznych plansz"), url: "{{site}}?onderwerp=feest" },
    ],
  },
  {
    slug: "nieuwsbrief", name: "Nieuwsbrief (basis)", kind: "campaign",
    subject: t("Nieuws van Kleurhoek", "Neues von Kleurhoek", "News from Kleurhoek", "Des nouvelles de Kleurhoek", "Novedades de Kleurhoek", "Novità da Kleurhoek", "Wiadomości z Kleurhoek"),
    preheader: {},
    blocks: [
      { id: "h", type: "heading", text: { nl: "Kop van de nieuwsbrief" } },
      { id: "p", type: "text", text: { nl: "Schrijf hier je bericht. Een lege regel begint een nieuwe alinea. **Vet** en [een link](https://www.kleurhoek.nl) kan ook." } },
      { id: "pl", type: "plates", source: "new", max: 6, columns: 3 },
      { id: "b", type: "button", label: { nl: "Naar Kleurhoek" }, url: "{{site}}" },
    ],
  },
];

export const DEFAULT_WORKFLOWS: { slug: string; name: string; enabled: boolean; trigger: Trigger; steps: Step[] }[] = [
  { slug: "welkom", name: "Welkom na aanmelden", enabled: true, trigger: { type: "subscribed" }, steps: [{ type: "send", template: "welkom" }] },
  {
    slug: "nieuwe-platen-wekelijks", name: "Nieuwe platen, elke maandag", enabled: true, trigger: { type: "schedule", weekday: 1, hour: 8 },
    steps: [{ type: "filter", topics: ["nieuwe-platen"] }, { type: "require_plates", min: 3 }, { type: "send", template: "nieuwe-platen" }],
  },
  {
    slug: "feestdag", name: "Twee weken voor een feestdag", enabled: true, trigger: { type: "holiday_soon", days: 14 },
    steps: [{ type: "filter", topics: ["feestdagen"] }, { type: "send", template: "feestdag" }],
  },
];
