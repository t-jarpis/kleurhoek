/**
 * Alle permissies van de API. Een endpoint vraagt er precies één; rollen bundelen ze.
 * Nieuwe permissie? Voeg hem hier toe en geef hem aan de juiste ingebouwde rollen.
 */
export const PERMISSIONS = {
  "analytics.read": "Bezoekers en downloads bekijken",
  "operations.ratelimit.read": "Rate limits bekijken",
  "operations.ratelimit.manage": "Rate limits wijzigen",
  "operations.access.read": "Toegang tot de website (IP-lijst) bekijken",
  "operations.access.manage": "Toegang tot de website (IP-lijst) wijzigen",
  "identity.users.read": "Gebruikers en rollen bekijken",
  "identity.users.block": "Gebruikers blokkeren en deblokkeren",
  "identity.roles.assign": "Rollen toekennen aan beheerders",
  "catalog.manage": "Platen beheren",
  "availability.manage": "Beschikbaarheid per land beheren",
  "shop.read": "Winkel en winkelcijfers bekijken",
  "shop.manage": "Winkelkoppelingen en producten beheren",
  "organizations.read": "Organisaties en huisstijl bekijken",
  "organizations.manage": "Organisaties, huisstijl, domeinen en aanbod wijzigen",
} as const;

export type Permission = keyof typeof PERMISSIONS;
export const ALL_PERMISSIONS = Object.keys(PERMISSIONS) as Permission[];

export interface BuiltInRole { slug: string; name: string; permissions: Permission[] }

/** Ingebouwde rollen. Worden bij elke start bijgewerkt, zodat code en database niet uit elkaar lopen. */
export const BUILT_IN_ROLES: BuiltInRole[] = [
  { slug: "platformbeheerder", name: "Platformbeheerder", permissions: ALL_PERMISSIONS },
  { slug: "contentbeheerder", name: "Contentbeheerder", permissions: ["catalog.manage", "availability.manage", "analytics.read", "shop.read", "shop.manage", "organizations.read"] },
  { slug: "analist", name: "Analist", permissions: ["analytics.read", "operations.ratelimit.read", "operations.access.read", "shop.read"] },
  { slug: "support", name: "Support", permissions: ["identity.users.read", "identity.users.block"] },
];
