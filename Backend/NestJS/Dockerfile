# NestJS Complete Project Dockerfile

# Build stage
FROM node:20-alpine AS base
WORKDIR /usr/src/app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci --prefer-offline --no-audit --no-fund --legacy-peer-deps || npm install --prefer-offline --no-audit --no-fund --legacy-peer-deps

# Copy source
COPY tsconfig.json tsconfig.build.json ./
COPY src ./src
COPY test ./test

# Build application
RUN npm run build --verbose

# Runtime stage
FROM node:20-alpine AS runtime
WORKDIR /usr/src/app
ENV NODE_ENV=production

# Create a non-root user and group
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Copy necessary files from the build stage
COPY --from=base /usr/src/app/node_modules ./node_modules
COPY --from=base /usr/src/app/dist ./dist
COPY --from=base /usr/src/app/package.json ./

# Set correct ownership
RUN chown -R appuser:appgroup /usr/src/app

# Switch to the non-root user
USER appuser

EXPOSE 3000
CMD ["node", "dist/main.js"]