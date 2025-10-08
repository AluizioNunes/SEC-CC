# Multi-stage build: install deps and build, then serve with nginx for smaller runtime image
FROM node:20-alpine AS builder
WORKDIR /app

# Use root frontend package files (project uses package.json.frontend)
# Copy only frontend-specific files to keep build context small
COPY package.json.frontend ./package.json
COPY package-lock.json ./package-lock.json

# Install dependencies for build
RUN npm ci --legacy-peer-deps --silent

# Copy only frontend source and public assets
COPY src ./src
COPY public ./public
COPY index.html ./
COPY vite.config.ts ./
COPY tsconfig.json ./
COPY tsconfig.app.json ./tsconfig.app.json
COPY tsconfig.node.json ./tsconfig.node.json

# Build (if package script exists)
RUN npm run build --if-present --silent

# Runtime image serving static files with nginx
FROM nginx:alpine AS runtime
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]