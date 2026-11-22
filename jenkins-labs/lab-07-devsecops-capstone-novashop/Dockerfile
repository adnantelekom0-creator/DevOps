# ===================================================
# Stage 1: Dependency Isolation
# ===================================================
FROM node:18-alpine AS dependencies
WORKDIR /app
COPY app/package.json ./
RUN npm install --production

# ===================================================
# Stage 2: Hardened, Minimal Runtime Container
# ===================================================
FROM node:18-alpine
LABEL maintainer="DevOps Atolyesi <egitim@devopsatolyesi.com>"
LABEL org.opencontainers.image.title="novashop-order-service"

WORKDIR /app

# Non-root execution enforcement
USER node

COPY --chown=node:node --from=dependencies /app/package.json ./
COPY --chown=node:node app/ ./

ARG APP_VERSION=1.0.0
ARG APP_ENV=production
ENV PORT=8080 \
    APP_VERSION=${APP_VERSION} \
    APP_ENV=${APP_ENV} \
    NODE_ENV=production

EXPOSE 8080

HEALTHCHECK --interval=15s --timeout=5s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:8080/health || exit 1

CMD ["node", "server.js"]
