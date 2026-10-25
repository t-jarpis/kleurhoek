import type { Org } from "./org";
import { basePath, siteDomains } from "./sites";

/** Voorvoegsel van de links voor deze organisatie en markt (ADR 0040): alleen Kleurhoek zelf op eigen domeinen zonder /<markt>. */
export const baseFor = (org: Pick<Org, "isDefault"> | null, market: string) => basePath(market, !!org?.isDefault && !!siteDomains());
