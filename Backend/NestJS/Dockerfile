# NestJS Dockerfile - Using Node 20 LTS
FROM node:20-alpine

WORKDIR /usr/src/app

# Install build deps
RUN apk add --no-cache python3 make g++ git

# Copy package files
COPY package.json ./

# Install ALL dependencies (including dev dependencies for build)
RUN npm install

# Copy source
COPY tsconfig.json ./
COPY src ./src

# Build application
RUN npm run build

EXPOSE 3000
CMD ["node", "dist/main.js"]
