# Frontend builder - Optimized build process
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files first for better layer caching
COPY package*.json ./

# Install dependencies
RUN npm ci --prefer-offline --no-audit --no-fund

# Copy only necessary source files
COPY src ./src
COPY index.html .
COPY tsconfig*.json ./
COPY vite.config.ts ./
COPY public ./public

# Set build arguments as environment variables
ARG NODE_ENV=production
ARG VITE_API_URL=http://localhost:8000
ARG VITE_NESTJS_URL=http://localhost:3000
ARG VITE_FRONTEND_URL=http://localhost:5173

ENV NODE_ENV=${NODE_ENV}
ENV VITE_API_URL=${VITE_API_URL}
ENV VITE_NESTJS_URL=${VITE_NESTJS_URL}
ENV VITE_FRONTEND_URL=${VITE_FRONTEND_URL}

# Build the application with timeout protection
RUN timeout 300 npm run build

# Production stage - serve with nginx
FROM nginx:alpine AS production

# Install curl for health checks
RUN apk add --no-cache curl

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY docker/frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Set proper permissions (simplified to avoid hanging)
RUN chown -R nginx:nginx /usr/share/nginx/html

# Switch to non-root user
USER nginx

# Add health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]