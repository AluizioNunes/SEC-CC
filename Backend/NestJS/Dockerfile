# NestJS Dockerfile
FROM node:22-alpine AS base

WORKDIR /usr/src/app

# Install build deps
RUN apk add --no-cache python3 make g++

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci

# Copy source
COPY tsconfig.json ./
COPY src ./src

# Build application
RUN npm run build

# Runtime image
FROM node:22-alpine AS runtime
WORKDIR /usr/src/app
ENV NODE_ENV=production

# Copy only necessary files
COPY --from=base /usr/src/app/node_modules ./node_modules
COPY --from=base /usr/src/app/dist ./dist
COPY --from=base /usr/src/app/package.json ./

EXPOSE 3000
CMD ["node", "dist/main.js"]
