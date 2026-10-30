/**
 * IndexNow (ADR 0061): de sleutel waarmee Kleurhoek nieuwe pagina's bij Bing (en daarmee Copilot en ChatGPT),
 * Yandex, Seznam en Naver aanmeldt. Geen geheim: zoekmachines halen hem op via /indexnow.txt om te zien dat de
 * aanmelding echt van dit domein komt. Dezelfde sleutel staat in scripts/indexnow.mjs.
 */
export const INDEXNOW_KEY = "53075bde558b1ae534a24a6c12389173";
