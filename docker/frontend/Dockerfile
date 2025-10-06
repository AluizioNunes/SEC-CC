# Frontend builder - Multi-stage build for production
FROM node:20-alpine AS builder

# Install additional debugging tools
RUN apk add --no-cache curl

WORKDIR /app

# Copy package files first for better Docker layer caching
COPY package.json package-lock.json* ./

# Install dependencies with detailed logging
RUN echo "📦 Installing dependencies..." && \
    npm install --verbose --no-audit --no-fund && \
    echo "✅ Dependencies installed successfully"

# Copy source code
COPY . .

# Build the application
RUN echo "🚀 Starting build process..." && \
    echo "📊 Node version: $(node --version)" && \
    echo "📦 NPM version: $(npm --version)" && \
    echo "🔨 Running TypeScript compilation..." && \
    npx tsc -b --verbose && \
    echo "✅ TypeScript compilation completed" && \
    echo "⚡ Running Vite build..." && \
    npm run build && \
    echo "✅ Build completed successfully!" && \
    echo "📊 Build output:" && \
    ls -la dist

# Production stage - serve with nginx
FROM nginx:alpine AS production

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY docker/frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Add health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
