// Gegenereerd door packages/theme/scripts/build.mjs. Niet met de hand wijzigen.
export const activeTheme = {
  "id": "studio",
  "name": "Studio",
  "font": "manrope",
  "logo": {
    "word": "kleurhoek",
    "blocks": [
      "krijt-rood",
      "krijt-amber",
      "krijt-groen",
      "krijt-blauw"
    ]
  }
} as const;
export const manifest = {
  "defaultTheme": "studio",
  "defaultFont": "manrope",
  "themes": [
    {
      "id": "studio",
      "name": "Studio",
      "description": "Rustig en strak: Manrope, 1px randen, hoek 8px, inktzwarte knoppen; kleur alleen in logo, stippen en platen (ADR 0012).",
      "font": "manrope"
    }
  ],
  "fonts": [
    {
      "id": "manrope",
      "family": "Manrope"
    },
    {
      "id": "nunito",
      "family": "Nunito"
    }
  ]
} as const;
