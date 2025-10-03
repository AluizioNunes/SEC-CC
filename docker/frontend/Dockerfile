# Frontend builder that outputs Vite build to /app/dist (shared via named volume)
FROM node:20-alpine

WORKDIR /app

# Install deps at runtime to ensure host changes are picked up; alternatively we can use multi-stage
COPY package.json package-lock.json* ./

# Install production and dev deps for build (using npm install to avoid cache issues)
RUN npm install

# Copy source
COPY . .

# Build on container start so dist is written to the mounted volume
CMD ["sh", "-c", "npm run build && tail -f /dev/null"]
