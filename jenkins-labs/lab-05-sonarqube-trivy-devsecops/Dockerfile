FROM node:18-alpine
WORKDIR /app
COPY app/package*.json ./
RUN npm install --production
COPY app/ ./
USER node
EXPOSE 3000
CMD ["node", "index.js"]
