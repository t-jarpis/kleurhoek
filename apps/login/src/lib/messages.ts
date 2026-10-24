/**
 * Teksten van de inlogpagina per taal (ADR 0029). De taal komt uit het inlogverzoek (ui_locales) of de
 * browser (Accept-Language) en staat daarna in de flow. Andere talen staan in locales/<taal>.ts.
 */
export const nl = {
  title: "Inloggen",
  expiredTitle: "Opnieuw beginnen",
  errExpired: "Deze inlogpoging is verlopen. Ga terug naar de site en klik opnieuw op Inloggen.",
  errOutage: "Inloggen lukt nu even niet. Probeer het over een paar minuten opnieuw.",
  errEmail: "Vul een geldig e-mailadres in.",
  errCode: "Deze code klopt niet of is verlopen.",
  errWait: "Wacht even voor je een nieuwe code vraagt.",
  errAdult: "Een account is alleen voor ouders en verzorgers van 16 jaar en ouder.",
  errRegister: "Vul je naam en een geldig e-mailadres in.",
  errRestart: "Er ging iets mis. Begin opnieuw.",
  backToSite: "Terug naar de site",
  privacy: "Privacy",
  emailIntro: (site: string) => `Voor ouders en verzorgers: bewaar je boekjes en voorkeuren bij ${site}.`,
  email: "E-mailadres",
  next: "Verder",
  noAccount: "Nog geen account?",
  makeOne: "Maak er een",
  welcomeBack: "Welkom terug",
  passkeyFor: "Log in met je passkey voor",
  loginPasskey: "Inloggen met passkey",
  ratherCode: "Stuur me liever een code",
  otherEmail: "Ander e-mailadres",
  enterCode: "Vul je code in",
  codeSentVerify: "We hebben een code gestuurd naar dit adres om het te bevestigen:",
  codeSentLogin: "Als dit adres bij ons bekend is, hebben we daar een code naartoe gestuurd. Kijk ook in je ongewenste mail.",
  code: "Code",
  confirm: "Bevestigen",
  login: "Inloggen",
  resend: "Stuur een nieuwe code",
  createTitle: "Account maken",
  createIntro: "Een account is voor ouders en verzorgers. Kinderen kleuren zonder account.",
  firstName: "Je voornaam",
  adultBefore: "Ik ben 16 jaar of ouder en ga akkoord met de",
  privacyStatement: "privacyverklaring",
  create: "Account maken",
  haveAccount: "Al een account?",
  offerTitle: "Volgende keer sneller?",
  offerText: "Met een passkey log je in met je vingerafdruk, gezicht of de pincode van je apparaat. Geen code meer nodig.",
  makePasskey: "Passkey maken",
  notNow: "Niet nu",
  wait: "Even geduld…",
  pkFailed: "Dat lukte niet.",
  pkNoneChosen: "Geen passkey gekozen.",
  pkNoneMade: "Geen passkey gemaakt.",
  pkAborted: "Afgebroken. Probeer het opnieuw of kies een andere manier.",
  pkBadPasskey: "Dat lukte niet met deze passkey.",
  pkNoConnection: "Even geen verbinding. Probeer het opnieuw.",
  loggedOutTitle: "Je bent uitgelogd",
  loggedOutText: "Tot de volgende keer.",
  toSite: "Naar Kleurhoek",
};

/** Zelfde vorm als nl, met gewone strings. */
type Widen<T> = T extends string ? string : T extends (...a: infer A) => infer R ? (...a: A) => Widen<R> : T extends object ? { [K in keyof T]: Widen<T[K]> } : T;
export type LoginMessages = Widen<typeof nl>;
/** De teksten die de passkey-knop in de browser nodig heeft. */
export type PasskeyTexts = Pick<LoginMessages, "wait" | "pkFailed" | "pkNoneChosen" | "pkNoneMade" | "pkAborted">;
