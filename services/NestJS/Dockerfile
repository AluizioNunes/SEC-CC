# NestJS Complete Project Dockerfile
FROM node:20-alpine AS base

WORKDIR /usr/src/app

# Install build deps
RUN apk add --no-cache python3 make g++ git

# Copy package files
COPY ../../package-nestjs.json package.json
COPY ../../Backend/NestJS/package-lock.json ./

# Install dependencies
RUN npm ci --prefer-offline --no-audit --no-fund --legacy-peer-deps || npm install --prefer-offline --no-audit --no-fund --legacy-peer-deps

# Copy source
COPY ../../tsconfig-nestjs.json tsconfig.json
COPY ../../tsconfig.build-nestjs.json tsconfig.build.json
COPY ../../Backend/NestJS/src ./src
COPY ../../Backend/NestJS/test ./test

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