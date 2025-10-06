# Frontend builder - Robust build process
FROM node:20-alpine AS builder

# Install additional debugging tools
RUN apk add --no-cache curl git

# Set working directory to project root
WORKDIR /app

# Copy package files first for better Docker layer caching
COPY package.json package-lock.json* ./

# Install dependencies with detailed logging and better error handling
RUN echo "📦 Installing dependencies in $(pwd)..." && \
    pwd && \
    ls -la && \
    npm ci --verbose --no-audit --no-fund && \
    echo "✅ Dependencies installed successfully"

# Copy source code
COPY . .

# Set build arguments as environment variables
ARG NODE_ENV=production
ARG VITE_API_URL=http://localhost:8000
ARG VITE_NESTJS_URL=http://localhost:3000
ARG VITE_FRONTEND_URL=http://localhost:5173

ENV NODE_ENV=${NODE_ENV}
ENV VITE_API_URL=${VITE_API_URL}
ENV VITE_NESTJS_URL=${VITE_NESTJS_URL}
ENV VITE_FRONTEND_URL=${VITE_FRONTEND_URL}

# Build the application with comprehensive debugging
RUN echo "🚀 Starting build process in $(pwd)..." && \
    echo "📊 Node version: $(node --version)" && \
    echo "📦 NPM version: $(npm --version)" && \
    echo "🔧 Environment: $NODE_ENV" && \
    echo "🌐 API URL: $VITE_API_URL" && \
    echo "🔗 NestJS URL: $VITE_NESTJS_URL" && \
    echo "🖥️ Frontend URL: $VITE_FRONTEND_URL" && \
    echo "📁 Current directory contents:" && \
    ls -la && \
    echo "" && \
    echo "🔍 Checking package.json scripts:" && \
    cat package.json | jq '.scripts' 2>/dev/null || cat package.json | grep -A 10 '"scripts"' && \
    echo "" && \
    echo "⚡ Running TypeScript check first..." && \
    npx tsc --noEmit --skipLibCheck && \
    echo "✅ TypeScript check completed" && \
    echo "" && \
    echo "⚡ Running build command..." && \
    npm run build && \
    echo "✅ Build completed successfully!" && \
    echo "📊 Build output:" && \
    ls -la dist 2>/dev/null && \
    echo "📁 Files in dist:" && \
    find dist -type f | wc -l | xargs echo "files found" 2>/dev/null || echo "No dist directory or no files"

# Production stage - serve with nginx
FROM nginx:alpine AS production

# Install curl for health checks
RUN apk add --no-cache curl

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY docker/frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Create nginx user and set permissions
RUN addgroup -g 1001 -S nginx && \
    adduser -S nginx -u 1001 && \
    chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chown -R nginx:nginx /etc/nginx/conf.d

# Switch to non-root user
USER nginx

# Add health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
