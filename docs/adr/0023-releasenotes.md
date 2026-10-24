# 0023 Releasenotes in het admin panel, en één goedkeuring per uitrol

Datum: 24-10-2026. Status: aangenomen.

## Context
Na elke uitrol willen we in het admin panel zien wat er veranderde, per omgeving. Daarnaast vroeg een uitrol naar productie twee goedkeuringen: bouwen en uitrollen waren aparte jobs in de GitHub-omgeving `prod`.

## Besluit
- **Eén job** in `.github/workflows/deploy.yml`: bouwen en uitrollen samen, dus één goedkeuring voor prod. De vier images worden in één keer gebouwd met `docker buildx bake` (`docker-bake.hcl`); de gedeelde stappen draaien één keer.
- **Releasenotes**: de workflow schrijft de laatste 300 commits naar `apps/api/release-log.json` (sha, datum, onderwerp en de trailer `Release-note:`), en geeft de commit mee als `BUILD_SHA`. Beide gaan in het API-image.
- Bij het opstarten legt de API in `operations.releases` vast welke versie draait, zodra die anders is dan de vorige: eerste release, nieuwe release (met de commits sinds de vorige) of terugdraaien (een versie die eerder draaide). Een advisory lock voorkomt dubbele regels bij meerdere replica's. Er is geen extra geheim of aanroep vanuit GitHub nodig, en terugdraaien na een mislukte test komt er vanzelf in.
- **Nederlandse tekst**: een commit met een merkbare wijziging krijgt de trailer `Release-note: <zin in het Nederlands>`. Commits zonder trailer staan ingeklapt als technische wijziging (het Engelse onderwerp).
- Pagina **Releases** in het admin panel (recht `releases.read`, voor alle ingebouwde rollen), component ReleaseNotes uit het design system.

## Gevolgen
- Lokaal (docker compose) is er geen `BUILD_SHA`: dan worden geen releases vastgelegd.
- Releases zijn per omgeving, want elke omgeving heeft een eigen database.
