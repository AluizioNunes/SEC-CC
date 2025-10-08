# Multi-stage build: install deps and build, then serve with nginx for smaller runtime image
FROM node:20-alpine AS builder
WORKDIR /app

# Use root frontend package files (project uses package.json.frontend)
# Copy only frontend-specific files to keep build context small
COPY package.json.frontend ./package.json

# Install dependencies for build (use npm install so package-lock isn't required in context)
RUN npm install --legacy-peer-deps --silent

# Copy only frontend source and public assets
## Instead of building inside this context (which cannot include repo root),
## use prebuilt `dist/` (already present at repo root) and copy it into the nginx image.
FROM nginx:alpine AS runtime
WORKDIR /usr/share/nginx/html

# Copy prebuilt static assets from repository `dist/` into image
COPY /dist/ /usr/share/nginx/html/

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]