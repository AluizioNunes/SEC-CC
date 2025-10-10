# Multi-stage build: install deps and build, then serve with nginx for smaller runtime image
FROM node:20-alpine AS builder
WORKDIR /app

# Copy package files
COPY package.json package.json.frontend ./

# Install dependencies for build
RUN npm install --legacy-peer-deps --silent

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Runtime image
FROM nginx:alpine AS runtime
WORKDIR /usr/share/nginx/html

# Copy built static assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html/

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]