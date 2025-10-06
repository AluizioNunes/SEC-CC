# NestJS Dockerfile
FROM node:22-alpine AS base

WORKDIR /usr/src/app

# Install build deps
RUN apk add --no-cache python3 make g++

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Copy source
COPY tsconfig.json ./
COPY src ./src

# Runtime image (no build step)
FROM node:22-alpine AS runtime
WORKDIR /usr/src/app
ENV NODE_ENV=production

# Copy only necessary files
COPY --from=base /usr/src/app/node_modules ./node_modules
COPY --from=base /usr/src/app/src ./src
COPY --from=base /usr/src/app/tsconfig.json ./
COPY --from=base /usr/src/app/package.json ./

EXPOSE 3000
CMD ["npm", "start"]
