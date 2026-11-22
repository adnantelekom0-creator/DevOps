# Asama 1: Build / Test asamasi
FROM node:18-alpine AS builder
WORKDIR /app
COPY app/package.json ./
RUN npm install --production && mkdir -p /app/node_modules

# Asama 2: Minimal ve Guvenli Runtime asamasi
FROM node:18-alpine
LABEL maintainer="DevOps Atolyesi <egitim@devopsatolyesi.com>"
WORKDIR /app

# Guvenlik: Root yerine node kullanicisi ile calistirma
USER node

COPY --chown=node:node --from=builder /app/node_modules ./node_modules
COPY --chown=node:node app/ ./

ARG APP_VERSION=1.0.0
ENV PORT=3000 \
    APP_VERSION=${APP_VERSION} \
    NODE_ENV=production

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:3000/health || exit 1

CMD ["node", "server.js"]
