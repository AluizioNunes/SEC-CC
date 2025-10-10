# Simplified NestJS Dockerfile for Docker deployment

FROM node:20-alpine

WORKDIR /usr/src/app

# Copy package files
COPY package.json package-lock.json* ./

# Install only production dependencies - simplified
RUN npm install --production --legacy-peer-deps --no-audit --no-fund

# Copy source code
COPY src ./src
COPY tsconfig.json tsconfig.build.json ./

# Build the application
RUN npm install -g @nestjs/cli typescript
RUN npx tsc

EXPOSE 3000

# Start the application
CMD ["node", "dist/main.js"]