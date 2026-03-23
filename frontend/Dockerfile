FROM node:20-slim AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-slim AS runner
WORKDIR /app
COPY --from=builder /app/build ./build
COPY --from=builder /app/package.json .

ENV NODE_ENV=production
EXPOSE 3000

CMD ["node", "build/index.js"]
