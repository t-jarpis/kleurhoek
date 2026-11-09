# Eigendomsregister Kleurhoek

Wat er bij Kleurhoek hoort, waar het staat en wat er bij een verkoop mee moet (ADR 0004: los verkoopbaar). Geen geheimen in dit bestand: alleen namen en plaatsen. Bijwerken bij elke nieuwe dienst, elk account en elke sleutel. Regels met *na te kijken* zijn nog niet bevestigd door de eigenaar.

Stand: 9 november 2026. Eigenaar van alles hieronder: Thijs Langenhuijsen (privé; nog geen bedrijf).

## Naam, merk en inhoud
| Wat | Stand | Bij verkoop |
|---|---|---|
| Naam "Kleurhoek" | Niet geregistreerd als merk. Gecontroleerd op 9 november 2026 in TMview (EUIPO, omvat het Benelux-register van BOIP en het EU-register): geen merk "Kleurhoek" of "Denkhoek", ook niet met "fuzzy" zoeken. | Overweeg registratie vóór verkoop (Benelux, klassen 16, 41). |
| Platen | Eigen ontwerpen, gemaakt met hulp van AI en elk nagekeken (`packages/catalog-data`, generators in `scripts/plates`). Eén proefplaat is getraceerd uit een tekening van een beeldmodel (`dino-likt-aan-een-ijsje`, bron in de repo). | Gaat mee. |
| Logo en huisstijl | Eigen ontwerp (`docs/huisstijl`, design system). | Gaat mee. |
| Teksten en vertalingen (29 talen) | In de repo. | Gaat mee. |

## Domeinen en DNS
| Wat | Waar | Bij verkoop |
|---|---|---|
| kleurhoek.nl, kleurhoek.be, kleurhoek.com | Registrar *na te kijken* (kleurhoek.nl waarschijnlijk Neostrada); DNS bij Cloudflare, Terraform `infra/envs/zone` en `infra/modules/market-domain`. | Domeinen verhuizen; zones overdragen of opnieuw met Terraform. |
| Cloudflare-account | Account van Thijs; zones, Workers (analytics, inloggen), regels, Zero Trust Access voor het admin panel. | Zones en Workers naar het account van de koper (Terraform). |
| Cloudflare-tokens (Terraform) | In de sleutelhanger op de Mac. | Intrekken. |
| Mail op eigen domein | Brevo en Scaleway TEM (ADR's over mail en bezorging). | Afzenderdomeinen en accounts overdragen of opnieuw. |

## Code
| Wat | Waar | Bij verkoop |
|---|---|---|
| Repo `t-jarpis/kleurhoek` | GitHub (privé), Actions (CI, Deploy, statuscontrole), omgevingen `dev` en `prod`. | Repo overdragen of kopiëren. |
| Platformpakketten `@t-jarpis/*` | Repo `t-jarpis/platform`; als tarball in `vendor/` (ADR 0009). | Tarballs gaan mee; licentie voor de koper regelen. |

## Hosting en data
| Wat | Waar | Bij verkoop |
|---|---|---|
| Containers, database, registry, opslag | Scaleway, eigen organisatie, projecten `kleurhoek-prod` en `kleurhoek-dev`. | Project/organisatie overdragen of opnieuw met Terraform plus `pg_dump`. |
| Gedeeld met Denkhoek | In `kleurhoek-prod` draaien ook de containers en de database `denkhoek` van Denkhoek (ADR 0095). | Denkhoek eerst verhuizen (eigen project) of afspraken maken; database `denkhoek` niet meeleveren. |
| Cockpit-token (capaciteit) | Scaleway, alleen metrics (ADR 0092). | Opnieuw aanmaken. |
| Terraform-state | Scaleway Object Storage (bucket *na te kijken* in `infra/envs/*/main.tf`). | Meeleveren. |
| Gegevens van bezoekers | Accounts (16+, ADR 0002) in Zitadel; tellingen zonder persoonsgegevens; abonnees op mail. | Overdracht volgens de privacyverklaring; bezoekers informeren. |

## Inloggen
| Wat | Waar | Bij verkoop |
|---|---|---|
| Zitadel-organisaties "Kleurhoek", "Kleurhoek (dev)" en "Org Beheer" | Zitadel Cloud-instance `dev-qbmulu.eu1.zitadel.cloud` (gedeeld met Denkhoek). Terraform `infra/modules/zitadel`. | Naar een eigen instance van de koper; gebruikers exporteren/importeren. |
| Eigen inlogpagina login.kleurhoek.nl | Eigen app `apps/login` (ADR 0018). | Gaat mee. |
| Inloggen met Google, Apple, Microsoft | App-registraties bij die partijen *na te kijken* (ADR 0004 noemt ze). | Overdragen of opnieuw registreren. |

## Externe accounts
| Wat | Waar | Bij verkoop |
|---|---|---|
| Google Search Console, Bing Webmaster Tools | Account van Thijs. | Eigenaar toevoegen en zelf verwijderen. |
| Pinterest, Facebook, Instagram (Meta) | Accounts en app-registraties voor automatisch plaatsen (ADR 0069 e.v.). | Accounts en apps overdragen. |
| Amazon-partnerprogramma | Per land (winkel, ADR 0011). | Opnieuw aanmelden door de koper (partnerprogramma's zijn persoonsgebonden). |
| IndexNow | Sleutel in de repo/Deploy-workflow. | Gaat mee. |
