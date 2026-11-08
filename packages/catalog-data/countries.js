"use strict";
/**
 * Landen bij platen staan in plates.json met hun Nederlandse naam (de bron). Op de site tonen we ze in de
 * taal van de markt, via de ISO-code en Intl.DisplayNames (ADR 0094). Een nieuw land komt hier bij;
 * test/countries.test.js controleert dat elk land in plates.json een code heeft.
 */
const COUNTRY_CODES = {
  "Australië": "AU", "Brazilië": "BR", "Canada": "CA", "China": "CN", "Egypte": "EG", "Frankrijk": "FR",
  "India": "IN", "Italië": "IT", "Japan": "JP", "Kenia": "KE", "Mexico": "MX", "Nederland": "NL",
  "Nieuw-Zeeland": "NZ", "Peru": "PE", "Verenigde Staten": "US",
};

const cache = new Map();
/** Naam van een land (Nederlandse bronnaam) in de gevraagde taal; valt terug op de bronnaam. */
function countryName(country, language) {
  const code = COUNTRY_CODES[country];
  if (!code || language === "nl") return country;
  try {
    let names = cache.get(language);
    if (!names) { names = new Intl.DisplayNames([language], { type: "region", fallback: "none" }); cache.set(language, names); }
    return names.of(code) ?? country;
  } catch { return country; }
}

module.exports = { COUNTRY_CODES, countryName };
