# syntax=docker/dockerfile:1.7
# Eén Dockerfile voor de drie apps: `--target api`, `--target web` of `--target admin`.
# Bouwen vanaf de repo-root: docker build --target api -t kleurhoek-api .
# Platformpakketten komen uit vendor/, dus er is geen token voor een registry nodig.

ARG NODE_IMAGE=node:22.23.4-alpine

FROM ${NODE_IMAGE} AS base
ENV PNPM_HOME=/pnpm PATH=/pnpm:$PATH CI=1 NEXT_TELEMETRY_DISABLED=1 TURBO_TELEMETRY_DISABLED=1
RUN corepack enable
WORKDIR /repo

# Afhankelijkheden ophalen op basis van alleen de lockfile: deze laag blijft gecachet zolang die niet verandert.
FROM base AS deps
COPY pnpm-lock.yaml pnpm-workspace.yaml package.json ./
COPY vendor ./vendor
RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    pnpm fetch --frozen-lockfile

FROM deps AS build
ARG NEXT_PUBLIC_MARKETS=nl-nl
ENV NEXT_PUBLIC_MARKETS=${NEXT_PUBLIC_MARKETS} NODE_ENV=production
COPY . .
RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    pnpm install --frozen-lockfile --offline --prod=false
RUN pnpm turbo run build --filter=@kleurhoek/api --filter=@kleurhoek/web --filter=@kleurhoek/admin
# Alleen productie-afhankelijkheden van de API, zonder symlinks naar de workspace.
RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    pnpm --filter @kleurhoek/api deploy --prod --legacy /out/api

FROM ${NODE_IMAGE} AS runtime
RUN apk add --no-cache tini && apk upgrade --no-cache
ENV NODE_ENV=production
WORKDIR /app
ENTRYPOINT ["/sbin/tini", "--"]

# API: migreert (en in dev: vult de catalogus) bij het opstarten; handmatig kan ook met `node dist/db/migrate.js` en `node dist/db/seed-cli.js`.
FROM runtime AS api
COPY --from=build --chown=node:node /out/api /app
USER node
EXPOSE 3001
CMD ["node", "dist/main.js"]

FROM runtime AS web
# Ruimere grens voor request-headers: sessiecookies (Zitadel-tokens) plus de cookie van Cloudflare Access.
ENV PORT=3000 HOSTNAME=0.0.0.0 NODE_OPTIONS=--max-http-header-size=32768
COPY --from=build --chown=node:node /repo/apps/web/.next/standalone /app
COPY --from=build --chown=node:node /repo/apps/web/.next/static /app/apps/web/.next/static
USER node
EXPOSE 3000
COPY --chown=node:node docker/request-log.cjs /app/request-log.cjs
CMD ["node", "-r", "/app/request-log.cjs", "apps/web/server.js"]

FROM runtime AS admin
ENV PORT=3002 HOSTNAME=0.0.0.0 NODE_OPTIONS=--max-http-header-size=32768
COPY --from=build --chown=node:node /repo/apps/admin/.next/standalone /app
COPY --from=build --chown=node:node /repo/apps/admin/.next/static /app/apps/admin/.next/static
USER node
EXPOSE 3002
COPY --chown=node:node docker/request-log.cjs /app/request-log.cjs
CMD ["node", "-r", "/app/request-log.cjs", "apps/admin/server.js"]
