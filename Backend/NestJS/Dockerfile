# NestJS Complete Project Dockerfile
FROM node:20-alpine AS base

WORKDIR /usr/src/app

# Install build deps
RUN apk add --no-cache python3 make g++ git

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci --prefer-offline --no-audit --no-fund --legacy-peer-deps

# Copy source
COPY tsconfig.json tsconfig.build.json ./
COPY src ./src
COPY test ./test

# Build application
RUN npm run build --verbose

# Runtime image
FROM node:20-alpine AS runtime
WORKDIR /usr/src/app
ENV NODE_ENV=production

# Copy only necessary files
COPY --from=base /usr/src/app/node_modules ./node_modules
COPY --from=base /usr/src/app/dist ./dist
COPY --from=base /usr/src/app/package.json ./

EXPOSE 3000
CMD ["node", "dist/main.js"]