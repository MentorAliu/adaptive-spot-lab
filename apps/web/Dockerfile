FROM node:24.19.0-bookworm-slim AS dependencies
RUN npm install --global pnpm@10.28.2
WORKDIR /workspace
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml ./
COPY apps/web/package.json apps/web/package.json
RUN pnpm install --frozen-lockfile

FROM dependencies AS source
COPY apps/web apps/web
COPY services/engine/openapi.json services/engine/openapi.json

FROM source AS build
RUN pnpm --filter web build

FROM node:24.19.0-bookworm-slim AS runtime
ENV NODE_ENV=production HOST=0.0.0.0 PORT=3000
WORKDIR /app
COPY --from=build --chown=node:node /workspace/apps/web/.output /app/.output
USER node
EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]
